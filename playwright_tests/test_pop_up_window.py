import pytest
import requests
from playwright.sync_api import Page, BrowserContext, expect

BASE_URL = "https://qaplayground.dev/apps/popup/"
OPEN_BUTTON_XPATH = ".//div[@class='flex-center']/a"
POPUP_BUTTON_XPATH = ".//div/button"
MAIN_TEXT_XPATH = ".//div[@class='flex-center']/p"


@pytest.fixture(scope="function", autouse=True)
def go_to_main(page: Page):
    page.goto(BASE_URL)
    page.wait_for_selector(f"xpath={MAIN_TEXT_XPATH}")
    yield


def test_main_text_is_what_is_expected(page: Page, expected_text="Click to open pop-up"):
    text = page.locator(f"xpath={MAIN_TEXT_XPATH}").inner_text()
    assert text == expected_text, f"Real text is {text!r}, expected {expected_text!r}"


def test_open_button_is_clickable(page: Page):
    btn = page.locator(f"xpath={OPEN_BUTTON_XPATH}")
    expect(btn).to_be_visible()
    expect(btn).to_be_enabled()


def test_open_button_text_is_what_is_expected(page: Page, expected_text="OPEN"):
    text = page.locator(f"xpath={OPEN_BUTTON_XPATH}").inner_text()
    assert text == expected_text, f"Real text is {text!r}, expected {expected_text!r}"


def test_the_new_window_is_opened_as_separate_window(page: Page, context: BrowserContext):
    main_pages = context.pages
    with context.expect_page() as popup_info:
        page.click(f"xpath={OPEN_BUTTON_XPATH}")
    popup = popup_info.value

    assert len(context.pages) == len(main_pages) + 1

    main_size = page.viewport_size
    popup_size = popup.viewport_size
    assert popup_size["width"] <= main_size["width"], "Popup is wider than main window"


def test_submit_button_is_clickable_and_text(page: Page, context: BrowserContext):
    with context.expect_page() as popup_info:
        page.click(f"xpath={OPEN_BUTTON_XPATH}")
    popup = popup_info.value
    popup.wait_for_load_state()

    submit = popup.locator(f"xpath={POPUP_BUTTON_XPATH}")
    expect(submit).to_be_visible()
    expect(submit).to_be_enabled()

    text = submit.inner_text()
    assert text == "Submit", f"Real text is {text!r}, expected 'Submit'"


def test_submit_button_closes_the_pop_up_window(page: Page, context: BrowserContext):
    # open the popup
    with context.expect_page() as popup_info:
        page.click(f"xpath={OPEN_BUTTON_XPATH}")
    popup = popup_info.value
    popup.wait_for_load_state()

    # wait for it to close
    with popup.expect_event("close"):
        popup.click(f"xpath={POPUP_BUTTON_XPATH}")


def test_text_on_the_main_page_is_updated(page: Page, context: BrowserContext, expected_text='Button Clicked'):
    with context.expect_page() as popup_info:
        page.click(f"xpath={OPEN_BUTTON_XPATH}")
    popup = popup_info.value
    popup.wait_for_load_state()
    popup.click(f"xpath={POPUP_BUTTON_XPATH}")

    expect(page.locator(f"xpath={MAIN_TEXT_XPATH}")).to_have_text(expected_text)


def test_URL_of_the_main_page_is_changed_to_what_is_expected(page: Page, context: BrowserContext, expected_url_ending='/#'):
    with context.expect_page() as popup_info:
        page.click(f"xpath={OPEN_BUTTON_XPATH}")
    popup = popup_info.value
    popup.wait_for_load_state()
    popup.click(f"xpath={POPUP_BUTTON_XPATH}")

    assert page.url.endswith(expected_url_ending), f"Real URL is {page.url!r}, expected to end with {expected_url_ending!r}"


def test_URL_of_the_pop_up_page_is_changed_to_what_is_expected(page: Page, context: BrowserContext, expected_url_ending='/popup'):
    with context.expect_page() as popup_info:
        page.click(f"xpath={OPEN_BUTTON_XPATH}")
    popup = popup_info.value
    popup.wait_for_load_state()

    assert popup.url.endswith(expected_url_ending), f"Real URL is {popup.url!r}, expected to end with {expected_url_ending!r}"


def test_HTTPS_request_of_open_button_is_200():
    response = requests.get(BASE_URL)
    assert response.status_code == 200


def test_HTTPS_request_of_submit_button_is_200():
    response = requests.get(BASE_URL + "popup")
    assert response.status_code == 200