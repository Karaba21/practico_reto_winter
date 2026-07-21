# E2E Tests

Pruebas E2E con **Behave** (Gherkin) + **Playwright** (Python), usando el patrón
**Page Object Model**. Cada ejercicio vive en su propia carpeta interna con su
propio `features/`, para mantenerlos independientes entre sí.

## Estructura

```
e2e-tests/
├── requirements.txt        # Dependencias compartidas por todos los ejercicios
├── venv/                   # Entorno virtual compartido (no versionado)
├── ejercicio_a/            # Operación Frazadita
│   ├── features/
│   │   ├── environment.py          # Hooks de Behave (setup/teardown de Playwright)
│   │   ├── frazadita.feature       # Escenario en Gherkin
│   │   ├── steps/
│   │   │   └── frazadita_steps.py  # Steps que conectan el Gherkin con las Page Objects
│   │   └── pages/
│   │       ├── base_page.py
│   │       ├── home_page.py        # Búsqueda y alta al carrito
│   │       └── cart_page.py        # Lectura y validación del carrito
│   └── screenshots/                # Se genera al correr los tests (capturas del carrito y de fallos)
└── ejercicio_b/            # Pendiente
    └── features/
        ├── steps/
        └── pages/
```

> `environment.py` vive dentro de `features/` de cada ejercicio porque Behave
> sólo lo autodetecta ahí (es su convención fija, no una carpeta arbitraria).
> Por eso cada ejercicio tiene el suyo, en vez de compartir uno solo.

## Instalación

El venv y las dependencias (`behave`, `playwright`) son compartidos por todos
los ejercicios:

```bash
cd e2e-tests
python3 -m venv venv
source venv/bin/activate        # En Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

## Ejecución

Como ya no hay un `features/` en la raíz, hay que pararse dentro de la carpeta
del ejercicio que se quiera correr (o pasarle la ruta a `behave`):

```bash
source venv/bin/activate

cd ejercicio_a
behave

# o, desde e2e-tests/, sin cambiar de directorio:
behave ejercicio_a/features
```

Por defecto corre en modo headless. Para ver el navegador mientras corre:

```bash
HEADLESS=false behave
```

## Ejercicio A — Operación Frazadita

Simula el flujo de compra de un usuario buscando productos de invierno en
[geant.com.uy](https://www.geant.com.uy/), agregando al menos dos productos
distintos al carrito y validando que los ítems y el total sean correctos.

### Qué valida el escenario

1. Ingresa a geant.com.uy.
2. Busca "manta" (winter blanket) y agrega el primer resultado al carrito.
3. Busca "calefactor" (electric heater) y agrega el primer resultado al carrito.
4. Va al carrito.
5. Valida que el carrito contenga los 2 productos agregados.
6. Valida que el total del carrito sea igual a la suma de los precios de esos productos.
7. Captura un screenshot del detalle del carrito en `screenshots/cart_detail.png`.

> Nota: se usan los términos en español "manta" y "calefactor" en lugar de
> "winter blanket" / "electric heater" porque el catálogo del sitio está en
> español y esos términos son los que devuelven resultados reales.

### Notas sobre el sitio

geant.com.uy es una SPA (Blazor Server), no un sitio estático: la búsqueda y
el agregado al carrito dependen de llamadas asincrónicas que a veces tardan
más de lo esperado. `HomePage.search()` reintenta la búsqueda si el grid de
resultados no aparece a tiempo, y `CartPage` sabe cerrar un posible diálogo
modal (`rz-dialog-wrapper`) que puede interceptar clics. Si el layout del
carrito cambia, los selectores a ajustar son los de
`ejercicio_a/features/pages/cart_page.py`.

## Ejercicio B

Pendiente.