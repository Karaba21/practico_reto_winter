"""
Hooks de Behave: se ejecutan automáticamente antes/después de cada escenario.
Acá se levanta y se cierra el navegador de Playwright, para que los steps
no tengan que preocuparse por esto.
"""

from playwright.sync_api import sync_playwright


def before_all(context):
    context.playwright = sync_playwright().start()
    context.browser = context.playwright.chromium.launch(headless=True)


def before_scenario(context, scenario):
    context.browser_context = context.browser.new_context()
    context.page = context.browser_context.new_page()


def after_scenario(context, scenario):
    context.browser_context.close()


def after_all(context):
    context.browser.close()
    context.playwright.stop()