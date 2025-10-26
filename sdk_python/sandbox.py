import threading
from contextlib import AbstractContextManager
from typing import Optional, Dict, Any
from models.sandbox_info import SandboxInstance
from sandbox_client.client import SandboxClient
from services.log import get_logger

class SandboxSDK(AbstractContextManager):
    def __init__(self, pico_base_url: str = "http://127.0.0.1:8080"):
        self.logger = get_logger(f"{__name__}.SandboxSDK")
        self._client = SandboxClient(api_url=pico_base_url)  
        self._active_sandboxes: Dict[str, SandboxInstance] = {}
        self._lock = threading.RLock()

    def create_sandbox(self, config: Optional[Dict[str, Any]] = None) -> SandboxInstance:
        config = config or {}
        image = config.get("image", SandboxClient.DEFAULT_IMAGE)
        ttl = int(config.get("ttl", SandboxClient.DEFAULT_TTL))

        session_id = self._client.create_sandbox(ttl=ttl, image=image)
        session_info = self._client.get_sandbox(session_id)
        
        sandbox = SandboxInstance(
            sandbox_id=session_id,
            client=self._client,
            status=session_info["status"],
            created_at=session_info.get("createdAt"),
            expires_at=session_info.get("expiresAt")
        )

        with self._lock:
            self._active_sandboxes[sandbox.id] = sandbox

        self.logger.info(f"Sandbox {sandbox.id} created")
        return sandbox

    def get_sandbox(self, sandbox_id: str) -> Optional[SandboxInstance]:
        with self._lock:
            if sandbox_id in self._active_sandboxes:
                return self._active_sandboxes[sandbox_id]
            
            session_info = self._client.get_sandbox(sandbox_id)
            if not session_info:
                return None
            
            return SandboxInstance(
                sandbox_id=sandbox_id,
                client=self._client,
                status=session_info["status"],
                created_at=session_info.get("createdAt"),
                expires_at=session_info.get("expiresAt")
            )
    
    def get_sandboxes(self) -> Dict[str, SandboxInstance]:
        with self._lock:
            return dict(self._active_sandboxes)

    def delete_sandbox(self, sandbox_id: str) -> bool:
        with self._lock:
            if sandbox_id in self._active_sandboxes:
                del self._active_sandboxes[sandbox_id]
            return self._client.delete_sandbox(sandbox_id)

    def __exit__(self, exc_type, exc_val, exc_tb):
        with self._lock:
            for sandbox in self._active_sandboxes.values():
                sandbox.stop()
        return False