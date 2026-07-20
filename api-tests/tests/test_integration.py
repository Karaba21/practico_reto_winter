"""Integration tests combining TheMealDB and Open-Meteo behind a simple
business rule: if it's cold enough, a guiso (stew) is justified.
"""

import logging

import pytest

logger = logging.getLogger("veredicto_gastronomico")

CIUDADES = [
    {"nombre": "Montevideo", "lat": -34.90, "lon": -56.16},
    {"nombre": "Buenos Aires", "lat": -34.60, "lon": -58.38},
    {"nombre": "Bariloche", "lat": -41.13, "lon": -71.31},
    {"nombre": "Ushuaia", "lat": -54.80, "lon": -68.30},
    {"nombre": "São Paulo", "lat": -23.55, "lon": -46.63},
]

CATEGORIAS = ["Beef", "Chicken", "Pork", "Vegetarian"]

TEMPERATURA_UMBRAL_GUISO = 15.0

# Al menos 5 combinaciones categoria + ciudad (una por ciudad, rotando categorias).
COMBINACIONES = [
    (CATEGORIAS[i % len(CATEGORIAS)], ciudad) for i, ciudad in enumerate(CIUDADES)
]


def veredicto_guiso(temperatura: float) -> str:
    if temperatura < TEMPERATURA_UMBRAL_GUISO:
        return "guiso oficialmente justificado"
    return "no justificado"


class TestGuisoOficialmenteJustificado:
    @pytest.mark.parametrize(
        "categoria,ciudad",
        COMBINACIONES,
        ids=[f"{categoria}-{ciudad['nombre']}" for categoria, ciudad in COMBINACIONES],
    )
    def test_veredicto_guiso_segun_clima(self, mealdb_client, meteo_client, categoria, ciudad):
        # 1. Buscar comidas de la categoria y traer el detalle completo del primer resultado.
        filter_response = mealdb_client.filter_by_category(categoria)
        assert filter_response.status_code == 200
        meals = filter_response.json()["meals"]
        assert meals, f"No se encontraron comidas para la categoria '{categoria}'"

        primer_meal_id = meals[0]["idMeal"]
        lookup_response = mealdb_client.lookup_by_id(primer_meal_id)
        assert lookup_response.status_code == 200
        meal_detail = lookup_response.json()["meals"][0]
        assert meal_detail["idMeal"] == primer_meal_id
        assert meal_detail["strMeal"]

        # 2. Consultar la temperatura actual de la ciudad.
        weather_response = meteo_client.current_weather(ciudad["lat"], ciudad["lon"])
        assert weather_response.status_code == 200
        temperatura = weather_response.json()["current"]["temperature_2m"]

        # 3. Aplicar la regla de negocio y loggear el veredicto.
        veredicto = veredicto_guiso(temperatura)
        mensaje = (
            f"[VEREDICTO] {ciudad['nombre']} ({temperatura}°C) + "
            f"{meal_detail['strMeal']} ({categoria}) -> {veredicto.upper()}"
        )
        logger.info(mensaje)
        print(mensaje)

        if temperatura < TEMPERATURA_UMBRAL_GUISO:
            assert veredicto == "guiso oficialmente justificado"
        else:
            assert veredicto == "no justificado"
