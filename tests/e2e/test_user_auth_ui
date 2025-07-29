import pytest
from playwright.sync_api import sync_playwright, expect
import time

# Base URL of the application
BASE_URL = "http://127.0.0.1:8001"

# Helper function to generate unique username
def generate_unique_username():
    return f"testuser_{int(time.time())}"

# Fixture to set up Playwright page
@pytest.fixture(scope="function")
def page():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Set headless=False for debugging
        page = browser.new_page()
        yield page
        page.close()
        browser.close()

# Positive Test: Register with valid data
def test_register_with_valid_data(page):
    username = generate_unique_username()
    page.goto(f"{BASE_URL}/register")

    # Fill in the form with valid data
    page.fill("#username", username)
    page.fill("#email", f"{username}@example.com")
    page.fill("#first_name", "Test")
    page.fill("#last_name", "User")
    page.fill("#password", "ValidPassword123")
    page.fill("#confirm_password", "ValidPassword123")

    # Submit the form
    page.click("button[type='submit']")

    # Confirm success message
    success_message = page.locator("#success-message")
    expect(success_message).to_be_visible()
    expect(success_message).to_have_text("Registration successful! Redirecting to login...")

# Positive Test: Login with correct credentials
def test_login_with_correct_credentials(page):
    # Register a user first
    username = generate_unique_username()
    page.goto(f"{BASE_URL}/register")
    page.fill("#username", username)
    page.fill("#email", f"{username}@example.com")
    page.fill("#first_name", "Test")
    page.fill("#last_name", "User")
    page.fill("#password", "ValidPassword123")
    page.fill("#confirm_password", "ValidPassword123")
    page.click("button[type='submit']")
    page.wait_for_url(f"{BASE_URL}/login")

    # Now login
    page.goto(f"{BASE_URL}/login")
    page.fill("#username", username)
    page.fill("#password", "ValidPassword123")
    page.click("button[type='submit']")

    # Confirm success message and token display
    success_message = page.locator("#success-message")
    expect(success_message).to_be_visible()
    expect(success_message).to_contain_text("Login successful! Access Token:")

    # Check localStorage for token
    access_token = page.evaluate("() => localStorage.getItem('access_token')")
    assert access_token is not None, "Access token not stored in localStorage"

# Negative Test: Register with short password
def test_register_with_short_password(page):
    page.goto(f"{BASE_URL}/register")

    # Fill in the form with short password
    page.fill("#username", "testuser")
    page.fill("#email", "testuser@example.com")
    page.fill("#first_name", "Test")
    page.fill("#last_name", "User")
    page.fill("#password", "short")
    page.fill("#confirm_password", "short")

    # Submit the form
    page.click("button[type='submit']")

    # Confirm client-side error message
    error_message = page.locator("#error-message")
    expect(error_message).to_be_visible()
    expect(error_message).to_have_text("Password must be at least 8 characters long")

# Negative Test: Login with wrong password
def test_login_with_wrong_password(page):
    # Register a user first
    username = generate_unique_username()
    page.goto(f"{BASE_URL}/register")
    page.fill("#username", username)
    page.fill("#email", f"{username}@example.com")
    page.fill("#first_name", "Test")
    page.fill("#last_name", "User")
    page.fill("#password", "ValidPassword123")
    page.fill("#confirm_password", "ValidPassword123")
    page.click("button[type='submit']")
    page.wait_for_url(f"{BASE_URL}/login")

    # Attempt login with wrong password
    page.goto(f"{BASE_URL}/login")
    page.fill("#username", username)
    page.fill("#password", "WrongPassword")
    page.click("button[type='submit']")

    # Confirm server error message
    error_message = page.locator("#error-message")
    expect(error_message).to_be_visible()
    expect(error_message).to_have_text("Invalid username or password")
