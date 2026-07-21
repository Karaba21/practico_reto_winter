"""
Steps de Behave.
Estos steps NO conocen selectores de Playwright: solo llaman
a métodos de los Page Objects (SearchPage, MoviePage). Esto es la esencia
del Page Object Model combinado con BDD.
"""

from behave import given, when, then
from pages.search_page import SearchPage
from pages.movie_page import MoviePage


@given('que el usuario ingresa a TMDB')
def step_abrir_tmdb(context):
    context.search_page = SearchPage(context.page)
    context.search_page.open()


@when('busca la película "{titulo}"')
def step_buscar_pelicula(context, titulo):
    context.search_page.search_movie(titulo)


@when('selecciona el primer resultado de la búsqueda')
def step_seleccionar_resultado(context):
    context.search_page.select_first_result()
    context.movie_page = MoviePage(context.page)


@then('el director debe ser "{director_esperado}"')
def step_validar_director(context, director_esperado):
    director_actual = context.movie_page.get_director()
    assert director_actual == director_esperado, (
        f"Se esperaba el director '{director_esperado}' "
        f"pero se encontró '{director_actual}'"
    )


@then('la calificación debe ser mayor a {valor_minimo:g}')
def step_validar_calificacion(context, valor_minimo):
    rating_actual = context.movie_page.get_rating()
    assert rating_actual > valor_minimo, (
        f"Se esperaba una calificación mayor a {valor_minimo} "
        f"pero se obtuvo {rating_actual}"
    )


@then('se guarda una captura de pantalla como evidencia')
def step_guardar_screenshot(context):
    context.movie_page.save_screenshot("screenshots/ice_age_validacion.png")