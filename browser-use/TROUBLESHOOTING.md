# Troubleshooting Guide

## Issues Fixed

### Issue 1: Permission Denied When Mounting Script File

**Symptom:**
```
python3: can't open file '/tmp/script.py': [Errno 13] Permission denied
```

**Root Cause:**
When mounting files from the host into a Docker container running as a non-root user (sandbox), permission mismatches can occur.

**Solution:**
Instead of mounting the script file directly, we pass the script content through a bash command:

```bash
docker run --rm browser-use:latest bash -c "
cat > /tmp/script.py << 'EOF'
<script content>
EOF
python3 /tmp/script.py
"
```

This creates the file inside the container with the correct ownership.

### Issue 2: Playwright Browsers Not Found

**Symptom:**
```
playwright._impl._errors.Error: BrowserType.launch: Executable doesn't exist at /ms-playwright/chromium...
╔════════════════════════════════════════════════════════════╗
║ Looks like Playwright was just installed or updated.       ║
║ Please run the following command to download new browsers: ║
```

**Root Cause:**
Playwright browsers were installed as root in `/root/.cache/ms-playwright`, but the container runs as the `sandbox` user who can't access that directory.

**Solution:**
1. Install Playwright browsers as root
2. Copy browsers to a shared location (`/ms-playwright`)
3. Make the directory accessible to all users (chmod 755)
4. Set `PLAYWRIGHT_BROWSERS_PATH=/ms-playwright` environment variable

```dockerfile
RUN playwright install chromium && \
    mkdir -p /ms-playwright && \
    cp -r /root/.cache/ms-playwright/* /ms-playwright/ && \
    chmod -R 755 /ms-playwright

ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
```

### Issue 3: Network Connection Errors

**Symptom:**
```
playwright._impl._errors.Error: Page.goto: net::ERR_NETWORK_CHANGED at https://example.com/
```

**Root Cause:**
Docker's default bridge network can sometimes cause network issues with browser automation.

**Solution:**
Use `--network=host` flag to share the host's network stack:

```bash
docker run --rm --network=host browser-use:latest python3 script.py
```

This gives the container direct access to the host's network interfaces.

## Verification

Test the setup with:

```bash
# Test script
bash test_docker.sh

# Test Python client
python3 browser_client.py --mode local --url https://example.com --output screenshot.png
```

## Common Issues

### Issue: Browser Crashes

**Solution:**
Add these flags when launching the browser:

```python
browser = p.chromium.launch(
    headless=True,
    args=[
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-setuid-sandbox',
        '--disable-gpu'
    ]
)
```

### Issue: Out of Memory

**Solution:**
Increase Docker memory limit:

```bash
docker run --rm --memory=2g browser-use:latest python3 script.py
```

### Issue: Slow Performance

**Solution:**
Allocate more CPU resources:

```bash
docker run --rm --cpus=2 browser-use:latest python3 script.py
```

### Issue: Can't Access Certain Websites

**Solution:**
Some websites may block automation. Try:
1. Use a different user agent
2. Enable stealth mode with `playwright-stealth`
3. Add delays between actions
4. Use `wait_until="domcontentloaded"` instead of `"networkidle"`

## Best Practices

1. **Always use headless mode in containers**
   ```python
   browser = p.chromium.launch(headless=True)
   ```

2. **Set appropriate timeouts**
   ```python
   page.goto(url, timeout=30000)  # 30 seconds
   ```

3. **Handle errors gracefully**
   ```python
   try:
       page.goto(url)
   except Exception as e:
       print(f"Navigation failed: {e}")
   ```

4. **Clean up resources**
   ```python
   try:
       # your code
   finally:
       browser.close()
   ```

5. **Use context managers when possible**
   ```python
   with sync_playwright() as p:
       browser = p.chromium.launch()
       # browser automatically closes
   ```

## Performance Tips

1. **Reuse browser contexts** for multiple pages
2. **Disable unnecessary features**:
   ```python
   context = browser.new_context(
       bypass_csp=True,
       java_script_enabled=True
   )
   ```
3. **Use `wait_for_selector` instead of fixed delays**
4. **Limit screenshot quality** for faster execution:
   ```python
   page.screenshot(path='shot.png', quality=50)
   ```

## Getting Help

If you encounter issues not covered here:

1. Check Docker logs: `docker logs <container>`
2. Run with verbose output: `python3 -v browser_client.py`
3. Test browsers individually: `docker exec -it browser-sandbox bash`
4. Check Playwright documentation: https://playwright.dev/python/docs/intro
