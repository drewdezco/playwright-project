"""
Browser automation fundamentals using Playwright.
Tests page navigation, element interactions, form submissions, screenshots, and network interception.
"""
import pytest
from playwright.sync_api import Page, expect


@pytest.mark.e2e
class TestBrowserBasics:
    """Basic browser automation examples."""
    
    def test_page_navigation(self, page: Page, base_url: str):
        """Test basic page navigation."""
        page.goto(base_url)
        
        # Wait for page to load
        page.wait_for_load_state("networkidle")
        
        # Assert page title
        assert "Playwright" in page.title()
    
    def test_element_interaction(self, page: Page, base_url: str):
        """Test clicking elements."""
        page.goto(base_url)
        
        # Find and click a link
        get_started_link = page.get_by_role("link", name="Get started")
        get_started_link.click()
        
        # Wait for navigation
        page.wait_for_load_state("networkidle")
        
        # Verify navigation occurred
        assert "get-started" in page.url.lower() or "docs" in page.url.lower()
    
    def test_form_filling(self, page: Page):
        """Test filling out forms."""
        # Using a demo form site
        page.goto("https://the-internet.herokuapp.com/login")
        
        # Fill username
        username_field = page.locator("#username")
        username_field.fill("tomsmith")
        
        # Fill password
        password_field = page.locator("#password")
        password_field.fill("SuperSecretPassword!")
        
        # Submit form
        submit_button = page.locator('button[type="submit"]')
        submit_button.click()
        
        # Verify success
        page.wait_for_load_state("networkidle")
        success_message = page.locator(".flash.success")
        expect(success_message).to_be_visible()
    
    def test_text_input(self, page: Page):
        """Test typing text into input fields."""
        page.goto("https://the-internet.herokuapp.com/login")
        
        username_field = page.locator("#username")
        username_field.type("tomsmith", delay=100)  # Type with delay
        
        # Verify text was entered
        assert username_field.input_value() == "tomsmith"
    
    def test_checkbox_interaction(self, page: Page):
        """Test checkbox interactions."""
        page.goto("https://the-internet.herokuapp.com/checkboxes")
        
        checkboxes = page.locator('input[type="checkbox"]')
        first_checkbox = checkboxes.first
        
        # Check if already checked, then toggle
        if not first_checkbox.is_checked():
            first_checkbox.check()
        
        assert first_checkbox.is_checked()
    
    def test_dropdown_selection(self, page: Page):
        """Test selecting from dropdown."""
        page.goto("https://the-internet.herokuapp.com/dropdown")
        
        dropdown = page.locator("#dropdown")
        dropdown.select_option("2")
        
        selected_value = dropdown.input_value()
        assert selected_value == "2"
    
    def test_screenshot_capture(self, page: Page, base_url: str):
        """Test capturing screenshots."""
        page.goto(base_url)
        page.wait_for_load_state("networkidle")
        
        # Full page screenshot
        page.screenshot(path="screenshots/full_page.png", full_page=True)
        
        # Element screenshot
        header = page.locator("header").first
        if header.is_visible():
            header.screenshot(path="screenshots/header.png")
    
    def test_network_interception(self, page: Page):
        """Test intercepting network requests."""
        intercepted_requests = []
        
        def handle_request(request):
            intercepted_requests.append({
                "url": request.url,
                "method": request.method
            })
        
        page.on("request", handle_request)
        
        page.goto("https://playwright.dev")
        page.wait_for_load_state("networkidle")
        
        # Verify requests were intercepted
        assert len(intercepted_requests) > 0
    
    def test_wait_for_element(self, page: Page, base_url: str):
        """Test waiting for elements to appear."""
        page.goto(base_url)
        
        # Wait for specific element
        header = page.locator("header").first
        header.wait_for(state="visible", timeout=10000)
        
        assert header.is_visible()
    
    def test_element_assertions(self, page: Page, base_url: str):
        """Test Playwright's expect assertions."""
        page.goto(base_url)
        
        # Use expect API for assertions
        header = page.locator("header").first
        expect(header).to_be_visible()
        
        # Assert text content
        title = page.locator("h1").first
        if title.is_visible():
            expect(title).to_contain_text("Playwright")
    
    def test_keyboard_interactions(self, page: Page):
        """Test keyboard interactions."""
        page.goto("https://the-internet.herokuapp.com/key_presses")
        
        input_field = page.locator("#target")
        input_field.click()
        
        # Press keys
        page.keyboard.press("Enter")
        page.keyboard.type("Hello World")
        
        # Verify input
        assert "Hello World" in input_field.input_value()


@pytest.mark.e2e
class TestAdvancedInteractions:
    """Advanced browser interaction examples."""
    
    def test_hover_interaction(self, page: Page):
        """Test hovering over elements."""
        page.goto("https://the-internet.herokuapp.com/hovers")
        
        # Hover over first figure
        figure = page.locator(".figure").first
        figure.hover()
        
        # Verify hover effect (caption becomes visible)
        caption = figure.locator(".figcaption")
        expect(caption).to_be_visible()
    
    def test_drag_and_drop(self, page: Page):
        """Test drag and drop functionality."""
        page.goto("https://the-internet.herokuapp.com/drag_and_drop")
        
        box_a = page.locator("#column-a")
        box_b = page.locator("#column-b")
        
        # Drag A to B
        box_a.drag_to(box_b)
        
        # Verify swap occurred
        assert box_a.text_content() == "B"
        assert box_b.text_content() == "A"
    
    def test_file_upload(self, page: Page):
        """Test file upload."""
        page.goto("https://the-internet.herokuapp.com/upload")
        
        # Create a test file
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("Test file content")
            temp_file = f.name
        
        try:
            # Upload file
            file_input = page.locator("#file-upload")
            file_input.set_input_files(temp_file)
            
            # Submit
            submit_button = page.locator("#file-submit")
            submit_button.click()
            
            # Verify upload success
            success_message = page.locator("#uploaded-files")
            expect(success_message).to_be_visible()
        finally:
            # Cleanup
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def test_alerts_and_dialogs(self, page: Page):
        """Test handling alerts and dialogs."""
        page.goto("https://the-internet.herokuapp.com/javascript_alerts")
        
        # Handle alert
        page.on("dialog", lambda dialog: dialog.accept())
        
        alert_button = page.locator("button", has_text="Click for JS Alert")
        alert_button.click()
        
        # Alert should be handled automatically
    
    def test_iframe_interaction(self, page: Page):
        """Test interacting with iframes."""
        page.goto("https://the-internet.herokuapp.com/iframe")
        
        # Switch to iframe
        iframe = page.frame_locator("#mce_0_ifr")
        editor = iframe.locator("body")
        
        # Clear and type in iframe
        editor.clear()
        editor.type("Hello from Playwright!")
        
        # Verify content
        assert "Hello from Playwright!" in editor.text_content()

