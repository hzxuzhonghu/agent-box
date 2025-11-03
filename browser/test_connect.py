from playwright.sync_api import sync_playwright
import sys

endpoints_to_try = [
    "ws://localhost:9222/",
    "ws://localhost:9222",
    "http://localhost:9222",
]

for endpoint in endpoints_to_try:
    print(f"\nTrying endpoint: {endpoint}")
    try:
        with sync_playwright() as p:
            browser = p.chromium.connect(endpoint, timeout=5000)
            print(f"✓ SUCCESS with {endpoint}")
            browser.close()
            sys.exit(0)
    except Exception as e:
        print(f"✗ FAILED: {type(e).__name__}: {str(e)[:100]}")

print("\nAll endpoints failed")
