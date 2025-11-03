#!/usr/bin/env python3
"""
Browser Sandbox Client - Interact with browser-use sandbox using Playwright

This script demonstrates how to:
1. Run a browser sandbox locally using Docker
2. Execute Playwright browser automation scripts inside the sandbox
3. Retrieve results (screenshots, page content, etc.)

Usage:
    python browser_client.py --url https://example.com --output screenshot.png
"""

import os
import sys
import argparse
import tempfile
from typing import Optional, Dict, Any


class BrowserSandboxClient:
    """Client for interacting with browser sandbox environments via Docker"""
    
    def __init__(self):
        """Initialize the browser sandbox client"""
        pass
        
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    
    def execute_playwright_script(self, script: str, output_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a Playwright Python script in the Docker sandbox
        
        Args:
            script: Python script content using Playwright
            output_file: Optional path to save screenshot or output file
            
        Returns:
            Dictionary with execution results (stdout, stderr, exit_code)
        """
        return self._execute_local(script, output_file)
    
    def _execute_local(self, script: str, output_file: Optional[str] = None) -> Dict[str, Any]:
        """Execute script locally using Docker"""
        import subprocess
        
        # Create temporary script file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(script)
            script_path = f.name
        
        # Make script readable by all users (for Docker container)
        os.chmod(script_path, 0o644)
        print(f"✓ Temporary script created at {script_path}")
        
        # Create temporary directory for output
        output_dir = tempfile.mkdtemp()
        os.chmod(output_dir, 0o777)
        
        try:
            # Run docker command with script passed via stdin or volume
            # We'll use a bash command to copy the script content and execute it
            # This avoids permission issues with mounted files
            # Add --network=host to share host network and avoid network issues
            cmd = [
                "docker", "run", "--rm",
                "--network=host",
                "-v", f"{output_dir}:/tmp/output",
                "browser-use:latest",
                "bash", "-c",
                f"cat > /tmp/script.py << 'EOF'\n{script}\nEOF\npython3 /tmp/script.py"
            ]
            
            print(f"Executing in Docker container...")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            # Check if output file was created
            container_output = os.path.join(output_dir, "output.png")
            if output_file and os.path.exists(container_output):
                import shutil
                shutil.copy2(container_output, output_file)
                print(f"✓ Screenshot saved to {output_file}")
            
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode,
                "success": result.returncode == 0
            }
        
        finally:
            os.unlink(script_path)
            # Clean up output directory
            import shutil
            if os.path.exists(output_dir):
                shutil.rmtree(output_dir)


def create_example_script(url: str = "https://example.com") -> str:
    """Create an example Playwright script"""
    return f"""
from playwright.sync_api import sync_playwright
import sys
import os

def main():
    with sync_playwright() as p:
        # Launch browser in headless mode
        browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
        context = browser.new_context(
            viewport={{"width": 1280, "height": 720}},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        )
        page = context.new_page()
        
        try:
            print(f"Navigating to {url}...")
            page.goto("{url}", wait_until="networkidle", timeout=30000)
            
            # Get page title
            title = page.title()
            print(f"Page title: {{title}}")
            
            # Get page content
            content = page.content()
            print(f"Page content length: {{len(content)}} characters")
            
            # Take screenshot - save to /tmp/output if mounted, otherwise /tmp
            if os.path.exists("/tmp/output"):
                screenshot_path = "/tmp/output/output.png"
            else:
                screenshot_path = "/tmp/output.png"
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"Screenshot saved to {{screenshot_path}}")
            
            # Extract some text content
            body_text = page.inner_text("body")
            print(f"Body text preview: {{body_text[:200]}}...")
            
            print("\\n✓ Browser automation completed successfully!")
            
        except Exception as e:
            print(f"Error: {{e}}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            sys.exit(1)
        finally:
            browser.close()

if __name__ == "__main__":
    main()
"""


def main():
    parser = argparse.ArgumentParser(description="Browser Sandbox Client - Local Docker Mode")
    parser.add_argument(
        "--url",
        default="https://example.com",
        help="URL to visit with the browser"
    )
    parser.add_argument(
        "--output",
        default="screenshot.png",
        help="Output file path for screenshot"
    )
    parser.add_argument(
        "--script",
        help="Path to custom Playwright script file"
    )
    
    args = parser.parse_args()
    
    # Load or create script
    if args.script:
        with open(args.script, 'r') as f:
            script = f.read()
        print(f"Using custom script from {args.script}")
    else:
        script = create_example_script(args.url)
        print(f"Using example script to visit {args.url}")
    
    # Execute
    try:
        with BrowserSandboxClient() as client:
            result = client.execute_playwright_script(script, output_file=args.output)
            
            print("\n" + "="*60)
            print("EXECUTION RESULTS")
            print("="*60)
            print(f"Exit Code: {result['exit_code']}")
            print(f"Success: {result['success']}")
            print("\nStdout:")
            print(result['stdout'])
            if result['stderr']:
                print("\nStderr:")
                print(result['stderr'])
            print("="*60)
            
            if result['success']:
                print("\n✓ Browser automation completed successfully!")
                if os.path.exists(args.output):
                    print(f"✓ Screenshot saved to: {args.output}")
            else:
                print("\n✗ Browser automation failed!")
                sys.exit(1)
                
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
