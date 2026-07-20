import pytest

CIUDADES_VALIDAS = [
    {"nombre": "Montevideo", "lat": -34.90, "lon": -56.16},
    {"nombre": "Bariloche", "lat": -41.13, "lon": -71.31},
]


class TestCurrentWeather:
    @pytest.mark.parametrize("ciudad", CIUDADES_VALIDAS, ids=lambda c: c["nombre"])
    def test_current_temperature_returns_200_and_numeric_value(self, meteo_client, ciudad):
        response = meteo_client.current_weather(ciudad["lat"], ciudad["lon"])

        assert response.status_code == 200
        data = response.json()
        assert "current" in data
        assert isinstance(data["current"]["temperature_2m"], (int, float))

    def test_response_coordinates_match_requested_city(self, meteo_client):
        ciudad = CIUDADES_VALIDAS[0]

        response = meteo_client.current_weather(ciudad["lat"], ciudad["lon"])

        data = response.json()
        assert data["latitude"] == pytest.approx(ciudad["lat"], abs=0.5)
        assert data["longitude"] == pytest.approx(ciudad["lon"], abs=0.5)


class TestInvalidInput:
    def test_missing_coordinates_returns_no_usable_weather_data(self, meteo_client):
        # Open-Meteo answers with 200 and an empty body when lat/lon are
        # omitted entirely, rather than a proper error payload.
        response = meteo_client.raw_get({})

        assert response.status_code == 200
        assert response.text.strip() == ""

    @pytest.mark.parametrize("lat,lon", [(999, 999), (-999, -999)])
    def test_out_of_range_coordinates_returns_400(self, meteo_client, lat, lon):
        response = meteo_client.current_weather(lat, lon)

        assert response.status_code == 400
        assert response.json().get("error") is True

    def test_non_numeric_coordinates_returns_400(self, meteo_client):
        response = meteo_client.raw_get(
            {"latitude": "invalid", "longitude": "invalid", "current": "temperature_2m"}
        )

        assert response.status_code == 400
        assert response.json().get("error") is True
