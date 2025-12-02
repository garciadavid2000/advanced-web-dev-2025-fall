import pytest
import threading
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from app import create_app
from app.extensions import db

# Configure port for the test server
TEST_PORT = 5001
TEST_SERVER_URL = f'http://localhost:{TEST_PORT}'

@pytest.fixture(scope='session')
def live_server():
    """Run the Flask app in a separate thread for E2E testing."""
    app = create_app('testing')
    
    # Disable reloader and debugger for the thread
    app.debug = False
    app.use_reloader = False
    
    # Create a thread to run the app
    server_thread = threading.Thread(target=app.run, kwargs={'port': TEST_PORT, 'use_reloader': False})
    server_thread.daemon = True
    server_thread.start()
    
    # Give the server a moment to start
    time.sleep(1)
    
    yield app
    
    # No clean shutdown for thread, but daemon threads are killed when main process exits

@pytest.fixture(scope='module')
def driver():
    """Setup Selenium WebDriver."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run headless for CI/CD compatibility
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    yield driver
    
    driver.quit()

def test_landing_page_loads(live_server, driver):
    """Test that the landing page loads correctly."""
    driver.get(TEST_SERVER_URL)
    assert "Task Tracking" in driver.title or "Streaks" in driver.title

def test_auth_bypass_and_dashboard_access(live_server, driver):
    """Test authentication bypass and access to protected dashboard."""
    import requests
    
    # 1. Create a session via the test-login endpoint
    # We use requests first to get the session cookie
    response = requests.post(f"{TEST_SERVER_URL}/auth/test-login")
    assert response.status_code == 200
    
    # Extract the session cookie
    session_cookie = response.cookies.get('session')
    assert session_cookie is not None
    
    # 2. Set the cookie in Selenium
    # Selenium needs to be on the domain to set cookies for it
    driver.get(TEST_SERVER_URL + "/404") # Go to a dummy page on the domain
    
    driver.add_cookie({
        'name': 'session',
        'value': session_cookie,
        'path': '/'
    })
    
    # 3. Navigate to the dashboard (or a protected route)
    # Assuming '/' is the dashboard for logged-in users or there is a specific '/dashboard'
    # Based on api.ts, if no session, redirects. If session, should show content.
    driver.get(TEST_SERVER_URL + "/")
    
    # 4. Verify we are logged in
    time.sleep(1) # Wait for page load
    assert "/signin" not in driver.current_url

def test_task_lifecycle(live_server, driver):
    """Test the full lifecycle of a task: Create -> Edit -> Complete -> Delete."""
    import requests
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import Select

    # --- 1. Login ---
    # We need to ensure we are logged in. Re-using the session from previous test might work 
    # if the browser session persists, but let's be safe and re-login or check.
    # Since driver fixture is module scoped, it keeps the session.
    # But let's verify we are on the dashboard.
    driver.get(TEST_SERVER_URL)
    time.sleep(1)
    
    if "/signin" in driver.current_url:
        # Perform login again if needed
        response = requests.post(f"{TEST_SERVER_URL}/auth/test-login")
        session_cookie = response.cookies.get('session')
        driver.get(TEST_SERVER_URL + "/404")
        driver.add_cookie({'name': 'session', 'value': session_cookie, 'path': '/'})
        driver.get(TEST_SERVER_URL)
        time.sleep(1)

    wait = WebDriverWait(driver, 10)

    # --- 2. Create Task ---
    # Click "Create your first task" (empty state) or Sidebar "+" button
    try:
        create_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Create your first task')]")))
        create_btn.click()
    except:
        # Fallback for non-empty state (if we ran tests sequentially without clearing db, but db is in-memory so it should be empty)
        # Or if the button text is different.
        pass

    # Wait for modal
    wait.until(EC.visibility_of_element_located((By.XPATH, "//h2[contains(text(), 'Create New Task')]")))

    # Fill Title
    title_input = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[placeholder='e.g., Go to gym']")))
    title_input.send_keys("Test Task")

    # Select Days (Mon, Wed, Fri)
    for day in ['Mon', 'Wed', 'Fri']:
        day_btn = driver.find_element(By.XPATH, f"//button[text()='{day}']")
        day_btn.click()

    # Select Category
    category_select_elem = wait.until(EC.visibility_of_element_located((By.TAG_NAME, "select")))
    category_select = Select(category_select_elem)
    category_select.select_by_visible_text("Work")

    # Click Create
    submit_btn = driver.find_element(By.XPATH, "//button[text()='Create Task']")
    submit_btn.click()

    # Wait for modal to close and task to appear
    wait.until(EC.invisibility_of_element_located((By.XPATH, "//h2[contains(text(), 'Create New Task')]")))
    wait.until(EC.visibility_of_element_located((By.XPATH, "//h3[contains(text(), 'Test Task')]")))

    # --- 3. Edit Task ---
    # Click on the task title
    task_title = driver.find_element(By.XPATH, "//h3[contains(text(), 'Test Task')]")
    task_title.click()

    # Wait for Edit Modal
    wait.until(EC.visibility_of_element_located((By.XPATH, "//h2[contains(text(), 'Edit Task')]")))

    # Change Title
    edit_input = driver.find_element(By.CSS_SELECTOR, "input[value='Test Task']")
    edit_input.clear()
    edit_input.send_keys("Updated Task")

    # Click Save
    save_btn = driver.find_element(By.XPATH, "//button[text()='Save Changes']")
    save_btn.click()

    # Wait for modal close and new title
    wait.until(EC.invisibility_of_element_located((By.XPATH, "//h2[contains(text(), 'Edit Task')]")))
    wait.until(EC.visibility_of_element_located((By.XPATH, "//h3[contains(text(), 'Updated Task')]")))

    # --- 4. Complete Task ---
    complete_btn = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Complete Updated Task']")
    complete_btn.click()

    # Verify completion
    def is_button_disabled(d):
        btn = d.find_element(By.CSS_SELECTOR, "button[aria-label='Complete Updated Task']")
        return not btn.is_enabled()
    
    wait.until(is_button_disabled)

    # --- 5. Delete Task ---
    task_title_updated = driver.find_element(By.XPATH, "//h3[contains(text(), 'Updated Task')]")
    task_title_updated.click()

    # Wait for Edit Modal
    wait.until(EC.visibility_of_element_located((By.XPATH, "//h2[contains(text(), 'Edit Task')]")))

    # Click Delete
    delete_btn = driver.find_element(By.XPATH, "//button[text()='Delete']")
    delete_btn.click()

    # Handle Alert
    wait.until(EC.alert_is_present())
    alert = driver.switch_to.alert
    alert.accept()

    # Verify Task is Gone
    wait.until(EC.invisibility_of_element_located((By.XPATH, "//h3[contains(text(), 'Updated Task')]")))

