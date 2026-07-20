import pytest

from schemas.meal_schema import validate_meal, validate_meal_summary

KNOWN_MEALS = ["Arrabiata", "Chicken Karaage"]


class TestSearchByName:
    @pytest.mark.parametrize("meal_name", KNOWN_MEALS)
    def test_search_known_meal_returns_200_and_results(self, mealdb_client, meal_name):
        response = mealdb_client.search_by_name(meal_name)

        assert response.status_code == 200
        meals = response.json()["meals"]
        assert meals is not None
        assert len(meals) > 0

    @pytest.mark.parametrize("meal_name", KNOWN_MEALS)
    def test_search_result_name_matches_query(self, mealdb_client, meal_name):
        response = mealdb_client.search_by_name(meal_name)

        names = [meal["strMeal"] for meal in response.json()["meals"]]
        assert any(meal_name.lower() in name.lower() for name in names)

    def test_search_unknown_meal_returns_none(self, mealdb_client):
        response = mealdb_client.search_by_name("xyzunlikelymealname123")

        assert response.status_code == 200
        assert response.json()["meals"] is None


class TestLookupById:
    def test_lookup_known_id_matches_schema(self, mealdb_client):
        search_response = mealdb_client.search_by_name("Arrabiata")
        known_id = search_response.json()["meals"][0]["idMeal"]

        response = mealdb_client.lookup_by_id(known_id)

        assert response.status_code == 200
        meal = response.json()["meals"][0]
        validate_meal(meal)

    def test_lookup_returns_none_for_nonexistent_id(self, mealdb_client):
        response = mealdb_client.lookup_by_id(999999)

        assert response.status_code == 200
        assert response.json()["meals"] is None

    @pytest.mark.parametrize("invalid_id", ["abc", "12.5", "!!!", ""])
    def test_lookup_returns_none_for_invalid_id_format(self, mealdb_client, invalid_id):
        response = mealdb_client.lookup_by_id(invalid_id)

        assert response.status_code == 200
        # TheMealDB signals a malformed id either with `meals: null` or with
        # the literal string "Invalid ID" - never an actual list of meals.
        meals = response.json()["meals"]
        assert meals is None or meals == "Invalid ID"


class TestFilterByCategory:
    @pytest.mark.parametrize("category", ["Beef", "Chicken", "Seafood"])
    def test_filter_known_category_returns_results(self, mealdb_client, category):
        response = mealdb_client.filter_by_category(category)

        assert response.status_code == 200
        meals = response.json()["meals"]
        assert meals is not None
        assert len(meals) > 0

    def test_filter_result_matches_summary_schema(self, mealdb_client):
        response = mealdb_client.filter_by_category("Beef")

        meals = response.json()["meals"]
        for meal in meals[:5]:
            validate_meal_summary(meal)

    def test_filter_unknown_category_returns_no_meals(self, mealdb_client):
        response = mealdb_client.filter_by_category("NotACategory123")

        assert response.status_code == 200
        assert not response.json()["meals"]


class TestCategories:
    def test_list_categories_returns_200_and_data(self, mealdb_client):
        response = mealdb_client.list_categories()

        assert response.status_code == 200
        categories = response.json()["categories"]
        assert len(categories) > 0
