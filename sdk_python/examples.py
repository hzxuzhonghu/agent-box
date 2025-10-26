from sandbox import SandboxSDK
from models.sandbox_info import PodState
from services import exceptions

def main():
    # Initialize SandboxSDK with default Pico service URL (http://127.0.0.1:8080)
    # Custom URL can be specified like: SandboxSDK(pico_base_url="http://custom-url:port")
    sdk = SandboxSDK()

    try:
        print("1. Create a new sandbox with custom configuration")
        # Configuration can include 'image' (container image) and 'ttl' (time-to-live in seconds)
        sandbox_config = {
            "image": "sandbox:latest",  # Custom image (default uses PicoClient.DEFAULT_IMAGE)
            "ttl": 3600  # Sandbox will auto-expire after 1 hour (3600 seconds)
        }
        sandbox = sdk.create_sandbox(config=sandbox_config)
        print(f"Created sandbox with ID: {sandbox.id}")
        print(f"Initial status: {sandbox.status}")
        print(f"Created at: {sandbox.created_at}")
        print(f"Expires at: {sandbox.expires_at}")

        print("2. Refresh sandbox status to get latest state")
        sandbox.refresh_status()
        print(f"Refreshed status: {sandbox.status}")

        print("3. Check if sandbox is in running state")
        if sandbox.is_running():
            print("Sandbox is currently running")
            
            print("4. Execute command in the running sandbox")
            try:
                cmd = "uname -a"
                #result = sandbox.execute_command(command=cmd)
                result = sandbox.execute_command(command=cmd)
                print("\nCommand execution result:")
                print(f"STDOUT: {result.strip()}")
            except exceptions.SandboxNotReadyError as e:
                print(f"Command execution failed: {str(e)}")

            print("5. Upload local file to sandbox")
            try:
                local_file = "./local_test.txt"
                remote_file = "/tmp/remote_test.txt"
                sandbox.upload_file(local_path=local_file, remote_path=remote_file)
                print(f"\nFile upload result: Success")
            except exceptions.SandboxNotReadyError as e:
                print(f"File upload failed: {str(e)}")

            print("6. Download file from sandbox to local")
            try:
                remote_download = "/etc/os-release"  # Example file to download
                local_download = "./downloaded_os-release.txt"
                sandbox.download_file(remote_path=remote_download, local_path=local_download)
                print(f"\nSuccessfully downloaded {remote_download} to {local_download}")
            except exceptions.SandboxNotReadyError as e:
                print(f"File download failed: {str(e)}")

        print("7. Get sandbox by ID (demonstrates retrieval of existing sandboxes)")
        retrieved_sandbox = sdk.get_sandbox(sandbox_id=sandbox.id)
        if retrieved_sandbox:
            print(f"\nRetrieved sandbox ID: {retrieved_sandbox.id}")
            print(f"Retrieved sandbox status: {retrieved_sandbox.status}")
        else:
            print(f"\nFailed to retrieve sandbox with ID: {sandbox.id}")

        print("8. Get all active sandboxes")
        active_sandboxes = sdk.get_sandboxes()
        print(f"\nNumber of active sandboxes: {len(active_sandboxes)}")
        for sb_id, sb in active_sandboxes.items():
            print(f"Active sandbox: {sb_id} (Status: {sb.status})")

        print("9. Stop/delete the sandbox through instance method")
        stop_result = sandbox.stop()
        print(f"\nSandbox stop via instance method: {'Success' if stop_result else 'Failed'}")

    except Exception as e:
        print(f"\nAn error occurred during operation: {str(e)}")

if __name__ == "__main__":
    main()