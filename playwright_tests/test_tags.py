# URL = https://qaplayground.dev/apps/tags-input-box/
# In this task there's a field there you can create and remove tags
# There's also a button "remove all"
# Aim: Write test-cases and automate them

# Test cases plan:
# 1. After inputting text and pressing key "Enter", the tag is saved and is displayed
# 2. After clicking on "X" button near a tag, the tag is deleted
# 3. After clicking on "Remove all" button, all tags are removed

import pytest
from playwright.sync_api import Page, expect

BASE_URL = 'https://qaplayground.dev/apps/tags-input-box/'

@pytest.fixture(scope="function", autouse=True)
def visit_page(page: Page):
    page.goto(BASE_URL)
    page.wait_for_selector(".content")  # wait for the main content area to be visible

def test_tag_is_saved_and_displayed_after_entering_value(page: Page):
    # Count existing tags
    previous_tags = page.locator("li")
    previous_count = previous_tags.count()

    # Input a new tag and press Enter
    input_box = page.locator("input")
    input_box.fill("random")
    input_box.press("Enter")

    # Check that a new tag appeared
    new_count = page.locator("li").count()
    assert new_count == previous_count + 1, "New tag has not appeared"

def test_click_on_x_symbol_leads_to_removal_of_tag(page: Page):
    # Count tags before removal
    tags = page.locator("li")
    initial_count = tags.count()

    if initial_count == 0:
        # Add a tag if none exist to allow testing removal
        input_box = page.locator("input")
        input_box.fill("toRemove")
        input_box.press("Enter")
        initial_count = 1

    # Click the "X" icon on the first tag
    page.locator("li >> nth=0 >> i").click()

    # Verify the tag was removed
    final_count = page.locator("li").count()
    assert final_count == initial_count - 1, "Tag was not removed"

def test_click_on_remove_all_button_leads_to_removing_all_tags(page: Page):
    # Add multiple tags to ensure we have some to remove
    input_box = page.locator("input")
    for tag_text in ["tag1", "tag2", "tag3"]:
        input_box.fill(tag_text)
        input_box.press("Enter")

    # Click the "Remove all" button
    page.locator("button", has_text="Remove all").click()

    # Check that all tags are removed
    expect(page.locator("li")).to_have_count(0)
