import time
from playwright.sync_api import sync_playwright, expect

def verify_frontend():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 1. Navigate to Dashboard
        print("Navigating to dashboard...")
        page.goto("http://localhost:5000")
        page.wait_for_selector("body")

        # Check initial state
        print("Checking initial state...")
        # Status should be ready
        expect(page.locator("#status-text")).to_have_text("Ready")

        # Check Market Clock Widget
        print("Checking Market Clock...")
        clock = page.locator(".market-clock-widget")
        expect(clock).to_be_visible()
        expect(page.locator("#ist-clock")).to_contain_text("IST")
        expect(page.locator("#session-london")).to_be_visible()

        # 2. Check Session State
        print("Checking session state...")
        # If session is active, end it to test modal
        if page.locator(".btn-session-end").is_visible():
            print("Ending previous session...")
            # We need to handle the confirm dialog
            page.on("dialog", lambda dialog: dialog.accept())
            page.locator(".btn-session-end").click()
            # Wait for end
            expect(page.locator(".btn-session-start")).to_be_visible()

        # 3. Check Session Modal
        print("Opening session modal...")
        page.locator(".btn-session-start").click()

        # Verify Modal appears
        modal = page.locator("#start-session-modal")
        expect(modal).to_be_visible()
        print("Modal visible.")

        # Verify Modal Content
        expect(page.locator("#modal-session-name")).to_be_visible()
        expect(page.locator("input[name='session-mode'][value='demo']")).to_be_checked()
        expect(page.locator("input[name='session-mode'][value='live']")).not_to_be_checked()
        expect(page.locator("#modal-market-type")).to_have_value("binary")

        # Test Live Mode Warning
        print("Testing Live Mode warning...")
        page.locator("input[name='session-mode'][value='live']").click()
        expect(page.locator("#live-warning")).to_be_visible()

        # Switch back to Demo
        page.locator("input[name='session-mode'][value='demo']").click()
        expect(page.locator("#live-warning")).not_to_be_visible()

        # 4. Start a Session
        print("Starting session...")
        page.locator("#modal-session-name").fill("Test Playwright Session")
        page.locator("#modal-market-type").select_option("crypto")

        # Click Start
        page.get_by_text("Start Session", exact=True).click()

        # Wait for session to start (modal closes)
        expect(modal).not_to_be_visible()

        # 5. Verify Badge
        print("Verifying badge...")
        badge = page.locator("#mode-badge")
        # Increase timeout to 12s to account for 10s polling interval
        expect(badge).to_be_visible(timeout=12000)
        expect(badge).to_have_text("🔵 DEMO MODE")

        # 6. Verify Journal Page
        print("Navigating to Journal...")
        page.goto("http://localhost:5000/journal")

        # Verify Filters
        expect(page.locator("#filter-mode")).to_be_visible()
        expect(page.locator("#filter-market")).to_be_visible()

        # Verify Tabs
        expect(page.locator("button.tab-btn:has-text('All Trades')")).to_be_visible()
        expect(page.locator("button.tab-btn:has-text('Rejected Trades')")).to_be_visible()

        # Verify Market Clock is also on Journal page
        expect(page.locator(".market-clock-widget")).to_be_visible()

        # Screenshot
        print("Taking screenshot...")
        page.screenshot(path="/home/jules/verification/verification.png")
        print("Verification complete.")

        browser.close()

if __name__ == "__main__":
    verify_frontend()
