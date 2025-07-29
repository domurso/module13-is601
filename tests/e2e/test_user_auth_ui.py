import pytest
from playwright.sync_api import sync_playwright, expect
import time
import requests
from requests.exceptions import ConnectionError

# Base URL of the application (Docker-mapped port)
BASE_URL = "http://127.0.0.1:8000"

# Helper function to generate unique username
def generate_unique_username():
    return f"testuser_{int(time.time())}"

# Helper function to check if server is up
def is_server_up(url, timeout=5, max_attempts=5):
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{url}/health", timeout=timeout)
            print(f"Health check attempt {attempt + 1}: {response.status_code}")
            return response.status_code == 200
        except ConnectionError:
            print(f"Health check attempt {attempt + 1} failed: ConnectionError")
            time.sleep(2)
    return False

# Fixture to set up Playwright page and check server
@pytest.fixture(scope="function")
def page():
    if not is_server_up(BASE_URL):
        pytest.fail(f"Server not running at {BASE_URL}. Ensure Docker container is running with port mapping '-p 8000:8001' and FastAPI app is started.")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Set headless=False for debugging
        page = browser.new_page()
        # Capture console logs for debugging
        page.on("console", lambda msg: print(f"Browser console: {msg.text}"))
        yield page
        page.close()
        browser.close()

# Positive Test: Register with valid data
def test_register_with_valid_data(page):
    username = generate_unique_username()
    
    # Navigate with retry
    for attempt in range(3):
        try:
            page.goto(f"{BASE_URL}/register", timeout=15000)
            print(f"Navigated to {BASE_URL}/register")
            break
        except Exception as e:
            print(f"Navigation attempt {attempt + 1} failed: {str(e)}")
            if attempt == 2:
                pytest.fail(f"Failed to navigate to {BASE_URL}/register after 3 attempts: {str(e)}")
            time.sleep(2)

    # Fill in the form with valid data
    page.fill("#username", username)
    page.fill("#email", f"{username}@example.com")
    page.fill("#first_name", "Test")
    page.fill("#last_name", "User")
    page.fill("#password", "ValidPassword123!")
    page.fill("#confirm_password", "ValidPassword123!")

    # Debug: Capture form state
    page.screenshot(path="screenshots/register_form_filled.png")
    
    # Submit the form and intercept response
    with page.expect_response("**/auth/register") as response_info:
        page.click("button[type='submit']")
        response = response_info.value
        response_body = response.text()
        print(f"Register response: {response.status} {response_body}")
        assert response.status == 201, f"Expected 201, got {response.status}: {response_body}"

    # Confirm success message
    success_message = page.locator("#success-message")
    expect(success_message).to_be_visible(timeout=30000)
    expect(success_message).to_have_text("Registration successful! Redirecting to login...")

    # Confirm redirect to /login
    page.wait_for_url(f"{BASE_URL}/login", timeout=30000)
    print(f"Redirected to {page.url}")

# Positive Test: Login with correct credentials
def test_login_with_correct_credentials(page):
    # Register a user first
    username = generate_unique_username()
    page.goto(f"{BASE_URL}/register")
    page.fill("#username", username)
    page.fill("#email", f"{username}@example.com")
    page.fill("#first_name", "Test")
    page.fill("#last_name", "User")
    page.fill("#password", "ValidPassword123!")
    page.fill("#confirm_password", "ValidPassword123!")
    page.click("button[type='submit']")
    page.wait_for_url(f"{BASE_URL}/login", timeout=30000)

    # Debug: Check login page loaded
    page.screenshot(path="screenshots/login_page.png")

    # Now login
    page.goto(f"{BASE_URL}/login")
    page.fill("#username", username)
    page.fill("#password", "ValidPassword123!")
    
    # Intercept login response
    with page.expect_response("**/auth/login") as response_info:
        page.click("button[type='submit']")
        response = response_info.value
        response_body = response.text()
        print(f"Login response: {response.status} {response_body}")
        assert response.status == 200, f"Expected 200, got {response.status}: {response_body}"

    # Confirm success message and token display
    success_message = page.locator("#success-message")
    expect(success_message).to_be_visible(timeout=30000)
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
    expect(error_message).to_be_visible(timeout=30000)
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
    page.fill("#password", "ValidPassword123!")
    page.fill("#confirm_password", "ValidPassword123!")
    page.click("button[type='submit']")
    page.wait_for_url(f"{BASE_URL}/login", timeout=30000)

    # Attempt login with wrong password
    page.goto(f"{BASE_URL}/login")
    page.fill("#username", username)
    page.fill("#password", "WrongPassword")
    
    # Intercept login response
    with page.expect_response("**/auth/login") as response_info:
        page.click("button[type='submit']")
        response = response_info.value
        response_body = response.text()
        print(f"Login response: {response.status} {response_body}")
        assert response.status == 401, f"Expected 401, got {response.status}: {response_body}"

    # Confirm server error message
    error_message = page.locator("#error-message")
    expect(error_message).to_be_visible(timeout=30000)
    expect(error_message).to_have_text("Invalid username or password")
