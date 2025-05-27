# URL = https://qaplayground.dev/apps/verify-account/
# In this task there's a code that has to be input in the confirmation fields
# Aim: Input code and get a "Success" window

# Steps:
# Read the code
# Divide code into numbers 
# Input code

import time

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options

BASE_URL = 'https://qaplayground.dev/apps/verify-account/'

@pytest.fixture
def driver():
    options = Options()
    options.add_argument('--start-maximized')
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()

def test_code_confirmation_shows_success_after_valid_code(driver):
    driver.get(BASE_URL)

    WebDriverWait(driver, 30).until(
        EC.visibility_of_element_located((By.CLASS_NAME, 'code-container'))
    )

    code = driver.find_element(By.TAG_NAME, 'small').text

    # Extract digits from the code
    code_digits = [char for char in code if char.isnumeric()]

    input_fields = driver.find_element(By.CLASS_NAME, 'code-container')\
                         .find_elements(By.TAG_NAME, 'input')

    for field, digit in zip(input_fields, code_digits):
        field.send_keys(digit)
    
    message = driver.find_element(By.TAG_NAME, 'small').text
    
    assert message == "Success", "Message shows not success"

