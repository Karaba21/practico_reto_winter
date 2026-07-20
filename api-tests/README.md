# api-tests

Suite de pruebas automatizadas en Python + pytest que valida datos de comidas
(TheMealDB) y los combina con datos climáticos (Open-Meteo) para decidir,
con una regla de negocio simple, si un guiso está oficialmente justificado.

## APIs usadas

- **TheMealDB** — `https://www.themealdb.com/api/json/v1/1/` (sin auth)
- **Open-Meteo** — `https://api.open-meteo.com/v1/forecast` (sin auth)

Ambas APIs son públicas y no requieren API key.

## Instalación

```bash
cd api-tests
python3 -m venv venv          # si todavía no existe
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Cómo correr los tests

Requiere conexión a internet (los tests golpean las APIs reales, no hay mocks).

```bash
pytest -v
```

Correr solo un módulo:

```bash
pytest -v tests/test_themealdb.py
pytest -v tests/test_openmeteo.py
pytest -v tests/test_integration.py
```

El veredicto de cada combinación categoría + ciudad se loggea automáticamente
durante la corrida (configurado vía `log_cli` en `pytest.ini`), no hace falta
pasar `-s`.

### Reporte HTML — "Veredicto Gastronómico Oficial"

```bash
pytest --html=veredicto_gastronomico_oficial.html --self-contained-html
```

Abrí `veredicto_gastronomico_oficial.html` en el navegador para ver el reporte
con el detalle de cada test y su resultado.

## Estructura

```
api-tests/
├── README.md
├── requirements.txt
├── pytest.ini
├── conftest.py            # fixtures: sesión de requests, base URLs, clientes
├── api_clients.py         # TheMealDBClient y OpenMeteoClient (sin requests sueltos en los tests)
├── tests/
│   ├── test_themealdb.py    # búsqueda, lookup, filtro por categoría, categorías, casos negativos
│   ├── test_openmeteo.py    # clima actual y casos negativos (coordenadas inválidas/faltantes)
│   └── test_integration.py  # regla de negocio: guiso justificado según temperatura
└── schemas/
    └── meal_schema.py     # JSON Schemas + helpers de validación con jsonschema
```

## Regla de negocio

En `test_integration.py`, para cada combinación de categoría de comida y
ciudad:

1. Se filtra por categoría en TheMealDB (`filter.php`) y se toma el primer
   resultado.
2. Se trae el detalle completo de esa comida (`lookup.php`).
3. Se consulta la temperatura actual de la ciudad (Open-Meteo).
4. Se aplica la regla: **si temperatura < 15°C → "guiso oficialmente
   justificado"**, caso contrario → **"no justificado"**.

El dataset de ciudades usado (`CIUDADES` en `test_integration.py`) cubre
climas bien distintos (Ushuaia, Bariloche, Montevideo, Buenos Aires, São
Paulo) para ejercitar ambas ramas de la regla.

## Notas de diseño

- `conftest.py` expone fixtures de sesión (`http_session`, `mealdb_client`,
  `meteo_client`) reutilizables en todos los tests.
- `api_clients.py` centraliza timeouts y manejo de errores de conexión
  (`ApiError`), así los tests no repiten lógica de `requests`.
- La validación de esquema de `meals` usa `jsonschema` (`schemas/meal_schema.py`),
  chequeando campos obligatorios y tipos (IDs numéricos como string, strings
  no vacíos).
- Los casos negativos verifican que la API responda de forma controlada
  (`meals: null`, `error: true`, status 400) sin que el cliente lance
  excepciones no manejadas.
