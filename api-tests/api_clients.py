"""Thin HTTP clients for TheMealDB and Open-Meteo public APIs.

Keeps requests-specific concerns (timeouts, connection errors) out of the
test modules so tests only deal with responses and assertions.
"""

import requests
from requests.exceptions import RequestException, Timeout

DEFAULT_TIMEOUT = 10


class ApiError(Exception):
    """Raised when a request fails to complete (timeout or connection error)."""


class TheMealDBClient:
    def __init__(self, session: requests.Session, base_url: str, timeout: int = DEFAULT_TIMEOUT):
        self.session = session
        self.base_url = base_url.rstrip("/") + "/"
        self.timeout = timeout

    def _get(self, endpoint: str, params: dict) -> requests.Response:
        try:
            return self.session.get(self.base_url + endpoint, params=params, timeout=self.timeout)
        except Timeout as exc:
            raise ApiError(f"Timeout calling TheMealDB endpoint '{endpoint}'") from exc
        except RequestException as exc:
            raise ApiError(f"Connection error calling TheMealDB endpoint '{endpoint}': {exc}") from exc

    def search_by_name(self, name: str) -> requests.Response:
        return self._get("search.php", {"s": name})

    def lookup_by_id(self, meal_id) -> requests.Response:
        return self._get("lookup.php", {"i": meal_id})

    def filter_by_category(self, category: str) -> requests.Response:
        return self._get("filter.php", {"c": category})

    def list_categories(self) -> requests.Response:
        return self._get("categories.php", {})


class OpenMeteoClient:
    def __init__(self, session: requests.Session, base_url: str, timeout: int = DEFAULT_TIMEOUT):
        self.session = session
        self.base_url = base_url
        self.timeout = timeout

    def current_weather(self, latitude, longitude, current: str = "temperature_2m") -> requests.Response:
        params = {"latitude": latitude, "longitude": longitude, "current": current}
        try:
            return self.session.get(self.base_url, params=params, timeout=self.timeout)
        except Timeout as exc:
            raise ApiError("Timeout calling Open-Meteo forecast endpoint") from exc
        except RequestException as exc:
            raise ApiError(f"Connection error calling Open-Meteo forecast endpoint: {exc}") from exc

    def raw_get(self, params: dict) -> requests.Response:
        """Escape hatch for negative tests that need full control over params."""
        try:
            return self.session.get(self.base_url, params=params, timeout=self.timeout)
        except Timeout as exc:
            raise ApiError("Timeout calling Open-Meteo forecast endpoint") from exc
        except RequestException as exc:
            raise ApiError(f"Connection error calling Open-Meteo forecast endpoint: {exc}") from exc
