class BasePage:
    OVERLAY_DIALOG = "//div[contains(@class,'rz-dialog-wrapper')]"
    OVERLAY_CLOSE_BUTTON = "xpath=.//*[contains(@class,'rz-dialog-titlebar-close') or contains(@class,'rz-dialog-titlebar-icon') or contains(@class,'close')]"

    def __init__(self, page):
        self.page = page

    def take_screenshot(self, path, full_page=True):
        self.page.screenshot(path=path, full_page=full_page)

    def wait_for_idle(self, timeout=30000):
        self.page.wait_for_load_state("networkidle", timeout=timeout)

    def dismiss_overlay_if_present(self, timeout=3000):
        """Handles the confirmation dialog (Radzen 'rz-dialog-wrapper') that
        the site shows after adding a product to the cart, if it appears.
        It is given a chance to auto-dismiss first (it is a transient
        confirmation toast, not a blocking form) before forcing it closed,
        so we never risk clicking a "cancel" action on it."""
        dialog = self.page.locator(self.OVERLAY_DIALOG)
        try:
            dialog.first.wait_for(state="visible", timeout=timeout)
        except Exception:
            return
        try:
            dialog.first.wait_for(state="hidden", timeout=4000)
            return
        except Exception:
            pass
        close_button = dialog.first.locator(self.OVERLAY_CLOSE_BUTTON)
        if close_button.count() > 0:
            close_button.first.click()
        else:
            self.page.keyboard.press("Escape")
        dialog.first.wait_for(state="hidden", timeout=timeout)
