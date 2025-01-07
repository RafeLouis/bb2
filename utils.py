import logging
import time
from collections.abc import Callable

from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException

import config
from exceptions import SignInError, NoSignInCredentialsError, NoSignInFieldsError, HTMLElementNotFoundError, \
    FormNotFilledError, URLNotPassedError

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


def load_page_and_run_func(driver: WebDriver, page_url: str, func: Callable) -> None:
    if not page_url:
        raise URLNotPassedError(f"Page url for {func.__name__} function not provided")
    load_page(driver, page_url)
    func(driver)


def click_element(driver: WebDriver, element: WebElement, delay: float = 1.0) -> None:
    try:
        if not element.is_displayed():
            driver.execute_script("arguments[0].scrollIntoView(true);", element)

        try:
            ActionChains(driver).move_to_element(element).click().perform()
        except Exception as e:
            logger.warning("ActionChains failed, falling back to JavaScript: %s", e)
            driver.execute_script("arguments[0].click();", element)

        time.sleep(delay)
        logger.debug("Element %s was clicked", element)

    except Exception as e:
        logger.exception("Failed to click element: %s", e)


def check_duplicates(game_element: WebElement, unique_ids: set[str]) -> bool:
    is_duplicate_badge = game_element.find_elements(By.XPATH, f".//p[text()='{config.DUPLICATE_TEXT_ALERT}']")

    try:
        game_id = game_element.find_element(By.CSS_SELECTOR, config.CARD_ID_SELECTOR).get_attribute(config.CARD_ID_ATTR)
    except NoSuchElementException as e:
        logger.warning("Unable to find element in game card: %s\n%s", game_element, e)
        return True

    logger.info("Game ID: %s", game_id)

    if not game_id:
        logger.warning("Unable to find Game ID for game card")
        return True

    if is_duplicate_badge:
        logger.debug("Game ID: %s skipped because of a duplicate badge", game_id)
        return True

    if game_id in unique_ids:
        logger.debug("Game ID: %s skipped because of duplicate", game_id)
        return True

    unique_ids.add(game_id)
    logger.debug("Duplicates not found for Game ID: %s", game_id)
    return False


def find_and_click_on_element(driver: WebDriver, selector: str, area: WebElement | None = None) -> None:
    if area:
        element = area.find_element(By.CSS_SELECTOR, selector)
    else:
        element = driver.find_element(By.CSS_SELECTOR, selector)
    logger.debug("Element found: %s", element)

    click_element(driver, element, config.CLICK_DELAY)


def save_games(driver: WebDriver) -> None:
    game_elements = driver.find_elements(By.CSS_SELECTOR, f"[id*='{config.CARD_SELECTOR}']")
    games_amount = len(game_elements or "")
    logger.info("Games found: %s", games_amount)

    saved_games_counter = skipped_games_counter = 0
    unique_game_ids: set[str] = set()

    for game_element in game_elements:
        if check_duplicates(game_element, unique_game_ids):
            logger.info("Game skipped")
            skipped_games_counter += 1
            continue

        try:
            find_and_click_on_element(driver=driver, selector=config.OPTIONS_BUTTON_SELECTOR, area=game_element)
            find_and_click_on_element(driver=driver, selector=config.SAVE_BUTTON_SELECTOR, area=game_element)
        except NoSuchElementException as e:
            logger.exception("Unable to find element in game card: %s\n%s", game_element, e)
        else:
            saved_games_counter += 1
            logger.info("Game saved")

    logger.info("Games handled: %s (saved: %s, skipped: %s)",
                games_amount, saved_games_counter, skipped_games_counter)


def sign_in(driver: WebDriver) -> None:
    if not (config.LOGIN_FIELD_SELECTOR and config.PASSWORD_FIELD_SELECTOR):
        raise NoSignInFieldsError("Credential fields haven't been found")

    try:
        url_before_signin = driver.current_url
        login_field = driver.find_element(By.ID, config.LOGIN_FIELD_SELECTOR)
        password_field = driver.find_element(By.ID, config.PASSWORD_FIELD_SELECTOR)
    except Exception as e:
        raise HTMLElementNotFoundError("HTML Element not found: %s", e)

    if not (config.LOGIN and config.PASSWORD):
        raise NoSignInCredentialsError("No sign in credentials")

    try:
        login_field.send_keys(config.LOGIN)
        password_field.send_keys(config.PASSWORD)
        password_field.send_keys(Keys.RETURN)
    except Exception as e:
        raise FormNotFilledError("Form not filled: %s", e)

    if url_before_signin == driver.current_url:
        raise SignInError("Unsuccessful attempt to sign in!")

    logger.info("Signed in successfully")
    time.sleep(1)


def load_page(driver: WebDriver, page: str) -> None:
    driver.get(page)
    driver.implicitly_wait(10)
    logger.info("Page '%s' loaded", driver.current_url)


def get_chrome_webdriver() -> WebDriver:
    chrome_options = ChromeOptions()
    chrome_options.add_argument("--headless")
    return webdriver.Chrome(options=chrome_options)
