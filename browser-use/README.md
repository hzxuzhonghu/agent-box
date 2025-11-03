# Browser-use Sandbox

A Docker-based sandbox environment for browser automation using Playwright.

## Overview

This sandbox provides an isolated environment for running browser automation scripts using Playwright. It includes:
- Python 3.11
- Playwright with Chromium, Firefox, and WebKit browsers
- SSH access for remote script execution
- Compatibility with the Sandbox API

## Quick Start

### 1. Build the Docker Image

```bash
cd browser-use
docker build -t browser-use:latest .
```

### 2. Run Locally

#### Option A: Direct Docker Execution

```bash
# Run a container
docker run -d --name browser-sandbox -p 2222:22 browser-use:latest

# Execute a script inside
docker exec browser-sandbox python3 /path/to/your_script.py
```

#### Option B: Using the Python Client (Local Mode)

```bash
# Install dependencies
pip install playwright

# Run the client script
python browser_client.py --mode local --url https://example.com
```

### 3. Use with Sandbox API

```bash
# Set environment variables
export SANDBOX_API_URL=http://localhost:8080/v1
export SANDBOX_API_TOKEN=your-bearer-token

# Run the client script
python browser_client.py --mode api --url https://example.com --output screenshot.png
```

## Docker Image Details

### Base Image
- `python:3.11-slim-bookworm`

### Installed Browsers
- Chromium (via Playwright)
- Firefox (via Playwright)
- WebKit (via Playwright)

### System User
- Username: `sandbox`
- Password: `sandbox`
- Home: `/home/sandbox`
- Sudo: enabled (no password required)

### Exposed Ports
- `22` - SSH (for Sandbox API compatibility)

## Browser Client Usage

### Basic Usage

```python
from browser_client import BrowserSandboxClient

# Local mode
with BrowserSandboxClient(mode="local") as client:
    script = """
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://example.com")
    print(page.title())
    browser.close()
"""
    result = client.execute_playwright_script(script)
    print(result['stdout'])
```

### API Mode

```python
from browser_client import BrowserSandboxClient

# API mode
with BrowserSandboxClient(
    mode="api",
    api_url="http://localhost:8080/v1",
    api_token="your-token"
) as client:
    script = """
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
    page = browser.new_page()
    page.goto("https://github.com")
    page.screenshot(path="/tmp/output.png")
    browser.close()
"""
    result = client.execute_playwright_script(script, output_file="github.png")
    print(f"Screenshot saved: {result.get('output_file')}")
```

### Command Line

```bash
# Visit a URL and take screenshot (local mode)
python browser_client.py --mode local --url https://github.com --output github.png

# Use custom script
python browser_client.py --mode local --script my_script.py

# API mode
python browser_client.py --mode api --url https://example.com
```

## Example Playwright Scripts

### Example 1: Simple Page Visit

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
    page = browser.new_page()
    page.goto("https://example.com")
    
    # Get title
    print(f"Title: {page.title()}")
    
    # Take screenshot
    page.screenshot(path="/tmp/output.png")
    
    browser.close()
```

### Example 2: Form Interaction

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
    page = browser.new_page()
    page.goto("https://www.google.com")
    
    # Search
    page.fill('textarea[name="q"]', 'Playwright Python')
    page.press('textarea[name="q"]', 'Enter')
    page.wait_for_load_state('networkidle')
    
    # Get results
    print(f"Search results page: {page.title()}")
    
    browser.close()
```

### Example 3: Multiple Pages

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
    context = browser.new_context()
    
    # Open multiple pages
    urls = ["https://example.com", "https://example.org", "https://example.net"]
    for url in urls:
        page = context.new_page()
        page.goto(url)
        print(f"{url}: {page.title()}")
    
    browser.close()
```

### Example 4: Data Extraction

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
    page = browser.new_page()
    page.goto("https://news.ycombinator.com")
    
    # Extract article titles
    titles = page.locator('.titleline > a').all_text_contents()
    for i, title in enumerate(titles[:10], 1):
        print(f"{i}. {title}")
    
    browser.close()
```

## Docker Management

### Build
```bash
docker build -t browser-use:latest .
```

### Run
```bash
# Run detached
docker run -d --name browser-sandbox browser-use:latest

# Run with port mapping (for SSH)
docker run -d --name browser-sandbox -p 2222:22 browser-use:latest

# Run with volume mount
docker run -d --name browser-sandbox -v $(pwd)/scripts:/workspace browser-use:latest
```

### Execute Commands
```bash
# Run a Python script
docker exec browser-sandbox python3 /workspace/script.py

# Interactive shell
docker exec -it browser-sandbox bash

# As sandbox user
docker exec -it -u sandbox browser-sandbox bash
```

### Stop and Remove
```bash
docker stop browser-sandbox
docker rm browser-sandbox
```

## Troubleshooting

### Browser Launch Issues

If you encounter browser launch errors, make sure to use these arguments:

```python
browser = p.chromium.launch(
    headless=True,
    args=[
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-setuid-sandbox'
    ]
)
```

### Memory Issues

For heavy browser workloads, increase Docker memory:

```bash
docker run -d --memory=2g --name browser-sandbox browser-use:latest
```

### Display Issues

The container runs in headless mode. If you need a display (for debugging):

```bash
# Install Xvfb in the container
docker exec browser-sandbox sudo apt-get update
docker exec browser-sandbox sudo apt-get install -y xvfb

# Run with virtual display
docker exec browser-sandbox sh -c "Xvfb :99 -screen 0 1280x720x24 &"
```

## Security Considerations

- The sandbox user has sudo access without password (for convenience in isolated environments)
- Default SSH password is `sandbox:sandbox` - change this for production use
- Consider using SSH key-based authentication instead of passwords
- Run containers with resource limits to prevent abuse
- Use network isolation for untrusted code execution

## Integration with Sandbox API

This Docker image is designed to work with the Sandbox API defined in `../api-spec/sandbox-api-spec.yaml`.

### Creating a Sandbox

```python
from sandbox_sessions_sdk import SandboxClient

client = SandboxClient(
    api_url="http://localhost:8080/v1",
    bearer_token="your-token"
)

sandbox = client.create_sandbox(
    ttl=1800,
    image="browser-use:latest",
    metadata={"type": "browser-automation"}
)
```

### SSH Access via HTTP CONNECT

```python
from sandbox_sessions_sdk import SandboxSSHClient

with SandboxSSHClient(
    api_url="http://localhost:8080/v1",
    bearer_token="your-token",
    sandbox_id=sandbox.sandbox_id,
    username="sandbox",
    password="sandbox"
) as ssh:
    # Upload script
    ssh.upload_file("local_script.py", "remote_script.py")
    
    # Execute
    result = ssh.run_command("python3 remote_script.py")
    print(result['stdout'])
    
    # Download results
    ssh.download_file("output.png", "local_output.png")
```

## Dependencies

### Python
- playwright
- playwright-stealth (optional, for stealth mode)
- requests (for API integration)
- Pillow (for image processing)

### System
- Chromium, Firefox, WebKit browsers (via Playwright)
- SSH server (openssh-server)
- Various system libraries for browser rendering

## License

This sandbox configuration is part of the agent-box project.

## Support

For issues or questions:
- Check the main project documentation
- Review Playwright documentation: https://playwright.dev/python/
- Check Docker logs: `docker logs browser-sandbox`
