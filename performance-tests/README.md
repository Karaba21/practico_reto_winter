# performance-tests

Pruebas de performance con [k6](https://k6.io) que simulan el "Operativo
Invierno" de la Asociación de Tortafriteros del Uruguay (ATU): miles de
tortafriteros consultando el clima a la vez durante un temporal para saber
cuánta harina y aceite tener a mano.

## API usada

- **Open-Meteo Geocoding** — `https://geocoding-api.open-meteo.com/v1/search`
  (resuelve nombre de ciudad → coordenadas; se piden 10 candidatos y se
  filtra por `country_code === 'UY'` del lado del cliente, porque el
  geocoder no soporta filtrar por país en el server. Acá fallan de forma
  orgánica los nombres mal escritos o inexistentes)
- **Open-Meteo Forecast** — `https://api.open-meteo.com/v1/forecast`
  (clima actual con las coordenadas resueltas)

Ambas son públicas y no requieren API key, igual que en `api-tests`.

## Instalación

```bash
brew install k6        # macOS
# o ver alternativas en https://k6.io/docs/get-started/installation/
```

## Cómo correr el test

Requiere conexión a internet (golpea la API real, sin mocks).

```bash
cd performance-tests
k6 run script.js
```

Para guardar el resumen final en JSON:

```bash
k6 run --summary-export=resumen.json script.js
```

## Escenario

- 100 usuarios virtuales concurrentes (`constant-vus`)
- Cada VU consulta una ciudad al azar cada 5 segundos, durante 2 minutos
- Ciudades objetivo: Montevideo, Salto, Paysandú, Las Piedras, Rivera,
  Maldonado, Tacuarembó
- Errores simulados: nombres mal escritos o inexistentes ("Montefideo",
  "Paysandoom", "Riviera", "Tacuarembou", "Maldonadoo") — el geocoder los
  devuelve como 0 resultados con status 200, así que se cuentan como error
  de negocio (ciudad no resuelta), no como falla HTTP
- Regla de negocio: si el clima indica lluvia y menos de 15°C, se dispara
  una alerta de "producción de tortas fritas al 200%" (métrica
  `alertas_produccion_tortas_200`)

## Métricas

- **Tiempo de respuesta**: `http_req_duration` (global) y `duracion_<ciudad>`
  (por ciudad, incluye la llamada de geocoding + forecast)
- **Tasa de errores**: `tasa_error_global`, `tasa_error_ciudades_validas`,
  `tasa_error_ciudades_inexistentes` y `errores_<ciudad>` por ciudad
- **Throughput**: `http_reqs` (peticiones por segundo, métrica nativa de k6)
- **Bonus — índice de crocancia estimado** (`indice_crocancia_estimado`):
  mide qué tan "crocante" saldría la tanda de tortas fritas según el clima.
  Fórmula inventada para la ocasión:

  ```
  indice = 50
         + max(0, 15 - temperatura) * 2   // más frío, más manija le meten
         + (hay_lluvia ? 15 : 0)          // la lluvia siempre suma clientes
         + min(precipitacion_mm * 3, 20)  // pero mucha lluvia moja la fritura
         - min(viento_kmh * 0.3, 15)      // el viento enfría el aceite
  ```

  Resultado acotado entre 0 y 100.

## Thresholds

- `http_req_duration`: p95 < 3000ms
- `http_req_failed` (fallas HTTP reales, no ciudades mal escritas): < 5%
