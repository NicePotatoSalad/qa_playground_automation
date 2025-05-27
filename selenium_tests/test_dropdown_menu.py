# URL = https://qaplayground.dev/apps/multi-level-dropdown/
# In this task there's a menu, one bar of which is a dropdown menu with more layers
# Aim: Test all elements of the dropdown menu without overloading the code

# Test cases plan:
# 1. Every element of the dropdown menu is clickable

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
import time
import pytest

BASE_URL = 'https://qaplayground.dev/apps/multi-level-dropdown/' # URL of the page with the task on QA playground

# This sets up the browser. It opens the site before the tests start and closes it after all are done.
@pytest.fixture
def driver():
    options = Options()
    options.add_argument("--start-maximized")  

    driver = webdriver.Chrome(options=options)  
    driver.get(BASE_URL)
    yield driver
    driver.quit()

def open_dropdown_and_click(driver, first_index, second_index=None):
    # Open nav
    nav = driver.find_element(By.XPATH, ".//ul/li[last()]")
    nav.click()
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, ".//div[@class='dropdown']"))
    )
    time.sleep(0.5) # Wait for the animation

    # First layer (e.g. "Profile", "My Tutorials", "Animals")
    first_button = driver.find_element(By.XPATH, f".//div[@class='menu']/a[{first_index}]")
    first_button.click()

    # Second layer (if there is one)
    if second_index is not None:
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, ".//div[@class='dropdown']"))
        )
        time.sleep(0.5) # Wait for the animation

        second_button = driver.find_element(By.XPATH, f".//div[@class='dropdown']/div/a[{second_index}]")
        driver.execute_script("arguments[0].scrollIntoView(true);", second_button)
        second_button.click()
        # time.sleep(1) # Wait for the link

def test_dropdownmenu_profile_button_is_clickable(driver):
    open_dropdown_and_click(driver, first_index=1, second_index=None)

    # Check that something happened (page changed, element appeared, etc)
    assert driver.current_url.endswith("#undefined")

def test_dropdownmenu_MyTutorialBack_button_is_clickable(driver):
    open_dropdown_and_click(driver, first_index=2, second_index=1)
    assert driver.current_url.endswith("#main")

def test_dropdownmenu_HTML_button_is_clickable(driver):
    open_dropdown_and_click(driver, first_index=2, second_index=2)

    assert driver.current_url.endswith("#!HTML")

def test_dropdownmenu_CSS_button_is_clickable(driver):
    open_dropdown_and_click(driver, first_index=2, second_index=3)

    assert driver.current_url.endswith("#!CSS")

def test_dropdownmenu_JavaScript_button_is_clickable(driver):
    open_dropdown_and_click(driver, first_index=2, second_index=4)
    assert driver.current_url.endswith("#!JavaScript")


# Supposed to come out FAILED since footer's infobox is covering the button -- Bug
def test_dropdownmenu_Awesome_button_is_clickable(driver):
    open_dropdown_and_click(driver, first_index=2, second_index=5)

    assert driver.current_url.endswith("#!Awesome")

def test_dropdownmenu_AnimalsBack_button_is_clickable(driver):
    open_dropdown_and_click(driver, first_index=3, second_index=1)

    assert driver.current_url.endswith("#main")

def test_dropdownmenu_Kangaroo_button_is_clickable(driver):
    open_dropdown_and_click(driver, first_index=3, second_index=2)

    assert driver.current_url.endswith("#!Kangaroo")

def test_dropdownmenu_Frog_button_is_clickable(driver):
    open_dropdown_and_click(driver, first_index=3, second_index=3)

    assert driver.current_url.endswith("#!Frog")

def test_dropdownmenu_Horse_button_is_clickable(driver):
    open_dropdown_and_click(driver, first_index=3, second_index=4)

    assert driver.current_url.endswith("#!Horse")

# Supposed to come out as FAILED since footer inbox-message is covering the button -- Bug
def test_dropdownmenu_Hedgehod_button_is_clickable(driver):
    open_dropdown_and_click(driver, first_index=3, second_index=5)

    assert driver.current_url.endswith("#!Hedgehod")