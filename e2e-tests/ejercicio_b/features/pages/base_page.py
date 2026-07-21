"""
BasePage: clase padre para todos los Page Objects.
Centraliza acciones genéricas de Playwright (click, fill, texto, screenshot)
para que las páginas concretas no repitan código ni conozcan detalles
de bajo nivel de Playwright.
"""


class BasePage:
    def __init__(self, page):
        self.page = page

    def goto(self, url: str):
        self.page.goto(url)

    def click(self, selector: str):
        self.page.click(selector)

    def fill(self, selector: str, text: str):
        self.page.fill(selector, text)

    def press(self, selector: str, key: str):
        self.page.press(selector, key)

    def get_text(self, selector: str) -> str:
        return self.page.inner_text(selector)

    def is_visible(self, selector: str) -> bool:
        return self.page.is_visible(selector)

    def take_screenshot(self, path: str):
        self.page.screenshot(path=path, full_page=True)