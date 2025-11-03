from playwright.sync_api import sync_playwright
import os

# Get the WebSocket endpoint from the Playwright server
ws_endpoint = os.getenv("PW_TEST_CONNECT_WS_ENDPOINT", "ws://localhost:9222/")

print("=== Web Search Automation with Playwright ===\n")

with sync_playwright() as p:
    # Connect to remote Playwright server
    browser = p.chromium.connect(ws_endpoint)
    
    # Create a new context with additional stealth settings
    context = browser.new_context(
        user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        viewport={"width": 1920, "height": 1080},
        locale="en-US",
        timezone_id="America/New_York",
        # Accept language and other headers
        extra_http_headers={
            "Accept-Language": "en-US,en;q=0.9",
        }
    )
    
    page = context.new_page()
    
    # Try alternative search engines
    search_engines = [
        {
            "name": "Bing",
            "url": "https://www.bing.com/",
            "search_input": 'textarea[name="q"]',
            "result_selector": 'h2'
        },
        {
            "name": "Google",
            "url": "https://www.google.com/",
            "search_input": 'textarea[name="q"]',
            "result_selector": 'h3'
        }
    ]
    
    search_query = "ai agent sandbox"
    success = False
    
    for engine in search_engines:
        try:
            print(f"\n--- Trying {engine['name']} ---")
            page.goto(engine['url'], wait_until="networkidle")
            print(f"✓ Navigated to: {page.url}")
            
            # Wait for page to settle
            page.wait_for_timeout(2000)
            
            # Find and fill search box
            search_box = page.locator(engine['search_input']).first
            search_box.click()
            
            # Type with human-like delays
            for char in search_query:
                search_box.type(char, delay=150)
            
            page.wait_for_timeout(500)
            search_box.press("Enter")
            
            # Wait for results
            page.wait_for_load_state("networkidle", timeout=10000)
            current_url = page.url
            print(f"✓ Search completed: {current_url}")
            
            # Check if we hit a CAPTCHA or error page
            if "sorry" in current_url.lower() or "captcha" in current_url.lower() or "418" in current_url:
                print(f"✗ {engine['name']} blocked the request (CAPTCHA/Rate limit)")
                page.screenshot(path=f"test_{engine['name'].lower()}_blocked.png")
                print(f"  Screenshot saved: test_{engine['name'].lower()}_blocked.png")
                continue
            
            # Try to extract results
            page.wait_for_timeout(2000)
            page.screenshot(path=f"test_{engine['name'].lower()}_results.png")
            print(f"✓ Screenshot saved: test_{engine['name'].lower()}_results.png")
            
            # Try to get result titles
            try:
                results = page.locator(engine['result_selector']).all_text_contents()
                valid_results = [r.strip() for r in results if r.strip() and len(r.strip()) > 10]
                
                if valid_results:
                    print(f"\n✓ Found {len(valid_results)} search results:")
                    for i, result in enumerate(valid_results[:5], 1):
                        # Truncate long titles
                        title = result[:100] + "..." if len(result) > 100 else result
                        print(f"  {i}. {title}")
                    success = True
                    break
                else:
                    print("✗ No valid results found in page")
            except Exception as e:
                print(f"✗ Could not extract results: {type(e).__name__}")
        
        except Exception as e:
            print(f"✗ Error with {engine['name']}: {type(e).__name__}: {str(e)[:100]}")
            continue
    
    # Clean up
    page.close()
    context.close()
    browser.close()

if success:
    print("\n=== ✓ Search completed successfully! ===")
else:
    print("\n=== ✗ All search engines blocked the automation ===")
    print("\nReasons for blocking:")
    print("  • Search engines detect automated browsers")
    print("  • Missing browser fingerprints and navigator properties")
    print("  • Too many rapid requests from the same IP")
    print("\nSolutions:")
    print("  1. Use official search APIs (Google Custom Search API, Bing Web Search API)")
    print("  2. Install playwright-stealth plugin")
    print("  3. Add residential proxies")
    print("  4. Use headful mode (non-headless browser)")
    print("  5. For testing: Check the screenshots to see what pages were loaded")
