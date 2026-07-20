import pytest
import requests

from api_clients import OpenMeteoClient, TheMealDBClient

THEMEALDB_BASE_URL = "https://www.themealdb.com/api/json/v1/1/"
OPENMETEO_BASE_URL = "https://api.open-meteo.com/v1/forecast"


@pytest.fixture(scope="session")
def http_session():
    session = requests.Session()
    yield session
    session.close()


@pytest.fixture(scope="session")
def themealdb_base_url():
    return THEMEALDB_BASE_URL


@pytest.fixture(scope="session")
def openmeteo_base_url():
    return OPENMETEO_BASE_URL


@pytest.fixture(scope="session")
def mealdb_client(http_session, themealdb_base_url):
    return TheMealDBClient(http_session, themealdb_base_url)


@pytest.fixture(scope="session")
def meteo_client(http_session, openmeteo_base_url):
    return OpenMeteoClient(http_session, openmeteo_base_url)
