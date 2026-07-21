"""
SearchPage: Page Object que representa la página principal de TMDB
y la interacción con el buscador.
Encapsula los selectores para que los steps de Behave no los conozcan.
"""

from pages.base_page import BasePage


class SearchPage(BasePage):
    URL = "https://www.themoviedb.org/"

    # Selectores encapsulados (si TMDB cambia su HTML, solo se toca acá)
    SEARCH_INPUT = "//input[@name='query']"
    FIRST_RESULT = "(//a[@data-media-type='movie' and starts-with(@href,'/movie/')])[1]"

    def open(self):
        self.goto(self.URL)

    def search_movie(self, title: str):
        self.fill(self.SEARCH_INPUT, title)
        self.press(self.SEARCH_INPUT, "Enter")

    def select_first_result(self):
        self.page.wait_for_selector(self.FIRST_RESULT)
        self.click(self.FIRST_RESULT)