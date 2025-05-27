# URL = https://qaplayground.dev/apps/tags-input-box/
# In this task there's a field there you can create and remove tags
# There's also a button "remove all"
# Aim: Write test-cases and automate them

# Test cases plan:
# 1. After inputting text and pressing key "Enter", the tag is saved and is displayed
# 2. After clicking on "X" button near a tag, the tag is deleted
# 3. After clicking on "Remove all" button, all tags are removed

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options

BASE_URL = 'https://qaplayground.dev/apps/tags-input-box/'

@pytest.fixture
def driver():
    options = Options()
    options.add_argument('--start-maximized')
    driver = webdriver.Chrome(options=options)
    driver.get(BASE_URL)
    WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CLASS_NAME, 'content')))
    yield driver
    driver.quit()

def test_tag_is_saved_and_displayed_after_entering_value(driver):
    previous_amount_of_elements = len(driver.find_elements(By.TAG_NAME, "li"))

    driver.find_element(By.TAG_NAME, "input").send_keys("random" + Keys.ENTER)

    new_amount_of_elements = len(driver.find_elements(By.TAG_NAME, "li"))

    assert new_amount_of_elements == previous_amount_of_elements + 1, "New tag has not appeared"

def test_click_on_x_symbol_leads_to_removal_of_tag(driver):
    previous_amount_of_elements = len(driver.find_elements(By.TAG_NAME, "li"))

    driver.find_element(By.XPATH, "//li[1]/i").click()

    new_amount_of_elements = len(driver.find_elements(By.TAG_NAME, "li"))

    assert new_amount_of_elements == previous_amount_of_elements - 1, "New tag has not been removed"

def test_click_on_remove_all_button_leads_to_removing_all_tags(driver):
    driver.find_element(By.TAG_NAME, "button").click()

    new_amount_of_elements = len(driver.find_elements(By.TAG_NAME, "li"))

    assert new_amount_of_elements == 0, "Not every tag was removed"
