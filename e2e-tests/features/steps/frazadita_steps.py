import os
from behave import given, when, then

from features.pages.home_page import HomePage
from features.pages.cart_page import CartPage

SCREENSHOTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "screenshots")


@given('que ingreso a la tienda online de Geant')
def step_open_store(context):
    context.home_page = HomePage(context.page)
    context.home_page.open()
    context.added_products = []


@when('busco "{term}" y agrego el primer resultado al carrito')
def step_search_and_add_to_cart(context, term):
    context.home_page.search(term)
    name, price = context.home_page.add_first_result_to_cart()
    context.added_products.append({"name": name, "price": price})


@when('voy al carrito')
def step_go_to_cart(context):
    context.home_page.go_to_cart()
    context.cart_page = CartPage(context.page)
    context.cart_page.wait_for_cart_loaded()


@then('el carrito debe contener {expected_count:d} productos distintos')
def step_validate_cart_items(context, expected_count):
    context.cart_items = context.cart_page.get_cart_items()

    assert len(context.cart_items) == expected_count, (
        f"Se esperaban {expected_count} productos en el carrito, "
        f"pero se encontraron {len(context.cart_items)}: {context.cart_items}"
    )

    cart_names = {item["name"] for item in context.cart_items}
    expected_names = {product["name"] for product in context.added_products}
    assert expected_names.issubset(cart_names), (
        f"Los productos agregados {expected_names} no coinciden con "
        f"los productos del carrito {cart_names}"
    )


@then('el total del carrito debe ser igual a la suma de los precios de los productos agregados')
def step_validate_cart_total(context):
    expected_total = sum(item["price"] for item in context.cart_items)
    actual_total = context.cart_page.get_total()

    assert actual_total == expected_total, (
        f"El total del carrito ({actual_total}) no coincide con la suma "
        f"esperada de los productos ({expected_total})"
    )


@then('capturo una captura de pantalla del detalle del carrito')
def step_screenshot_cart(context):
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    screenshot_path = os.path.join(SCREENSHOTS_DIR, "cart_detail.png")
    context.cart_page.take_screenshot(screenshot_path)
    assert os.path.exists(screenshot_path), "No se generó la captura de pantalla del carrito"
