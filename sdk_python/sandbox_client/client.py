import os
import json
import socket

import paramiko
import requests
from typing import Tuple, Dict, Any, Optional, IO, List

class SandboxClient:
    """Pico API Server client class that encapsulates session management, SSH connections, 
    and file transfer functionalities"""
    
    DEFAULT_API_URL = "http://localhost:8080"
    DEFAULT_TTL = 3600
    DEFAULT_USER = "sandbox"
    DEFAULT_IMAGE = "sandbox:latest"
    
    def __init__(self, api_url: Optional[str] = None):
        """Initialize the client
        
        Args:
            api_url: Pico API server address. Defaults to environment variable API_URL 
                     or DEFAULT_API_URL if not provided
        """
        self.api_url = api_url or self.get_env("API_URL", self.DEFAULT_API_URL)
        self.session_id: Optional[str] = None
        self.ssh_client: Optional[paramiko.SSHClient] = None
        self.tunnel_sock: Optional[socket.socket] = None
        self.private_key: Optional[paramiko.RSAKey] = None
        
    def __del__(self):
        """Destructor that automatically cleans up resources"""
        self.cleanup()
    
    @staticmethod
    def get_env(key: str, default: str) -> str:
        """Get environment variable with fallback to default value
        
        Args:
            key: Environment variable name
            default: Value to return if variable doesn't exist
            
        Returns:
            Environment variable value or default
        """
        return os.getenv(key, default)
    
    def generate_ssh_key_pair(self) -> Tuple[str, paramiko.RSAKey]:
        """Generate an RSA SSH key pair
        
        Returns:
            Tuple containing public key string and private key object
        """

        private_key = paramiko.RSAKey.generate(2048)
        self.private_key = private_key
        public_key = f"{private_key.get_name()} {private_key.get_base64()}"
        return public_key, private_key
    
    def create_sandbox_with_ssh_key(
        self,
        ttl: int = DEFAULT_TTL,
        image: str = DEFAULT_IMAGE,
        ssh_public_key: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new session on the Pico server
        
        Args:
            ttl: Session timeout in seconds
            image: Container image to use
            ssh_public_key: SSH public key for authentication
            metadata: Optional session metadata
            
        Returns:
            Created session ID
        """
        req_data = {
            "ttl": ttl,
            "image": image,
            "sshPublicKey": ssh_public_key,
            "metadata": metadata or {}
        }
        
        url = f"{self.api_url}/v1/sessions"
        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(req_data)
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to create session: {response.status_code} - {response.text}")
        
        session_data = response.json()
        self.session_id = session_data.get("sessionId")
        return self.session_id
    
    def create_sandbox(
        self,
        ttl: int = DEFAULT_TTL,
        image: str = DEFAULT_IMAGE,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate an SSH key pair and create a session with it
        
        Args:
            ttl: Session timeout in seconds
            image: Container image to use
            metadata: Optional session metadata
            
        Returns:
            Created session ID
        """
        public_key, _ = self.generate_ssh_key_pair()
        return self.create_sandbox_with_ssh_key(
            ttl=ttl,
            image=image,
            ssh_public_key=public_key,
            metadata=metadata or {"test": "ssh-key-auth"}
        )
    
    def get_sandbox(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session details by ID"""
        try:
            url = f"{self.api_url}/v1/sessions/{session_id}"
            response = requests.get(
                url,
                headers={"Content-Type": "application/json"}
            )
            print(url)
            print(response)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Session query failed: {str(e)}")
    
    def get_sandboxs(self) -> List[Dict[str, Any]]:
        """List all sessions"""
        try:
            url = f"{self.api_url}/v1/sessions"
            response = requests.get(
                url,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json().get("sessions", [])
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Session listing failed: {str(e)}")
            return []
    
    def delete_sandbox(self, session_id: str) -> bool:
        """Delete a session and clean up cached SSH key"""
        try:
            url = f"{self.api_url}/v1/sessions/{session_id}"
            response = requests.delete(
                url,
                timeout=30
            )
            if response.status_code == 404:
                return False
            response.raise_for_status()
            
            return True
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Session deletion failed: {str(e)}")

    
    def establish_tunnel(self, session_id: Optional[str] = None) -> socket.socket:
        """Establish an HTTP CONNECT tunnel to the session
        
        Args:
            session_id: Session ID to connect to (uses current session if not provided)
            
        Returns:
            Established tunnel socket connection
        """
        session_id = session_id or self.session_id
        if not session_id:
            raise Exception("No session ID specified. Please create a session first.")
        
        # Parse API address
        if self.api_url.startswith("http://"):
            host_part = self.api_url[7:]
        else:
            host_part = self.api_url
        
        # Handle port number
        if ":" in host_part:
            host, port_str = host_part.split(":", 1)
            port = int(port_str)
        else:
            host = host_part
            port = 8080
        
        # Establish TCP connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10.0)
        sock.connect((host, port))
        
        # Send CONNECT request
        connect_path = f"/v1/sessions/{session_id}/tunnel"
        request = (
            f"CONNECT {connect_path} HTTP/1.1\r\n"
            f"Host: {host}:{port}\r\n"
            "User-Agent: pico-client/1.0 (python)\r\n"
            "\r\n"
        )
        sock.sendall(request.encode())
        
        # Verify response
        response = sock.recv(4096).decode()
        if not response.startswith("HTTP/1.1 200"):
            sock.close()
            raise Exception(f"Tunnel establishment failed: {response}")
        
        self.tunnel_sock = sock
        return sock
    
    def connect_ssh(self) -> paramiko.SSHClient:
        """Establish an SSH connection over the provided tunnel using the given private key
        
        Args:
            conn: Established tunnel socket connection
            private_key: RSA private key for authentication
            
        Returns:
            Established SSH client connection
        """
        conn = self.tunnel_sock or self.establish_tunnel()

        ssh_client = paramiko.SSHClient()
        
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh_client.connect(
                hostname="sandbox",  
                username="sandbox",  
                pkey=self.private_key,
                sock=conn,
                timeout=10.0,        
                banner_timeout=10.0
            )
            self.ssh_client = ssh_client
            return ssh_client
        except paramiko.SSHException as e:
            raise paramiko.SSHException(f"SSH handshake failed: {str(e)}") from e
        
    def execute_command(self, command: str, ssh_client: Optional[paramiko.SSHClient] = None) -> str:
        """Execute a command over SSH
        
        Args:
            command: Command to execute
            ssh_client: SSH client instance (uses current connection if not provided)
            
        Returns:
            Command output
        """
        ssh_client = self.ssh_client or self.connect_ssh()
        if not ssh_client:
            raise Exception("No SSH connection established. Please call connect_ssh first.")
        
        stdin, stdout, stderr = ssh_client.exec_command(command)
        exit_status = stdout.channel.recv_exit_status()
        
        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()
        
        if exit_status != 0:
            raise Exception(f"Command execution failed (exit code {exit_status}): {error}")
        
        return output
    
    def execute_commands(self, commands: List[str]) -> Dict[str, str]:
        """Execute multiple commands over SSH
        
        Args:
            commands: List of commands to execute
            
        Returns:
            Dictionary mapping commands to their outputs
        """
        results = {}
        for cmd in commands:
            results[cmd] = self.execute_command(cmd)
        return results
    
    def upload_file(
        self,
        content: str,
        remote_path: str,
    ) -> None:
        """Upload file content to remote server via SFTP
        
        Args:
            content: Content to write to remote file
            remote_path: Path on remote server to upload to
            ssh_client: SSH client instance (uses current connection if not provided)
        """
        ssh_client = self.ssh_client or self.connect_ssh
        if not ssh_client:
            raise Exception("No SSH connection established. Please call connect_ssh first.")
        
        sftp = ssh_client.open_sftp()
        try:
            # Create remote directory if needed
            remote_dir = os.path.dirname(remote_path)
            self._sftp_mkdir_p(sftp, remote_dir)
            
            # Write file content
            with sftp.file(remote_path, 'w') as remote_file:
                remote_file.write(content)
        finally:
            sftp.close()
    
    def download_file(
        self,
        remote_path: str,
        local_path: str,
    ) -> None:
        """Download a file from remote server via SFTP
        
        Args:
            remote_path: Path on remote server to download from
            local_path: Local path to save the downloaded file
            ssh_client: SSH client instance (uses current connection if not provided)
        """
        ssh_client =  self.ssh_client
        if not ssh_client:
            raise Exception("No SSH connection established. Please call connect_ssh first.")
        
        sftp = ssh_client.open_sftp()
        try:
            # Ensure local directory exists
            local_dir = os.path.dirname(local_path)
            os.makedirs(local_dir, exist_ok=True)
            
            # Download file
            sftp.get(remote_path, local_path)
        finally:
            sftp.close()
    
    def cleanup(self) -> None:
        """Clean up all resources (SSH connections and tunnels)"""
        if self.ssh_client:
            self.ssh_client.close()
            self.ssh_client = None
        if self.tunnel_sock:
            self.tunnel_sock.close()
            self.tunnel_sock = None
    
    @staticmethod
    def _sftp_mkdir_p(sftp: paramiko.SFTPClient, remote_dir: str) -> None:
        """Recursively create remote directories (similar to mkdir -p)
        
        Args:
            sftp: SFTP client instance
            remote_dir: Remote directory path to create
        """
        dirs = remote_dir.split('/')
        current_dir = ''
        
        for dir in dirs:
            if not dir:
                current_dir += '/'
                continue
                
            current_dir = os.path.join(current_dir, dir)
            try:
                sftp.stat(current_dir)
            except FileNotFoundError:
                sftp.mkdir(current_dir)