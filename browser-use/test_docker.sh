#!/bin/bash
# Test script to verify Docker image and browser automation

set -e

echo "=========================================="
echo "Testing browser-use Docker image"
echo "=========================================="
echo ""

# Test 1: Check if Docker is running
echo "Test 1: Check Docker"
if docker ps >/dev/null 2>&1; then
    echo "✓ Docker is running"
else
    echo "✗ Docker is not running"
    exit 1
fi

# Test 2: Check if image exists
echo ""
echo "Test 2: Check if browser-use image exists"
if docker images | grep -q "browser-use"; then
    echo "✓ browser-use image found"
else
    echo "✗ browser-use image not found. Building..."
    docker build -t browser-use:latest .
fi

# Test 3: Test Playwright installation
echo ""
echo "Test 3: Test Playwright installation in container"
docker run --rm browser-use:latest python3 -c "from playwright.sync_api import sync_playwright; print('✓ Playwright imported successfully')"

# Test 4: Check browser executables
echo ""
echo "Test 4: Check browser installation"
docker run --rm browser-use:latest bash -c "
if [ -d '/ms-playwright' ]; then
    echo '✓ Browser directory exists at /ms-playwright'
    ls -la /ms-playwright/ | head -5
else
    echo '✗ Browser directory not found'
    exit 1
fi
"

# Test 5: Simple browser test
echo ""
echo "Test 5: Run simple browser automation"
docker run --rm browser-use:latest python3 << 'PYTHON'
from playwright.sync_api import sync_playwright

print("Launching browser...")
with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=['--no-sandbox', '--disable-dev-shm-usage']
    )
    print("✓ Browser launched successfully")
    page = browser.new_page()
    print("✓ Page created")
    page.goto("about:blank")
    print("✓ Navigation works")
    browser.close()
    print("✓ Browser closed")

print("\n✓ All browser tests passed!")
PYTHON

echo ""
echo "=========================================="
echo "✓ All tests passed!"
echo "=========================================="
