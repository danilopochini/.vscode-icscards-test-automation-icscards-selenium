import re

import requests
from behave import given, then, when
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


@given("I open the home page")
def step_open_home(context):
    context.home.open()


@given("the viewport is {width:d} by {height:d}")
def step_viewport(context, width, height):
    context.home.set_viewport(width, height)


@when('I click the "{name}" header link')
def step_click_header_link(context, name):
    context.home.click_header_link(name)


@when("I click the open menu button")
def step_click_menu(context):
    context.home.click_open_menu()


@then('the page title matches "{pattern}"')
def step_title(context, pattern):
    context.home.wait().until(lambda d: re.search(pattern, d.title))


@then('the canonical link is "{url}"')
def step_canonical(context, url):
    assert context.home.attribute((By.CSS_SELECTOR, "link[rel='canonical']"), "href") == url


@then('the meta description contains "{text}"')
def step_meta_description(context, text):
    assert text in context.home.attribute((By.CSS_SELECTOR, "meta[name='description']"), "content")


@then('the html language is "{lang}"')
def step_lang(context, lang):
    assert context.home.attribute((By.TAG_NAME, "html"), "lang") == lang


@then("the main heading is visible")
def step_heading(context):
    assert context.home.main_heading_visible()


@then('the "{name}" header link is the current page')
def step_link_current(context, name):
    assert context.home.header_link_attribute(name, "aria-current") == "page"


@then('the "{name}" header link points to "{href}"')
def step_link_href(context, name, href):
    assert context.home.header_link_attribute(name, "href").endswith(href)


@then('the url matches "{pattern}"')
def step_url(context, pattern):
    context.home.wait().until(lambda d: re.search(pattern, d.current_url))


@then("a dialog is visible")
def step_dialog(context):
    assert context.home.dialog_visible()


@then("the first {count:d} internal links respond without errors")
def step_links(context, count):
    hrefs = context.home.internal_links()
    assert hrefs, "expected internal links on the home page"
    failures = []
    for href in hrefs[:count]:
        response = requests.get(context.base_url + (href.split("#")[0] or "/"), timeout=30)
        if response.status_code >= 400:
            failures.append((href, response.status_code))
    assert not failures, f"Broken links: {failures}"
