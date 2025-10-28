import logging
import json

# Import the PicoClient from the pico package
from client import SandboxClient

def main():
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    log = logging.getLogger(__name__)
    
    try:
        # Initialize Pico client
        client = SandboxClient()
        
        log.info("===========================================")
        log.info("SSH Key-based Authentication Test")
        log.info("===========================================\n")
        
        # 1. Create session with SSH key
        log.info("Step 1: Creating session with SSH key...")
        session_id = client.create_sandbox()
        log.info(f"✅ Session created: {session_id}\n")
        
        # 2. Establish tunnel
        log.info("Step 2: Establishing HTTP tunnel...")
        client.establish_tunnel()
        log.info("✅ Tunnel established\n")
        
        # 3. Establish SSH connection
        log.info("Step 3: Connecting via SSH...")
        client.connect_ssh()
        log.info("✅ SSH connection established\n")

        # 4. get session info
        log.info("Step 4: Retrieving session info...")
        session_info = client.get_sandbox(session_id)
        log.info(f"   Session Info: {json.dumps(session_info, indent=2)}\n")
        
        # 5. get session list
        log.info("Step 5: Retrieving session list...")
        session_list = client.get_sandboxs()
        log.info(f"   Session List: {json.dumps(session_list, indent=2)}\n")

        # 6. Execute test commands
        log.info("Step 6: Executing test commands...")
        commands = [
            "whoami",
            "pwd",
            "echo 'Hello from PicoClient!'",
            "python --version",
            "uname -a"
        ]
        
        for i, cmd in enumerate(commands, 1):
            log.info(f"   [{i}/{len(commands)}] Executing: {cmd}")
            output = client.execute_command(cmd)
            log.info(f"      Output: {output.strip()}\n")
        
        # 7. Upload Python script
        log.info("Step 7: Uploading Python script...")
        script_content = """#!/usr/bin/env python3
import json
from datetime import datetime

def generate_fibonacci(n):
    fib = [0, 1]
    for i in range(2, n):
        fib.append(fib[i-1] + fib[i-2])
    return fib[:n]

n = 20
fib = generate_fibonacci(n)
with open('/workspace/output.json', 'w') as f:
    json.dump({
        "timestamp": datetime.now().isoformat(),
        "count": n,
        "numbers": fib,
        "sum": sum(fib)
    }, f, indent=2)
print(f"Generated {n} Fibonacci numbers")
"""
        client.upload_file(script_content, "/workspace/fib.py")
        log.info("✅ Script uploaded to /workspace/fib.py\n")
        
        # 8. Execute script
        log.info("Step 8: Executing Python script...")
        output = client.execute_command("python3 /workspace/fib.py")
        log.info(f"   Output: {output.strip()}\n")
        
        # 9. Download result file
        log.info("Step 9: Downloading output file...")
        local_path = "/tmp/pico_output.json"
        client.download_file("/workspace/output.json", local_path)
        log.info(f"✅ File downloaded to {local_path}\n")
        
        # 10. Verify result
        log.info("Step 10: Verifying output...")
        with open(local_path, 'r') as f:
            data = json.load(f)
        log.info(f"   Generated {data['count']} numbers, sum: {data['sum']}")
        
        log.info("\n===========================================")
        log.info("🎉 All operations completed successfully")
        log.info("===========================================")

        # 11. Delete session
        log.info("\nStep 11: Deleting session...")
        if client.delete_sandbox(session_id):
            log.info(f"✅ Session {session_id} deleted\n")
        else:
            log.error(f"❌ Failed to delete session {session_id}\n")
        
        
    except Exception as e:
        log.error(f"\n❌ Error: {str(e)}")
    finally:
        if 'client' in locals():
            client.cleanup()

if __name__ == "__main__":
    main()