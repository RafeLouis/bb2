import logging

import config
from utils import get_chrome_webdriver, sign_in, save_games, load_page_and_run_func

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


def main() -> None:
    logger.info("App started successfully")
    driver = get_chrome_webdriver()
    try:
        load_page_and_run_func(driver=driver, page_url=config.SIGNIN_PAGE, func=sign_in)
        load_page_and_run_func(driver=driver, page_url=config.WORKING_PAGE, func=save_games)
    except Exception as e:
        logger.error("An error occurred: %s", e)
    else:
        logger.info("App completed successfully")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
