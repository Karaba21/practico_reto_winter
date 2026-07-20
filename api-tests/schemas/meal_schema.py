"""JSON Schemas for TheMealDB responses, plus small validation helpers."""

from jsonschema import validate

MEAL_SCHEMA = {
    "type": "object",
    "properties": {
        "idMeal": {"type": "string", "pattern": r"^\d+$"},
        "strMeal": {"type": "string", "minLength": 1},
        "strCategory": {"type": "string", "minLength": 1},
        "strInstructions": {"type": "string", "minLength": 1},
        "strMealThumb": {"type": "string", "minLength": 1},
    },
    "required": ["idMeal", "strMeal", "strCategory", "strInstructions", "strMealThumb"],
}

# filter.php returns a summarized meal object (no category/instructions).
MEAL_SUMMARY_SCHEMA = {
    "type": "object",
    "properties": {
        "idMeal": {"type": "string", "pattern": r"^\d+$"},
        "strMeal": {"type": "string", "minLength": 1},
        "strMealThumb": {"type": "string", "minLength": 1},
    },
    "required": ["idMeal", "strMeal", "strMealThumb"],
}


def validate_meal(meal: dict) -> None:
    validate(instance=meal, schema=MEAL_SCHEMA)


def validate_meal_summary(meal: dict) -> None:
    validate(instance=meal, schema=MEAL_SUMMARY_SCHEMA)
