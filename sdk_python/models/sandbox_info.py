from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional

class PodState(Enum):
    """Immutable state enum with transition validation"""
    RUNNING = "Running"
    PENDING = "Pending"
    FAILED = "Failed"
    UNKNOWN = "Unknown"

@dataclass
class ExecutionResult:
    """Data model for command execution results"""
    stdout: str
    stderr: str
    exit_code: int
    execution_time: float = 0.0  # Duration in seconds

from typing import Optional, Dict, Any
from models.sandbox_info import PodState
from sandbox_client.client import SandboxClient
from services import exceptions

class SandboxInstance:
    def __init__(
        self,
        sandbox_id: str,
        client: SandboxClient,
        status: str,
        created_at: Optional[str] = None,
        expires_at: Optional[str] = None
    ):
        self.id = sandbox_id
        self._client = client
        self.status = status
        self.created_at = created_at
        self.expires_at = expires_at

    def is_running(self) -> bool:
        return self.status == PodState.RUNNING.value

    def execute_command(self, command: str) -> Dict[str, Any]:
        if not self.is_running():
            raise exceptions.SandboxNotReadyError(
                f"Sandbox {self.id} is not running (status: {self.status})"
            )
        return self._client.execute_command(command)

    def upload_file(self, local_path: str, remote_path: str) -> Dict[str, Any]:
        if not self.is_running():
            raise exceptions.SandboxNotReadyError(f"Sandbox {self.id} is not running")
        return self._client.upload_file(local_path, remote_path)

    def download_file(self, remote_path: str, local_path: str) -> None:
        if not self.is_running():
            raise exceptions.SandboxNotReadyError(f"Sandbox {self.id} is not running")
        self._client.download_file(remote_path, local_path)

    def stop(self) -> bool:
        return self._client.delete_sandbox(self.id)

    def refresh_status(self) -> None:
        session_info = self._client.get_sandbox(self.id)
        if session_info:
            self.status = session_info["status"]
            self.expires_at = session_info.get("expiresAt")