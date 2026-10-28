from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

TIMEOUT = 15


class BasePage:
    path = "/"

    def __init__(self, driver: WebDriver, base_url: str):
        self.driver = driver
        self.base_url = base_url.rstrip("/")

    def wait(self, timeout: int = TIMEOUT) -> WebDriverWait:
        return WebDriverWait(self.driver, timeout)

    def open(self) -> None:
        self.driver.get(f"{self.base_url}{self.path}")
        self.dismiss_cookie_banner()

    def dismiss_cookie_banner(self) -> None:
        # CookieFirst renders the consent dialog asynchronously; it may not appear at all.
        try:
            self.wait(5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-cookiefirst-action='reject']"))
            ).click()
        except TimeoutException:
            pass

    def click(self, locator) -> None:
        # Re-find the element on each attempt; the page re-renders after load.
        def attempt(driver):
            try:
                driver.find_element(*locator).click()
                return True
            except (StaleElementReferenceException, ElementClickInterceptedException,
                    ElementNotInteractableException, NoSuchElementException):
                return False

        self.wait().until(attempt)

    def attribute(self, locator, name: str):
        def attempt(driver):
            try:
                return driver.find_element(*locator).get_attribute(name) or ""
            except (StaleElementReferenceException, NoSuchElementException):
                return False

        return self.wait().until(attempt)

    def is_displayed(self, locator) -> bool:
        def attempt(driver):
            try:
                return driver.find_element(*locator).is_displayed()
            except (StaleElementReferenceException, NoSuchElementException):
                return False

        return bool(self.wait().until(attempt))

    def set_viewport(self, width: int, height: int) -> None:
        # CDP emulation allows phone widths that a real desktop window cannot shrink to.
        self.driver.execute_cdp_cmd(
            "Emulation.setDeviceMetricsOverride",
            {"width": width, "height": height, "deviceScaleFactor": 1, "mobile": width < 600},
        )
