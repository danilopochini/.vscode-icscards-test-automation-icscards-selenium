import time
from pathlib import Path

from selenium import webdriver

from pages.home_page import HomePage
from report_builder import Report


def _create_driver(userdata):
    browser = userdata.get("browser", "chrome").lower()
    headless = userdata.getbool("headless", False)
    if browser == "edge":
        options = webdriver.EdgeOptions()
        driver_cls = webdriver.Edge
    else:
        options = webdriver.ChromeOptions()
        driver_cls = webdriver.Chrome
    options.add_argument("--lang=nl-NL")
    options.add_argument("--window-size=1440,900")
    options.add_experimental_option("prefs", {"intl.accept_languages": "nl-NL,nl"})
    if headless:
        options.add_argument("--headless=new")
    return driver_cls(options=options)


def before_all(context):
    context.base_url = context.config.userdata.get("base_url", "https://www.icscards.nl")
    context.slowmo = float(context.config.userdata.get("slowmo", 0))
    context.report = Report()


def before_scenario(context, scenario):
    context.driver = _create_driver(context.config.userdata)
    context.driver.execute_cdp_cmd("Emulation.setTimezoneOverride", {"timezoneId": "Europe/Amsterdam"})
    context.home = HomePage(context.driver, context.base_url)
    context.report.start_scenario(scenario)


def after_step(context, step):
    try:
        shot = context.driver.get_screenshot_as_base64()
    except Exception:
        shot = ""
    context.report.add_step(step, shot)
    if context.slowmo:
        time.sleep(context.slowmo)


def after_scenario(context, scenario):
    context.report.end_scenario(scenario)
    context.driver.quit()


def after_all(context):
    context.report.write(Path("report.html"))
