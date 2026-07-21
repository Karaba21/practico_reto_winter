import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// k6's http.get(url, params) segundo argumento es de OPCIONES (tags,
// headers), no query params como en `requests`. Hay que armar la query
// string a mano.
function conQuery(url, query) {
  const partes = Object.entries(query).map(
    ([clave, valor]) => `${encodeURIComponent(clave)}=${encodeURIComponent(valor)}`
  );
  return `${url}?${partes.join('&')}`;
}

// ---------------------------------------------------------------------------
// Operativo Invierno: la ATU bajo presión
//
// Simula la app de la Asociación de Tortafriteros del Uruguay consultando el
// clima (Open-Meteo) para decidir cuánta harina y aceite tener a mano en cada
// ciudad. Primero resuelve el nombre de la ciudad vía el geocoder público
// (así los nombres mal escritos fallan de forma orgánica) y después pide el
// pronóstico actual con las coordenadas obtenidas.
// ---------------------------------------------------------------------------

const GEOCODING_URL = 'https://geocoding-api.open-meteo.com/v1/search';
const FORECAST_URL = 'https://api.open-meteo.com/v1/forecast';

const CIUDADES_VALIDAS = [
  { nombre: 'Montevideo' },
  { nombre: 'Salto' },
  { nombre: 'Paysandú' },
  { nombre: 'Las Piedras' },
  { nombre: 'Rivera' },
  { nombre: 'Maldonado' },
  { nombre: 'Tacuarembó' },
];

// Errores simulados: nombres mal escritos o directamente inexistentes.
const CIUDADES_INEXISTENTES = [
  { nombre: 'Montefideo' },
  { nombre: 'Paysandoom' },
  { nombre: 'Riviera' },
  { nombre: 'Tacuarembou' },
  { nombre: 'Maldonadoo' },
];

const TODAS_LAS_CIUDADES = [...CIUDADES_VALIDAS, ...CIUDADES_INEXISTENTES];

// Códigos WMO (weather_code de Open-Meteo) que representan lluvia/llovizna/tormenta.
const CODIGOS_DE_LLUVIA = [51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82, 95, 96, 99];

function normalizarNombreMetrica(nombre) {
  return nombre
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '') // saca tildes
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '');
}

// Métricas por ciudad: tasa de error y tiempo de respuesta, para poder
// comparar cómo se banca el sistema a cada tortafritero según su ciudad.
const metricasPorCiudad = {};
TODAS_LAS_CIUDADES.forEach(({ nombre }) => {
  const clave = normalizarNombreMetrica(nombre);
  metricasPorCiudad[clave] = {
    errores: new Rate(`errores_${clave}`),
    duracion: new Trend(`duracion_${clave}`, true),
  };
});

// Métricas globales del "Operativo Invierno".
const tasaErrorGlobal = new Rate('tasa_error_global');
const tasaErrorCiudadesValidas = new Rate('tasa_error_ciudades_validas');
const tasaErrorCiudadesInexistentes = new Rate('tasa_error_ciudades_inexistentes');
const alertasProduccion200 = new Counter('alertas_produccion_tortas_200');
const indiceCrocancia = new Trend('indice_crocancia_estimado');

export const options = {
  scenarios: {
    temporal_de_invierno: {
      executor: 'constant-vus',
      vus: 100,
      duration: '2m',
    },
  },
  thresholds: {
    http_req_duration: ['p(95)<3000'],
    // Solo cuenta como "http fallido" un error real de red/servidor, no una
    // ciudad mal escrita (esa es la resuelve el geocoder con 200 y 0 resultados).
    http_req_failed: ['rate<0.05'],
  },
};

// "Índice de crocancia estimado": cuanto más frío, más lluvia y más viento
// (se enfría el aceite más rápido), más manija le meten los tortafritas y
// más "crocante" sale la tanda -> más ganas de comer tortas fritas.
// Fórmula inventada para la métrica bonus, documentada en el README.
function calcularIndiceCrocancia(temperatura, hayLluvia, precipitacionMm, vientoKmh) {
  let indice = 50;
  indice += Math.max(0, 15 - temperatura) * 2; // más frío, más crocancia
  indice += hayLluvia ? 15 : 0;
  indice += Math.min(precipitacionMm * 3, 20);
  indice -= Math.min(vientoKmh * 0.3, 15);
  return Math.max(0, Math.min(100, Math.round(indice)));
}

function registrarResultado(clave, exito, duracionMs) {
  metricasPorCiudad[clave].errores.add(!exito);
  metricasPorCiudad[clave].duracion.add(duracionMs);
  tasaErrorGlobal.add(!exito);
}

export default function () {
  const ciudad = TODAS_LAS_CIUDADES[Math.floor(Math.random() * TODAS_LAS_CIUDADES.length)];
  const clave = normalizarNombreMetrica(ciudad.nombre);
  const esCiudadValida = CIUDADES_VALIDAS.some((c) => c.nombre === ciudad.nombre);

  // 1) La app resuelve el nombre de la ciudad a coordenadas. El geocoder de
  // Open-Meteo no soporta filtrar por país en el server, así que se pide un
  // puñado de candidatos y se filtra por Uruguay del lado del cliente (igual
  // que haría la app de la ATU, que solo le interesan ciudades uruguayas).
  const geoRes = http.get(
    conQuery(GEOCODING_URL, { name: ciudad.nombre, count: 10, language: 'es', format: 'json' }),
    { tags: { ciudad: ciudad.nombre, tipo: 'geocoding' } }
  );

  const geoOk = check(geoRes, {
    'geocoding responde 200': (r) => r.status === 200,
  });

  let coordenadas = null;
  if (geoOk) {
    const body = geoRes.json();
    if (body && body.results && body.results.length > 0) {
      const uruguaya = body.results.find((r) => r.country_code === 'UY');
      if (uruguaya) {
        coordenadas = { lat: uruguaya.latitude, lon: uruguaya.longitude };
      }
    }
  }

  const ciudadResuelta = geoOk && coordenadas !== null;
  check(null, { 'ciudad resuelta correctamente': () => ciudadResuelta });

  if (!ciudadResuelta) {
    // Nombre inexistente o mal escrito: no hay forma de saber cuánta harina
    // amasar en esa ciudad. Se cuenta como error de negocio.
    registrarResultado(clave, false, geoRes.timings.duration);
    (esCiudadValida ? tasaErrorCiudadesValidas : tasaErrorCiudadesInexistentes).add(true);
    sleep(5);
    return;
  }

  // 2) Con las coordenadas resueltas, se pide el pronóstico actual.
  const forecastRes = http.get(
    conQuery(FORECAST_URL, {
      latitude: coordenadas.lat,
      longitude: coordenadas.lon,
      current: 'temperature_2m,precipitation,weather_code,relative_humidity_2m,wind_speed_10m',
    }),
    { tags: { ciudad: ciudad.nombre, tipo: 'forecast' } }
  );

  const forecastOk = check(forecastRes, {
    'forecast responde 200': (r) => r.status === 200,
    'forecast trae temperatura numérica': (r) => {
      const data = r.json();
      return data && data.current && typeof data.current.temperature_2m === 'number';
    },
  });

  registrarResultado(clave, forecastOk, geoRes.timings.duration + forecastRes.timings.duration);
  (esCiudadValida ? tasaErrorCiudadesValidas : tasaErrorCiudadesInexistentes).add(!forecastOk);

  if (forecastOk) {
    const current = forecastRes.json().current;
    const temperatura = current.temperature_2m;
    const precipitacion = current.precipitation || 0;
    const viento = current.wind_speed_10m || 0;
    const hayLluvia = CODIGOS_DE_LLUVIA.includes(current.weather_code) || precipitacion > 0;

    indiceCrocancia.add(calcularIndiceCrocancia(temperatura, hayLluvia, precipitacion, viento));

    // Regla de negocio para lucirse.
    if (hayLluvia && temperatura < 15) {
      alertasProduccion200.add(1, { ciudad: ciudad.nombre });
    }
  }

  sleep(5);
}
