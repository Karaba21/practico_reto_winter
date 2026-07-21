import re

from features.pages.base_page import BasePage

BASE_URL = "https://www.geant.com.uy/"


class HomePage(BasePage):
    SEARCH_INPUT = "//input[@id='InputSearch']"
    SEARCH_BUTTON = "//button[contains(@class,'search-button')]"
    PRODUCT_ITEMS = "//div[contains(@class,'products-grid-list')]//div[contains(@class,'product-item')]"
    PRODUCT_NAME = "xpath=.//div[contains(@class,'prod-desc')]//h3/a"
    PRODUCT_PRICE = "xpath=.//div[contains(@class,'product-prices')]//span[@class='val']"
    ADD_TO_CART_BUTTON = "xpath=.//div[contains(@class,'widget-add-to-cart')]//button[contains(@class,'atc-button')]"
    CART_LINK = "//a[@href='cart']"

    def open(self):
        self.page.goto(BASE_URL, wait_until="networkidle", timeout=60000)

    def search(self, term, retries=3):
        """Fills the search box and presses Enter. The site is an SPA
        (Blazor Server) that occasionally swallows the first Enter press or
        leaves stale results from a previous search in the DOM, so the
        action is retried until the URL actually reflects the new keyword
        and the results grid renders."""
        self.dismiss_overlay_if_present(timeout=1000)
        last_error = None
        for _ in range(retries):
            search_input = self.page.locator(self.SEARCH_INPUT)
            search_input.click()
            search_input.fill(term)
            search_input.press("Enter")
            try:
                self.page.wait_for_url(re.compile(re.escape(term), re.IGNORECASE), timeout=10000)
                self.page.wait_for_selector(self.PRODUCT_ITEMS, timeout=10000)
                return
            except Exception as error:
                last_error = error
        raise TimeoutError(
            f"No se encontraron resultados para '{term}' tras {retries} intentos"
        ) from last_error

    def _first_result(self):
        return self.page.locator(self.PRODUCT_ITEMS).first

    def get_first_result_name(self):
        return self._first_result().locator(self.PRODUCT_NAME).inner_text().strip()

    def get_first_result_price(self):
        raw = self._first_result().locator(self.PRODUCT_PRICE).inner_text()
        return float(raw.replace(".", "").replace(",", ".").strip())

    def add_first_result_to_cart(self):
        """Adds the first product of the current search results to the cart
        and returns its (name, price) for later validation."""
        name = self.get_first_result_name()
        price = self.get_first_result_price()
        self._first_result().locator(self.ADD_TO_CART_BUTTON).click()
        self.dismiss_overlay_if_present()
        return name, price

    def go_to_cart(self):
        self.page.locator(self.CART_LINK).first.click()
        self.page.wait_for_load_state("networkidle", timeout=60000)
