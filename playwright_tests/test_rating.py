# URL = https://qaplayground.dev/apps/rating/
# In this task there's a form that contains 5 stars (inputs type='radio'), each of which is a button. The purpose is to give 
# a rating - amount of them shows user's satisfaction. Also there's a div that contains <li>'s with <img> of an emoji
# one star - angry emoji, 5 stars - happy one. Besides, there are 2 spans - one says "I absolutely hate it" if 1 star is set
# and "I love it" if 5 are => translates users decision onto the screen. The second span says "1 out of 5" if 1 star is set 
# therefore, showing how many stars are set in a number

# Goals:
# Cover the functionality of the website

# Test cases plan:
# 1. Button of a star is clickable
# 2. Correct emoji (<img src>) is shown
# 3. First span matches the expected one
# 4. Second span matches the expected one
# 5. Clicked button has attribute "checked"
# 6. There's a label for an input
# 7. An input (button) has an attribute "name"
# 8. No JS errors are shown
# 9. On page load, no stars are selected
# 10. User can not unselect the review once you clicked one the stars
# Repeat for all 5 stars-buttons

import pytest
from playwright.sync_api import Page, ConsoleMessage, expect

URL = "https://qaplayground.dev/apps/rating/"

EXPECTED_EMOJIS = [
    "emojis/emoji-1.png",
    "emojis/emoji-2.png",
    "emojis/emoji-3.png",
    "emojis/emoji-4.png",
    "emojis/emoji-5.png",
]

EXPECTED_TEXTS = [
    "I just hate it",
    "I don't like it",
    "This is awesome",
    "I just like it",
    "I just love it",
]

@pytest.fixture(autouse=True)
def go_to_app(page: Page):
    page.goto(URL)
    yield

@pytest.fixture(params=range(1, 6))
def star(request):
    return request.param

@pytest.fixture(autouse=True)
def collect_console_errors(page: Page):
    errors = []
    page.on("console", lambda msg: errors.append(msg) if msg.type == "error" else None)
    yield errors


def get_pseudo_element_text(page: Page, selector: str, pseudo: str = "::before") -> str:
    content = page.evaluate(
        """([selector, pseudo]) => {
            const el = document.querySelector(selector);
            if (!el) return "";
            return window.getComputedStyle(el, pseudo).getPropertyValue('content');
        }""",
        [selector, pseudo]
    )
    return content.strip('"')


# 1. Button of a star is clickable
def test_star_button_is_clickable(page: Page, star: int):
    label = page.locator(f"label[for='star-{star}']")
    label.click()  # will throw if not clickable

# 2. Correct emoji (<img src>) is shown
def test_correct_emoji_is_shown(page: Page, star: int):
    page.locator(f"label[for='star-{star}']").click()
    img = page.locator(f".emojis li:nth-of-type({star})")
    expect(img).to_be_visible()

# 3. First span matches the expected one
def test_feedback_text_matches(page: Page, star: int):
    page.locator(f"label[for='star-{star}']").click()
   
    content = get_pseudo_element_text(page, ".text")

    assert content == EXPECTED_TEXTS[star - 1], f'Expected "{EXPECTED_TEXTS[star - 1]}", got "{content}"'

# 4. Second span matches the expected one
def test_count_text_matches(page: Page, star: int):
    page.locator(f"label[for='star-{star}']").click()    

    content = get_pseudo_element_text(page, ".numb")

    assert content == f"{star} out of 5", f'Expected "{star}", got "{content}"'

# 5. Clicked button has attribute "checked"
def test_clicked_button_is_checked(page: Page, star: int):
    page.locator(f"label[for='star-{star}']").click()
    checked = page.locator(f"#star-{star}").is_checked()
    assert checked

# 6. There's a label for an input
def test_each_input_has_label(page: Page, star: int):
    label = page.locator(f"label[for='star-{star}']")
    expect(label).to_be_visible()

# 7. An input (button) has an attribute "name"
def test_input_has_name_attribute(page: Page, star: int):
    name = page.locator(f"#star-{star}").get_attribute("name")
    assert name == "rate"

# 8a. No JS errors are shown on load
def test_no_js_errors_on_load(collect_console_errors):
    assert not collect_console_errors, f"JS errors on load: {[m.text for m in collect_console_errors]}"

# 8b. No JS errors after click
def test_no_js_errors_after_click(page: Page, star: int, collect_console_errors):
    page.locator(f"label[for='star-{star}']").click()
    assert not collect_console_errors, f"JS errors after click: {[m.text for m in collect_console_errors]}"

# 9. On page load, no stars are selected
def test_no_stars_selected_on_load(page: Page):
    for i in range(1, 6):
        assert not page.locator(f"#star-{i}").is_checked()

# 10. User cannot unselect once clicked
def test_cannot_unselect_star(page: Page, star: int):
    label = page.locator(f"label[for='star-{star}']")
    label.click()
    assert page.locator(f"#star-{star}").is_checked()
    label.click()
    assert page.locator(f"#star-{star}").is_checked()

# 11. Initial feedback text matches
def test_feedback_text_matches_on_load(page: Page):
    content = get_pseudo_element_text(page, ".text")

    assert content == "Rate your experience"

# 12. Initial count text matches
def test_count_text_matches_on_load(page: Page, expected_text="0 out of 5"):
    content = get_pseudo_element_text(page, ".numb")

    assert content == expected_text