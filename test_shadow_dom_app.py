# URL = https://qaplayground.dev/apps/shadow-dom/
# In this task there is a Shadow DOM element <progress-bar>, that contains 2 divs:
# 1. A button "Boost" & 2. A progress bar itself
# On button click, progress bar gets filled to 95% after some animation.

# Goals:
# Cover the functionality of the website

# Test cases plan:
# Basic UI
# 1. Text on the button is what is expected
# 2. Button is visible and clickable
# 3. Keyboard accessibility: button can be accessed through the keyboard
# Shadow DOM Structure
# 4. Structure - required elements inside shadow DOM exist
# 5. Shadow DOM is open
# 6. Style encapsulation: CSS scripts do not affect the shadow dom element
# Behavior
# 7. On a button click, progress bar gets filled to 95%
# 8. Initially progress bar is filled on 5%
# 9. On multiple button clicks, progress bar stays at 95%
# Other
# 10. Crazy test: Page is still usable if Shadow DOM fails to load (graceful degradation)

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
import pytest
import time

from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

BASE_URL = "https://qaplayground.dev/apps/shadow-dom/"

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

# HELPER FUNCTION #
def get_the_button(driver):
    # Step 1: get the shadow host
    shadow_host = driver.find_element(By.CSS_SELECTOR, "progress-bar")

    # Step 2: use JavaScript to get the shadow root
    shadow_root = driver.execute_script("return arguments[0].shadowRoot", shadow_host)

    # Step 3: find elements inside the shadow DOM
    boost_button = shadow_root.find_element(By.CSS_SELECTOR, "button")

    return boost_button


# TESTS #
# 1. Text on the button is what is expected
def test_button_text_is_what_is_expected(driver, expected_text='BOOST 🚀'):
    button_text = get_the_button(driver).text

    assert button_text == expected_text, \
        f'The text on the button is {button_text}, but supposed to be {expected_text}'
    
# 2. Button is visible and clickable
def test_button_is_visible_and_clickable(driver):
    button = get_the_button(driver)

    assert button.is_displayed(), 'Button is not displayed'
    assert button.is_enabled(), 'Button is not clickable'

# 3. Keyboard accessibility: button can be accessed through the keyboard
def test_button_can_be_accessed_through_keyboard(driver, max_tabs=30):
    # Focus on the body
    driver.find_element(By.TAG_NAME, "body").click()

    # Shadow host and JS setup
    shadow_host = driver.find_element(By.CSS_SELECTOR, "progress-bar")

    for _ in range(max_tabs):
        ActionChains(driver).send_keys(Keys.TAB).perform()
        time.sleep(0.1)

        focused_element = driver.execute_script("return arguments[0].shadowRoot.activeElement", shadow_host)
        if focused_element and focused_element.tag_name == 'buttons':
            break
    else:
        # If we tabbed max_tabs times and still no button, fail
        raise AssertionError("Boost button was not focusable by keyboard (Tab).")
    
# 4. Structure - required elements inside shadow DOM exist
def test_required_elements_inside_shadow_dom_exist(driver, divs_number=2, style_number=1):

    shadow_host = driver.find_element(By.CSS_SELECTOR, "progress-bar")

    shadow_root = driver.execute_script("return arguments[0].shadowRoot", shadow_host)

    div_tags = driver.execute_script("""
        return Array.from(arguments[0].shadowRoot.children).filter(e => e.tagName === 'DIV');
    """, shadow_host)

    assert len(div_tags) == divs_number, f'Number of div tags is {len(div_tags)}, but supposed to be {divs_number}'

    style_tags = driver.execute_script("""
        return Array.from(arguments[0].shadowRoot.children).filter(e => e.tagName === 'STYLE');
    """, shadow_host)

    assert len(style_tags) == style_number, f'Number of style tags is {len(style_tags)}, but supposed to be {style_number}'

# 5. Shadow DOM is open
def test_shadow_dom_element_is_open(driver):
    shadow_host = driver.find_element(By.CSS_SELECTOR, "progress-bar")
    shadow_root = driver.execute_script("return arguments[0].shadowRoot", shadow_host)

    assert shadow_root is not None, "Shadow DOM is closed (cannot access it)"

# 6. Style encapsulation: CSS scripts do not affect the shadow dom element
def test_external_styles_do_not_affect_shadow_DOM_content(driver):
    # Get button inside shadow DOM
    button = get_the_button(driver)

    original_color = driver.execute_script("return getComputedStyle(arguments[0]).color", button)
    print(original_color)
    
    # Inject global CSS into the main document
    driver.execute_script("""
        const style = document.createElement('style');
        style.textContent = 'button { color: blue !important; }';
        document.head.appendChild(style);
    """)

    # Read its computed style
    new_color = driver.execute_script("return getComputedStyle(arguments[0]).color", button)

    assert new_color == original_color, "External CSS leaked into shadow DOM!"

# 7. On a button click, progress bar gets filled to 95%
def test_progress_bar_gets_filled_to_95_percents_after_button_click(driver):
    get_the_button(driver).click()

    progress_bar = driver.find_element(By.CSS_SELECTOR, 'progress-bar')

    time.sleep(10) # wait for the animation

    percents_amount = progress_bar.get_attribute('percent')

    assert percents_amount == '95'

# 8. Initially progress bar is filled on 5%
def test_progress_bar_is_initally_filled_on_5_percents(driver):
    progress_bar = driver.find_element(By.CSS_SELECTOR, 'progress-bar')
    percents_amount = progress_bar.get_attribute('percent')

    assert percents_amount == '5'

# 9. On multiple button clicks, progress bar stays at 95%
def test_progress_bar_stays_at_95_percents_after_multiple_button_clicks(driver):
    progress_bar = driver.find_element(By.CSS_SELECTOR, 'progress-bar')

    button = get_the_button(driver)
    
    button.click()
    time.sleep(2) # wait for some time
    button.click()
    button.click()
    time.sleep(2)
    button.click()
    time.sleep(4)
    button.click()

    time.sleep(2)

    percents_amount = progress_bar.get_attribute('percent')

    assert percents_amount == '95'

# 10. Crazy test: Page is still usable if Shadow DOM fails to load (graceful degradation)
def test_page_is_usable_if_shadow_dom_fails_to_load(driver):
    driver.execute_script("""
        const host = document.querySelector('progress-bar');
        if (host && host.shadowRoot) {
            host.shadowRoot.innerHTML = '';  // Simulate failure
        }
    """)

    assert driver.find_element(By.TAG_NAME, "main").is_displayed()

    # there could be more but fallback messages and logs are not designed for this app

