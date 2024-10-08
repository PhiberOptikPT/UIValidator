import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
from urllib.parse import urljoin

# Load environment variables
load_dotenv()

# Configuration
USERNAME = os.getenv("PORTAL_USERNAME")
PASSWORD = os.getenv("PORTAL_PASSWORD")

# Parse paths from environment variable and create full URLs
PATHS_TO_SCREENSHOT = os.getenv("SCREENSHOT_PATHS", "").split(",")

def setup_driver():
    """Set up and return a configured Chrome WebDriver"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)
    chrome_options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration
    chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
    chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--hide-scrollbars")
    chrome_options.add_argument("--enable-logging")
    chrome_options.add_argument("--v=1")  # Verbose logging
    # Add user agent to mimic a real browser
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    # Use webdriver_manager to automatically download and use the correct ChromeDriver version
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

def login(base_url, driver):
    driver.get(urljoin(base_url, "master/portal/"))

    # Wait for username field and enter username
    username_field = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, "username"))
    )
    username_field.send_keys(USERNAME)
    
    # Enter password
    password_field = driver.find_element(By.ID, "password")
    password_field.send_keys(PASSWORD)
    
    # Click login button
    login_button = driver.find_element(By.ID, "loginBtn")
    login_button.click()

    # Wait for login to complete (adjust the selector as needed)
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, "sigma_main_panel"))
    )

def get_filename_from_path(path):
    name = path.strip('/').replace('/', '_')
    if not name:
        name = 'home'
    return f"{name}.png"

def take_screenshot(driver, url, dir, filename):
    """Navigate to URL and take a screenshot"""
    driver.get(url)

    # Wait for page to load (adjust the selector as needed)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    #Wait for eventual spinner to disappear
    time.sleep(10)

    # Take screenshot
    driver.save_screenshot(f"{dir}/{filename}")
    print(f"Screenshot saved: {dir}/{filename}")

def construct_url(base_url, path):
    # Ensure there's exactly one slash between each part
    return '/'.join([base_url.rstrip('/'), path.lstrip('/')])

def capture_screenshots(base_url, old_relase, new_release):
    old_dir = "screenshots/old"
    new_dir = "screenshots/new"

    # Ensure the output directory exists
    os.makedirs(old_dir, exist_ok=True)
    os.makedirs(new_dir, exist_ok=True)

    driver = setup_driver()
    
    old_url = urljoin(base_url, old_relase)
    new_url = urljoin(base_url, new_release)

    try:
        print("Initiating login")
        login(base_url, driver)
        print("Login completed successfully")

        print("Initiating screenshot capture")
        for _, path in enumerate(PATHS_TO_SCREENSHOT):
            filename = get_filename_from_path(path)
            
            take_screenshot(driver, construct_url(old_url, path), old_dir, filename)
            take_screenshot(driver, construct_url(new_url, path), new_dir, filename)
    finally:
        driver.quit()

if __name__ == "__main__":
    base_url = os.getenv("BASE_URL")
    old_release = os.getenv("OLD_RELEASE")
    new_release = os.getenv("NEW_RELEASE")
    capture_screenshots(base_url, old_release, new_release)