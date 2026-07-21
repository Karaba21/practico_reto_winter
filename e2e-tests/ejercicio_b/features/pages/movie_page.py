"""
MoviePage: Page Object que representa la ficha de detalle de una película
en TMDB (director, calificación, etc.).
"""

from pages.base_page import BasePage


class MoviePage(BasePage):
    # Selectores encapsulados de la ficha de película
    DIRECTOR_LABEL = "//ol[contains(@class,'people')]//*[contains(text(),'Director')]"
    DIRECTOR_NAME = "//ol[contains(@class,'people')]//li[contains(@class,'profile')][p[@class='character'][normalize-space()='Director']]/p/a"
    RATING = "//div[contains(@class,'user_score_chart')]"

    def get_director(self) -> str:
        return self.get_text(self.DIRECTOR_NAME).strip()

    def get_rating(self) -> float:
        rating_attr = self.page.get_attribute(self.RATING, "data-percent")
        # TMDB expone el rating como porcentaje (0-100) en el atributo data-percent
        return round(float(rating_attr) / 10, 1)

    def save_screenshot(self, path: str):
        self.take_screenshot(path)