# URL = https://qaplayground.dev/apps/new-tab/
# In this task there's a menu, one bar of which is a dropdown menu with more layers
# Aim: Test all elements of the dropdown menu without overloading the code

# Test cases plan:
# 1. Button is clickable
# 2. Clicking on button leads to the change of URL
# 3. Page is opened in a new tab
# 4. The text on the new page is what's required
# 5. Target attribute check -- Confirm that the button has target="_blank"
# 6. No duplicate tabs -- Ensure that repeated clicks don’t open multiple unnecessary tabs
# 7. HTTP response
# 8. Title of the new page

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
import pytest
import requests

BASE_URL = "https://qaplayground.dev/apps/new-tab/"

# This sets up the browser. It opens the site before the tests start and closes it after all are done.
@pytest.fixture
def driver():
    options = Options()
    options.add_argument("--start-maximized")  

    driver = webdriver.Chrome(options=options)  
    driver.get(BASE_URL)
    yield driver
    driver.quit()

def test_button_is_clickable(driver):
    wait = WebDriverWait(driver, 10)
    button = wait.until(EC.visibility_of_element_located((By.XPATH, ".//div[@class='flex-center']/a")))

    # Wait until the button is clickable
    button = wait.until(EC.element_to_be_clickable((By.XPATH, ".//div[@class='flex-center']/a")))

    button = driver.find_element(By.XPATH, ".//div[@class='flex-center']/a")
    assert button.is_displayed(), 'Button is not displayed'
    assert button.is_enabled(), 'Button is not clickable'
    
def test_after_button_click_the_new_url_has_changed(driver):
    # Save current window handle (old tab)
    old_window = driver.current_window_handle
    old_url = driver.current_url

    # Click the link that opens a new tab
    driver.find_element(By.XPATH, ".//div[@class='flex-center']/a").click()

    # Wait until a new window/tab is opened
    WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))

    # Get all window handles
    windows = driver.window_handles

    # Switch to the new tab (the one that's not the original)
    for window in windows:
        if window != old_window:
            driver.switch_to.window(window)
            break

    # Now get the new URL from the new tab
    new_url = driver.current_url

    # Do the assertion
    assert old_url != new_url, "URL didn't change after clicking the button"
    
def test_after_button_click_the_new_url_has_changed_to_what_is_required(driver, required_url_ending='/new-page'):
    old_window = driver.current_window_handle

    driver.find_element(By.XPATH, ".//div[@class='flex-center']/a").click()

    # Wait until a new window/tab is opened
    WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))

    # Get all window handles
    windows = driver.window_handles

    # Switch to the new tab (the one that's not the original)
    for window in windows:
        if window != old_window:
            driver.switch_to.window(window)
            break

    # Now get the new URL from the new tab
    new_url = driver.current_url

    # Do the assertion
    assert new_url.endswith(required_url_ending), "URL didn't change after clicking the button"

def test_text_on_the_new_page_is_what_is_required(driver, required_text='Welcome to the new page!'):
    old_window = driver.current_window_handle

    driver.find_element(By.XPATH, ".//div[@class='flex-center']/a").click()

    # Wait until a new window/tab is opened
    WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))

    # Get all window handles
    windows = driver.window_handles

    # Switch to the new tab (the one that's not the original)
    for window in windows:
        if window != old_window:
            driver.switch_to.window(window)
            break
    
    text = driver.find_element(By.TAG_NAME, 'h1').text

    assert text == required_text, 'Text on the new tab is not what is supposed to be there'

def test_button_has_target_attribute_with_right_assigned_parameter(driver, assigned_parameter='_blank'):
    button = driver.find_element(By.XPATH, ".//div[@class='flex-center']/a")

    target_value = button.get_attribute("target")

    assert target_value == assigned_parameter, f'Expected target={assigned_parameter}, but got {target_value}'

def test_button_opens_only_one_new_tab(driver):
    old_window = driver.current_window_handle

    driver.find_element(By.XPATH, ".//div[@class='flex-center']/a").click()

    WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 1)

    windows = driver.window_handles

    assert len(windows) == 2

def test_https_response_is_200():
    response = requests.get('https://qaplayground.dev/apps/new-tab/')

    assert response.status_code == 200   

def test_the_title_of_the_new_tab_is_what_is_expected(driver, expected_title='New Page'):
    old_window = driver.current_window_handle

    driver.find_element(By.XPATH, ".//div[@class='flex-center']/a").click()

    WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))

    windows = driver.window_handles

    for window in windows:
        if window != old_window:
            driver.switch_to.window(window)
            break

    WebDriverWait(driver, 10).until(EC.title_is(expected_title))
    assert driver.title == expected_title, f"Unexpected title: {driver.title}"