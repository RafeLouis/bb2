import os

SIGNIN_PAGE = os.getenv("SIGNIN_PAGE", '')
WORKING_PAGE = os.getenv("WORKING_PAGE", '')

CARD_SELECTOR = os.getenv("CARD_SELECTOR", "swiper-container")
OPTIONS_BUTTON_SELECTOR = os.getenv("OPTIONS_BUTTON_SELECTOR", "")
SAVE_BUTTON_SELECTOR = os.getenv("SAVE_BUTTON_SELECTOR", "")
DUPLICATE_TEXT_ALERT = os.getenv("DUPLICATE_TEXT_ALERT", "")
CARD_ID_SELECTOR = os.getenv("CARD_ID_SELECTOR", "div[data-evresult-target='gid']")
CARD_ID_ATTR = os.getenv("CARD_ID_ATTRIBUTE", 'data-metrics')

LOGIN_FIELD_SELECTOR = os.getenv("LOGIN_FIELD_SELECTOR")
PASSWORD_FIELD_SELECTOR = os.getenv("PASSWORD_FIELD_SELECTOR")

LOGIN = os.getenv("LOGIN")
PASSWORD = os.getenv("PASSWORD")

CLICK_DELAY = float(os.getenv("CLICK_DELAY", 1.0))
