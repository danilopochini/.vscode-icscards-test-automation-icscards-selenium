from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage


class HomePage(BasePage):
    path = "/"

    def header_link_locator(self, name: str) -> tuple:
        return (By.XPATH, f"//header//a[normalize-space(.)='{name}']")

    def header_link(self, name: str) -> WebElement:
        return self.wait().until(EC.presence_of_element_located(self.header_link_locator(name)))

    def header_link_attribute(self, name: str, attribute: str) -> str:
        return self.attribute(self.header_link_locator(name), attribute)

    def main_heading_visible(self) -> bool:
        return self.is_displayed((By.CSS_SELECTOR, "h1"))

    def dialog_visible(self) -> bool:
        return self.is_displayed((By.CSS_SELECTOR, "dialog[open], [role='dialog']"))

    def click_header_link(self, name: str) -> None:
        self.click(self.header_link_locator(name))

    def main_heading(self) -> WebElement:
        return self.wait().until(EC.visibility_of_element_located((By.CSS_SELECTOR, "h1")))

    def click_open_menu(self) -> None:
        self.click((By.CSS_SELECTOR, "button[aria-label='Open menudialoog']"))

    def visible_dialog(self) -> WebElement:
        locator = (By.CSS_SELECTOR, "dialog[open], [role='dialog']")
        return self.wait().until(EC.visibility_of_element_located(locator))

    def internal_links(self) -> list[str]:
        return self.driver.execute_script(
            "return [...new Set([...document.querySelectorAll(\"a[href^='/']:not([href^='//'])\")]"
            ".map(e => e.getAttribute('href')))];"
        )
