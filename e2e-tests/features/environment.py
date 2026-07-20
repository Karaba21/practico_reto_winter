import os
from playwright.sync_api import sync_playwright

HEADLESS = os.getenv("HEADLESS", "true").lower() != "false"
SCREENSHOTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "screenshots")


def before_all(context):
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    context.playwright = sync_playwright().start()
    context.browser = context.playwright.chromium.launch(headless=HEADLESS)


def after_all(context):
    context.browser.close()
    context.playwright.stop()


def before_scenario(context, scenario):
    context.browser_context = context.browser.new_context()
    context.page = context.browser_context.new_page()


def after_scenario(context, scenario):
    if scenario.status == "failed":
        safe_name = scenario.name.replace(" ", "_")
        context.page.screenshot(
            path=os.path.join(SCREENSHOTS_DIR, f"FAILED_{safe_name}.png"),
            full_page=True,
        )
    context.page.close()
    context.browser_context.close()
