#!/usr/bin/env python3
"""
Example Playwright scripts for browser automation in the sandbox
"""

from playwright.sync_api import sync_playwright
import sys


def example_simple_navigation():
    """Simple page navigation and screenshot"""
    print("Example 1: Simple Navigation")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        page = browser.new_page()
        
        page.goto("https://example.com", wait_until="networkidle")
        title = page.title()
        print(f"Page title: {title}")
        
        # Take screenshot
        page.screenshot(path="/tmp/output.png", full_page=True)
        print("Screenshot saved to /tmp/output.png")
        
        browser.close()


def example_form_interaction():
    """Interact with forms"""
    print("Example 2: Form Interaction")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        page = browser.new_page()
        
        # Go to Google
        page.goto("https://www.google.com")
        
        # Accept cookies if present
        try:
            page.click('button:has-text("Accept")', timeout=2000)
        except:
            pass
        
        # Search
        page.fill('textarea[name="q"]', 'Playwright Python')
        page.press('textarea[name="q"]', 'Enter')
        page.wait_for_load_state('networkidle')
        
        print(f"Results page: {page.title()}")
        page.screenshot(path="/tmp/output.png")
        
        browser.close()


def example_data_extraction():
    """Extract data from a webpage"""
    print("Example 3: Data Extraction")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        page = browser.new_page()
        
        # Go to Hacker News
        page.goto("https://news.ycombinator.com")
        
        # Extract article titles
        titles = page.locator('.titleline > a').all_text_contents()
        
        print("Top 10 articles on Hacker News:")
        for i, title in enumerate(titles[:10], 1):
            print(f"{i}. {title}")
        
        browser.close()


def example_multiple_pages():
    """Work with multiple pages"""
    print("Example 4: Multiple Pages")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        context = browser.new_context()
        
        urls = [
            "https://example.com",
            "https://example.org",
            "https://example.net"
        ]
        
        for url in urls:
            page = context.new_page()
            page.goto(url)
            print(f"{url} -> {page.title()}")
        
        browser.close()


def example_wait_for_element():
    """Wait for specific elements"""
    print("Example 5: Wait for Element")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        page = browser.new_page()
        
        page.goto("https://example.com")
        
        # Wait for specific element
        page.wait_for_selector('h1')
        heading = page.locator('h1').text_content()
        print(f"Main heading: {heading}")
        
        browser.close()


def example_mobile_emulation():
    """Emulate mobile device"""
    print("Example 6: Mobile Emulation")
    
    with sync_playwright() as p:
        # Get iPhone 13 device descriptor
        iphone_13 = p.devices['iPhone 13']
        
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        context = browser.new_context(**iphone_13)
        page = context.new_page()
        
        page.goto("https://example.com")
        print(f"Mobile view: {page.viewport_size}")
        
        page.screenshot(path="/tmp/output.png")
        
        browser.close()


def example_javascript_execution():
    """Execute JavaScript in the page"""
    print("Example 7: JavaScript Execution")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        page = browser.new_page()
        
        page.goto("https://example.com")
        
        # Execute JavaScript
        result = page.evaluate("""
            () => {
                return {
                    title: document.title,
                    url: window.location.href,
                    userAgent: navigator.userAgent,
                    innerHeight: window.innerHeight,
                    innerWidth: window.innerWidth
                }
            }
        """)
        
        print("Page info from JavaScript:")
        for key, value in result.items():
            print(f"  {key}: {value}")
        
        browser.close()


def example_network_interception():
    """Intercept network requests"""
    print("Example 8: Network Interception")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        page = browser.new_page()
        
        # Track all network requests
        requests = []
        page.on("request", lambda request: requests.append(request.url))
        
        page.goto("https://example.com")
        
        print(f"Total requests made: {len(requests)}")
        print("Sample requests:")
        for url in requests[:5]:
            print(f"  - {url}")
        
        browser.close()


def run_all_examples():
    """Run all examples"""
    examples = [
        example_simple_navigation,
        example_form_interaction,
        example_data_extraction,
        example_multiple_pages,
        example_wait_for_element,
        example_mobile_emulation,
        example_javascript_execution,
        example_network_interception
    ]
    
    for example in examples:
        try:
            print("\n" + "="*60)
            example()
            print("✓ Success")
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
        print("="*60)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        example_num = int(sys.argv[1])
        examples = [
            example_simple_navigation,
            example_form_interaction,
            example_data_extraction,
            example_multiple_pages,
            example_wait_for_element,
            example_mobile_emulation,
            example_javascript_execution,
            example_network_interception
        ]
        
        if 1 <= example_num <= len(examples):
            examples[example_num - 1]()
        else:
            print(f"Invalid example number. Choose 1-{len(examples)}")
    else:
        run_all_examples()
