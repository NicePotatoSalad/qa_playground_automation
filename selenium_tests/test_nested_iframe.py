# URL = https://qaplayground.dev/apps/iframe/
# In this task there're 2 iframes - 1st level iframe and 2nd level iframe
# In the 2nd layer iframe there's a button "Click me"
# On click, text "Button Clicked" should appear, also in the 2nd layer iframe

# Goals:
# Cover the functionality of the website

# Test cases plan:
# 1. Text on the button is what is expected
# 2. Button is visible and clickable
# 3. Expected text is appeared after the click on the button
# 4. No duplicate texts are shown after repeated button clicks
# 5. First layer iiframe's HTTPS response is 2xx
# 6. Second layer iiframe's HTTPS response is 2xx
# 7. Iframe structure doesn't change
    # Iframe is not used that often, but it has its own purposes, more often than not, they are an important
    # part of the website and programmers can accidentally mess them up AND it will have consequences (even legal ones)
    # Thus, this text will catch if someone accidentally crushes the structure (unless intended to)

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import pytest
import requests
import time

from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

BASE_URL = "https://qaplayground.dev/apps/iframe/"
FIRST_IFRAME_XPATH = './/iframe[@src="iframe1.html"]'
SECOND_IFRAME_XPATH = './/iframe[@src="iframe2.html"]'

@pytest.fixture(params=["chrome", "firefox"])
def driver(request) -> webdriver.Chrome | webdriver.Firefox: # type: ignore
    browser = request.param

    if browser == "chrome":
        options = ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--headless")
        driver = webdriver.Chrome(options=options)

    elif browser == "firefox":
        options = FirefoxOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--headless")
        driver = webdriver.Firefox(options=options)

    else:
        raise Exception(f"Unsupported browser: {browser}")

    driver.get(BASE_URL)
    yield driver
    driver.quit()

# HELPER FUNCTIONS #

def switch_to_frame_by_xpath(driver, xpath, timeout=10):
    WebDriverWait(driver, timeout).until(
        EC.frame_to_be_available_and_switch_to_it((By.XPATH, xpath))
    )

def get_to_the_second_frame(driver, first_iframe_xpath=FIRST_IFRAME_XPATH, second_iframe_xpath=SECOND_IFRAME_XPATH):
    switch_to_frame_by_xpath(driver, first_iframe_xpath)
    switch_to_frame_by_xpath(driver, second_iframe_xpath)

# TESTS #

# 1. Text on the button is what is expected
def test_text_on_the_button_is_what_is_expected(driver, expected_text='CLICK ME'):
    driver.switch_to.default_content()

    get_to_the_second_frame(driver)

    button_text = driver.find_element(By.TAG_NAME, 'a').text

    assert button_text == expected_text, \
        f'The text on the button is {button_text}, but supposed to be {expected_text}'
    
# 2. Button is visible and clickable
def test_button_is_visible_and_clickable(driver):
    driver.switch_to.default_content()

    get_to_the_second_frame(driver)

    button = driver.find_element(By.TAG_NAME, 'a')

    assert button.is_displayed(), 'Button is not displayed'
    assert button.is_enabled(), 'Button is not clickable'

# 3. Expected text is appeared after the click on the button
def test_expected_text_is_appeared_after_clicking_the_button(driver):
    wait = WebDriverWait(driver, 10)

    driver.switch_to.default_content()

    get_to_the_second_frame(driver)

    driver.find_element(By.TAG_NAME, 'a').click()

    # Check that the new text is appeared
    try:
        wait.until(
            EC.presence_of_element_located((By.ID, 'msg'))
        )
    except TimeoutException:
        assert False, f"Notification text did not appear after clicking the button."

# 4. No duplicate texts are shown after repeated button clicks
def test_no_duplicate_texts_are_shown_after_clicking_the_button(driver):
    wait = WebDriverWait(driver, 10)

    driver.switch_to.default_content()

    get_to_the_second_frame(driver)

    driver.find_element(By.TAG_NAME, 'a').click()

    wait.until(
            EC.presence_of_element_located((By.ID, 'msg'))
        )
    
    texts = driver.find_elements(By.ID, 'msg')

    assert len(texts) == 1, 'There are more than 1 text'

# 5. First layer iframe's HTTPS response is 2xx
def test_https_response_of_first_layer_iframe_is_2xx():
    response = requests.get('https://qaplayground.dev/apps/iframe/iframe1')

    assert response.ok, "First layer iframe's response code is not 2xx"


# 6. Second layer iframe's HTTPS response is 2xx
def test_https_response_of_second_layer_iframe_is_2xx():
    response = requests.get('https://qaplayground.dev/apps/iframe/iframe2')

    assert response.ok, "Second layer iframe's response code is not 2xx"

# 7. Iframe structure doesn't change
def test_iframe_structure_does_not_change(driver):

    driver.switch_to.default_content()

    # Check iframe1 is present in main pagae
    iframe1 = driver.find_element(By.XPATH, '//iframe[@src="iframe1.html"]')
    assert iframe1.is_displayed(), "iframe1 is not visible or present"

    driver.switch_to.frame(iframe1)

    # Inside iframe1, check for iframe2
    iframe2 = driver.find_element(By.XPATH, '//iframe[@src="iframe2.html"]')
    assert iframe2.is_displayed(), "iframe2 is not visible or present inside iframe1"
