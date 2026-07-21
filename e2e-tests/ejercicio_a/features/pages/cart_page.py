from features.pages.base_page import BasePage

CART_URL = "https://www.geant.com.uy/cart"


class CartPage(BasePage):
    CART_ITEMS = "//*[contains(@class,'cart-item') or contains(@class,'cart-line') or contains(@class,'product-item')]"
    ITEM_NAME = "xpath=.//*[contains(@class,'prod-desc') or contains(@class,'name') or contains(@class,'title')]//a | .//*[contains(@class,'prod-desc') or contains(@class,'name') or contains(@class,'title')]"
    ITEM_PRICE = "xpath=.//*[contains(@class,'product-prices') or contains(@class,'price')]//span[contains(@class,'val')]"

    CART_TOTAL = "//*[contains(@class,'total') and (contains(@class,'cart') or contains(@class,'resume') or contains(@class,'summary'))]//span[contains(@class,'val')]"

    def wait_for_cart_loaded(self, timeout=30000):
        self.page.wait_for_selector(self.CART_ITEMS, timeout=timeout)

    def get_cart_items(self):
        """Returns a list of {"name": str, "price": float} for every product in the cart."""
        self.dismiss_overlay_if_present()
        rows = self.page.locator(self.CART_ITEMS)
        results = []
        for i in range(rows.count()):
            row = rows.nth(i)
            name = row.locator(self.ITEM_NAME).first.inner_text().strip()
            price_text = row.locator(self.ITEM_PRICE).first.inner_text()
            price = float(price_text.replace(".", "").replace(",", ".").strip())
            results.append({"name": name, "price": price})
        return results

    def get_total(self):
        total_text = self.page.locator(self.CART_TOTAL).first.inner_text()
        return float(total_text.replace(".", "").replace(",", ".").strip())
