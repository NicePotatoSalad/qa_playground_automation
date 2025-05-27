# URL = https://qaplayground.dev/apps/popup/
# In this task there's a text and a button that leads to a pop-up window. 
# On the pop-up window there'a button "Submit" that closes the pop-up window. 
# After the closing the pop-up window, the text on the inital page is changed to "Button clicked"

# Test cases plan:
# 1. Text is what is expected
# 2. Button is clickable
# 3. Button's text is what is expected
# 4. The new window that's opened is in the separate window
# 5. Only one window is being opened
# 6. "Submit" button is clickable
# 7. "Submit" button text is what is expected
# 8. "Submit" button closes the pop-up window
# 9. Text on the main page is updated
# 10. URL of the main page is changed to the one that ends with "/#"
# 11. URL of the pop-up page is what is expected
# 12. HTTPS request of an open button is 200
# 13. HTTPS request of a submit button is 200


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
import pytest
import requests

from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

BASE_URL = "https://qaplayground.dev/apps/popup/"
OPEN_BUTTON_XPATH = ".//div[@class='flex-center']/a"
SUBMIT_BUTTON_XPATH = './/div/button'

@pytest.fixture(params=["chrome", "firefox"])
def driver(request):
    browser = request.param
    
    if browser == "chrome":
        options = ChromeOptions()
        options.add_argument("--start-maximized")
        driver = webdriver.Chrome(options=options)
    
    elif browser == "firefox":
        options = FirefoxOptions()
        options.add_argument("--start-maximized")
        driver = webdriver.Firefox(options=options)
    
    else:
        raise Exception(f"Unsupported browser: {browser}")

    driver.get("https://qaplayground.dev/apps/popup/")

    yield driver
    driver.quit()

# HELPER FUNCTIONS #

def click_open_popup(driver):
    driver.find_element(By.XPATH, OPEN_BUTTON_XPATH).click()

def wait_for_new_window(driver, wait, expected_count=2):
    wait.until(lambda d: len(d.window_handles) == expected_count)

def switch_to_new_window(driver, old_window):
    for window in driver.window_handles:
        if window != old_window:
            driver.switch_to.window(window)
            return window

def click_submit(driver, wait):
    wait.until(EC.element_to_be_clickable((By.XPATH, SUBMIT_BUTTON_XPATH)))
    driver.find_element(By.XPATH, SUBMIT_BUTTON_XPATH).click()

# TESTS #

def test_main_text_is_what_is_expected(driver, expected_text="Click to open pop-up"):
    text = driver.find_element(By.XPATH, ".//div[@class='flex-center']/p").text

    assert text == expected_text, f'Real text is {text}, while has to be {expected_text}'

def test_open_button_is_clickable(driver):
    wait = WebDriverWait(driver, 10)

    wait.until(EC.element_to_be_clickable((By.XPATH, OPEN_BUTTON_XPATH)))
    wait.until(EC.visibility_of_element_located((By.XPATH, OPEN_BUTTON_XPATH)))

    button = driver.find_element(By.XPATH, OPEN_BUTTON_XPATH)

    assert button.is_displayed(), 'Button is not displayed'
    assert button.is_enabled(), 'Button is not clickable'

def test_open_button_text_is_what_is_expected(driver, expected_text="OPEN"):
    text = driver.find_element(By.XPATH, OPEN_BUTTON_XPATH).text

    assert text == expected_text, f'Real text is {text}, while has to be {expected_text}'

def test_the_new_window_is_opened_as_separate_window(driver):
    # Click the button
    # Wait till the new window appears
    # Switch to a new window
    # Check that its actually a separate window
    wait = WebDriverWait(driver, 10)
    old_window = driver.current_window_handle

    click_open_popup(driver)

    wait_for_new_window(driver, wait, 2)

    switch_to_new_window(driver, old_window)

    size = driver.get_window_size()

    assert size['width'] <= 800, 'The new opened window is likely not a pop-up'

def test_no_duplicate_windows_are_opened(driver):

    click_open_popup(driver)

    WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 1)

    windows = driver.window_handles

    assert len(windows) == 2, 'Duplicate windows have been opened'

def test_submit_button_is_clickable(driver):
    wait = WebDriverWait(driver, 10)
    old_window = driver.current_window_handle
    
    click_open_popup(driver)

    wait_for_new_window(driver, wait, 2)

    switch_to_new_window(driver, old_window)

    wait.until(EC.element_to_be_clickable((By.XPATH, SUBMIT_BUTTON_XPATH)))
    wait.until(EC.visibility_of_element_located((By.XPATH, SUBMIT_BUTTON_XPATH)))

    button = driver.find_element(By.XPATH, SUBMIT_BUTTON_XPATH)

    assert button.is_displayed(), 'Button is not displayed'
    assert button.is_enabled(), 'Button is not clickable'

def test_submit_button_text_is_what_is_expected(driver, expected_text="Submit"):
    wait = WebDriverWait(driver, 10)
    old_window = driver.current_window_handle
    
    click_open_popup(driver)

    wait_for_new_window(driver, wait, 2)

    switch_to_new_window(driver, old_window)

    text = driver.find_element(By.XPATH, SUBMIT_BUTTON_XPATH).text

    assert text == expected_text, f'Real text is {text}, while has to be {expected_text}'

def test_submit_button_closes_the_pop_up_window(driver):
    wait = WebDriverWait(driver, 10)

    # Assigning variables for the old page to use later
    old_window = driver.current_window_handle
    
    click_open_popup(driver)

    wait_for_new_window(driver, wait, 2)

    # Get new variable for the list of windows
    new_windows = driver.window_handles

    switch_to_new_window(driver, old_window)

    click_submit(driver, wait)

    wait_for_new_window(driver, wait, 1)

    # Check that amount of windows is new amount minus 1
    assert len(driver.window_handles) == len(new_windows) - 1, 'Window was not closed'

# 9. Text on the main page is updated
def test_text_on_the_main_page_is_what_is_expected(driver, expected_text='Button Clicked'):
    wait = WebDriverWait(driver, 10)

    # Assigning variables for the old page to use later
    old_window = driver.current_window_handle
    
    click_open_popup(driver)

    wait_for_new_window(driver, wait, 2)

    switch_to_new_window(driver, old_window)

    # Assign variables of the pop-up window
    new_window = driver.current_window_handle

    click_submit(driver, wait)

    wait_for_new_window(driver, wait, 1)

    # Switch back to the original window
    switch_to_new_window(driver, new_window)

    # Check the text
    text = driver.find_element(By.XPATH, ".//div[@class='flex-center']/p").text

    assert text == expected_text, f'Real text is {text}, while has to be {expected_text}'

# 10. URL of the main page is changed to the one that ends with "/#"
def test_URL_of_the_main_page_is_changed_to_what_is_expected(driver, expected_url_ending='/#'):
    wait = WebDriverWait(driver, 10)

    original_url = driver.current_url

    click_open_popup(driver)

    wait_for_new_window(driver, wait, 2)

    assert driver.current_url.endswith(expected_url_ending), (
        f"Real URL is {driver.current_url}, "
        f"but has to be {original_url + expected_url_ending}"
    )

# 11. URL of the pop-up page is what is expected
def test_URL_of_the_pop_up_page_is_changed_to_what_is_expected(driver, expected_url_ending='/popup'):
    wait = WebDriverWait(driver, 10)
    
    old_window = driver.current_window_handle
    original_url = driver.current_url

    click_open_popup(driver)

    wait_for_new_window(driver, wait, 2)

    windows = driver.window_handles
    
    switch_to_new_window(driver, old_window)
        
    real_url = driver.current_url
    
    assert real_url.endswith(expected_url_ending), (
        f"Real URL is {real_url}, "
        f"but has to be {original_url + expected_url_ending}"
    )

# 12. HTTPS request of an open button is 200
def test_HTTPS_request_of_open_button_is_200():
    response = requests.get('https://qaplayground.dev/apps/popup/')

    assert response.status_code == 200  

# 13. HTTPS request of a submit button is 200
def test_HTTPS_request_of_submit_button_is_200():
    response = requests.get('https://qaplayground.dev/apps/popup/popup')

    assert response.status_code == 200
