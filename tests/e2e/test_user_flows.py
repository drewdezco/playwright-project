"""
Complete user workflow tests.
Tests multi-step user journeys, state management across pages, and error handling in flows.
"""
import pytest
from playwright.sync_api import Page, expect


@pytest.mark.e2e
class TestUserFlows:
    """Complete user workflow examples."""
    
    def test_complete_login_flow(self, page: Page):
        """Test complete login workflow."""
        # Navigate to login page
        page.goto("https://the-internet.herokuapp.com/login")
        
        # Fill credentials
        page.locator("#username").fill("tomsmith")
        page.locator("#password").fill("SuperSecretPassword!")
        
        # Submit
        page.locator('button[type="submit"]').click()
        
        # Verify successful login
        page.wait_for_load_state("networkidle")
        success_message = page.locator(".flash.success")
        expect(success_message).to_be_visible()
        assert "You logged into a secure area!" in success_message.text_content()
        
        # Verify navigation to secure area
        assert "secure" in page.url.lower()
    
    def test_multi_page_navigation_flow(self, page: Page, base_url: str):
        """Test navigating through multiple pages."""
        # Start at homepage
        page.goto(base_url)
        page.wait_for_load_state("networkidle")
        
        # Navigate to docs
        get_started = page.get_by_role("link", name="Get started")
        get_started.click()
        page.wait_for_load_state("networkidle")
        
        # Verify we're on docs page
        assert "docs" in page.url.lower() or "get-started" in page.url.lower()
        
        # Navigate back
        page.go_back()
        page.wait_for_load_state("networkidle")
        
        # Verify we're back at homepage
        assert base_url in page.url or "playwright.dev" in page.url
    
    def test_form_submission_flow(self, page: Page):
        """Test complete form submission workflow."""
        page.goto("https://the-internet.herokuapp.com/login")
        
        # Fill form
        username = page.locator("#username")
        password = page.locator("#password")
        
        username.fill("tomsmith")
        password.fill("SuperSecretPassword!")
        
        # Submit
        page.locator('button[type="submit"]').click()
        
        # Wait for redirect
        page.wait_for_load_state("networkidle")
        
        # Verify success state
        logout_button = page.locator("a", has_text="Logout")
        expect(logout_button).to_be_visible()
        
        # Logout
        logout_button.click()
        page.wait_for_load_state("networkidle")
        
        # Verify logged out
        assert "login" in page.url.lower()
    
    def test_search_flow(self, page: Page, base_url: str):
        """Test search functionality workflow."""
        page.goto(base_url)
        page.wait_for_load_state("networkidle")
        
        # Look for search functionality
        # Note: Playwright.dev may have search, this is a pattern example
        search_input = page.locator('input[type="search"], input[placeholder*="search" i]').first
        
        if search_input.is_visible():
            search_input.fill("testing")
            search_input.press("Enter")
            page.wait_for_load_state("networkidle")
            
            # Verify search results
            results = page.locator("article, .result, .search-result")
            if results.count() > 0:
                expect(results.first).to_be_visible()
    
    def test_error_handling_flow(self, page: Page):
        """Test error handling in user flow."""
        page.goto("https://the-internet.herokuapp.com/login")
        
        # Submit with invalid credentials
        page.locator("#username").fill("invalid")
        page.locator("#password").fill("invalid")
        page.locator('button[type="submit"]').click()
        
        # Wait for error
        page.wait_for_load_state("networkidle")
        
        # Verify error message
        error_message = page.locator(".flash.error")
        expect(error_message).to_be_visible()
        assert "Your username is invalid!" in error_message.text_content()
        
        # Retry with correct credentials
        page.locator("#username").fill("tomsmith")
        page.locator("#password").fill("SuperSecretPassword!")
        page.locator('button[type="submit"]').click()
        
        # Verify success after retry
        page.wait_for_load_state("networkidle")
        success_message = page.locator(".flash.success")
        expect(success_message).to_be_visible()
    
    def test_state_persistence_flow(self, page: Page):
        """Test state persistence across page interactions."""
        page.goto("https://the-internet.herokuapp.com/login")
        
        # Login
        page.locator("#username").fill("tomsmith")
        page.locator("#password").fill("SuperSecretPassword!")
        page.locator('button[type="submit"]').click()
        page.wait_for_load_state("networkidle")
        
        # Verify logged in state
        logout_button = page.locator("a", has_text="Logout")
        expect(logout_button).to_be_visible()
        
        # Navigate to another page (if available)
        # Then verify still logged in
        page.goto("https://the-internet.herokuapp.com")
        page.wait_for_load_state("networkidle")
        
        # Go back to secure area
        page.goto("https://the-internet.herokuapp.com/secure")
        page.wait_for_load_state("networkidle")
        
        # Verify still logged in
        logout_button = page.locator("a", has_text="Logout")
        expect(logout_button).to_be_visible()


@pytest.mark.e2e
class TestComplexWorkflows:
    """Complex multi-step workflow examples."""
    
    def test_multi_step_form_flow(self, page: Page):
        """Test multi-step form workflow."""
        # Using a demo site with multi-step forms
        page.goto("https://the-internet.herokuapp.com/login")
        
        # Step 1: Login
        page.locator("#username").fill("tomsmith")
        page.locator("#password").fill("SuperSecretPassword!")
        page.locator('button[type="submit"]').click()
        page.wait_for_load_state("networkidle")
        
        # Step 2: Navigate to a feature
        # Step 3: Perform action
        # Step 4: Verify result
        
        # This pattern can be extended for actual multi-step forms
    
    def test_data_entry_flow(self, page: Page):
        """Test data entry workflow with validation."""
        page.goto("https://the-internet.herokuapp.com/login")
        
        # Enter data
        username_field = page.locator("#username")
        password_field = page.locator("#password")
        
        # Validate fields are empty initially
        assert username_field.input_value() == ""
        assert password_field.input_value() == ""
        
        # Fill data
        username_field.fill("tomsmith")
        password_field.fill("SuperSecretPassword!")
        
        # Validate data was entered
        assert username_field.input_value() == "tomsmith"
        assert len(password_field.input_value()) > 0
        
        # Submit
        page.locator('button[type="submit"]').click()
        page.wait_for_load_state("networkidle")
        
        # Verify success
        success_message = page.locator(".flash.success")
        expect(success_message).to_be_visible()
    
    def test_workflow_with_retry(self, page: Page):
        """Test workflow with retry logic."""
        max_retries = 3
        success = False
        
        for attempt in range(max_retries):
            try:
                page.goto("https://the-internet.herokuapp.com/login")
                page.locator("#username").fill("tomsmith")
                page.locator("#password").fill("SuperSecretPassword!")
                page.locator('button[type="submit"]').click()
                page.wait_for_load_state("networkidle")
                
                # Verify success
                success_message = page.locator(".flash.success")
                expect(success_message).to_be_visible(timeout=5000)
                success = True
                break
            except Exception as e:
                if attempt < max_retries - 1:
                    page.reload()
                    continue
                else:
                    raise
        
        assert success, "Workflow failed after retries"

