Running Playwright E2E Tests

The E2E tests in tests/e2e/test_user_auth_ui.py verify the registration and login functionality, including positive and negative scenarios.

Prerequisites for Tests





Python Dependencies: Ensure Playwright and pytest are installed locally to run tests outside the container.

pip install pytest pytest-playwright requests
playwright install



Docker Container: The app must be running (via docker-compose up -d) for tests to interact with http://127.0.0.1:8000.

Steps to Run Tests





Ensure the App is Running: Start the Docker container if not already running:

docker-compose up -d



Run the Tests: From the project root, execute:

pytest tests/e2e/test_user_auth_ui.py

This runs all E2E tests, which include:





Positive: Register with valid data (username, email, first_name, last_name, password with special character).



Positive: Login with correct credentials, verifying JWT token storage.



Negative: Register with short password, checking client-side error.



Negative: Login with wrong password, checking server 401 error.



Debugging Tests: If tests fail, run in headed mode to watch the browser:

pytest tests/e2e/test_user_auth_ui.py --headed --slowmo=1000





Check screenshots/ for form state (register_form_filled.png, login_page.png).



Review console logs printed by the tests for JavaScript errors or server responses.

Running Tests Inside the Container (Optional)

If you prefer running tests inside the Docker container:





Ensure the Dockerfile includes Playwright:

RUN pip install playwright && playwright install



Rebuild the image:

docker-compose build



Run tests in the container:

docker-compose exec app pytest tests/e2e/test_user_auth_ui.py


