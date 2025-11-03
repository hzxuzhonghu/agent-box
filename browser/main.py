from playwright.sync_api import sync_playwright
import os

# Get the WebSocket endpoint from the Playwright server
# The server endpoint should be ws://localhost:9222/
ws_endpoint = os.getenv("PW_TEST_CONNECT_WS_ENDPOINT", "ws://localhost:9222/")

with sync_playwright() as p:
    # Connect to remote Playwright server
    browser = p.chromium.connect(ws_endpoint)
    
    # Create a new context with stealth settings
    context = browser.new_context(
        user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        viewport={"width": 1920, "height": 1080},
        locale="en-US",
        timezone_id="America/New_York",
        extra_http_headers={
            "Accept-Language": "en-US,en;q=0.9",
        }
    )
    
    page = context.new_page()
    
    # Navigate to Bing (more automation-friendly than Google)
    page.goto("https://www.bing.com/", wait_until="networkidle")
    print(f"Navigated to: {page.url}")
    
    # Wait a moment for the page to fully load (more human-like)
    page.wait_for_timeout(2000)
    
    # Search for "ai agent sandbox" with more human-like typing
    search_box = page.locator('textarea[name="q"]').first
    search_box.click()
    
    # Type character by character with human-like delays
    search_query = "ai agent sandbox"
    for char in search_query:
        search_box.type(char, delay=150)
    
    # Wait a bit before pressing Enter
    page.wait_for_timeout(500)
    search_box.press("Enter")
    
    # Wait for search results to load
    page.wait_for_load_state("networkidle", timeout=10000)
    print(f"Search completed: {page.url}")
    
    # Extract and print some search result titles
    try:
        # Wait for search results
        page.wait_for_timeout(2000)
        results = page.locator('h2').all_text_contents()
        valid_results = [r.strip() for r in results if r.strip() and len(r.strip()) > 10]
        
        print(f"\nFound {len(valid_results)} search results:")
        for i, result in enumerate(valid_results[:5], 1):
            # Truncate long titles
            title = result[:100] + "..." if len(result) > 100 else result
            print(f"  {i}. {title}")
    except Exception as e:
        print(f"Note: Could not extract results: {type(e).__name__}")
    
    # Take a screenshot of the search results
    page.screenshot(path="test_screenshot.png")
    print("\nScreenshot saved to test_screenshot.png")
    
    # Clean up
    page.close()
    context.close()
    browser.close()
    
print("Success!")
