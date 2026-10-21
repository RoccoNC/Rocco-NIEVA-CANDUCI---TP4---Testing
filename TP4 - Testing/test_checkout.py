from datetime import date
from decimal import Decimal

import pytest

from checkout import (
    CheckoutError,
    calcular_descuento,
    calcular_envio,
    calcular_subtotal,
    calcular_total,
    validar_item,
)

HOY_VIGENTE = date(2026, 10, 1)


def item(producto="buzo", talle="M", cantidad=1, **extra):
    return {"producto": producto, "talle": talle, "cantidad": cantidad, **extra}


def codigo_de_error(funcion, *args):
    with pytest.raises(CheckoutError) as error:
        funcion(*args)
    return error.value.code


def test_cantidad_cero_es_invalida():
    assert codigo_de_error(validar_item, item(cantidad=0)) == "CANTIDAD_INVALIDA"


# ---------------------------------------------------------------------------
# R1 — Catálogo y precios
# ---------------------------------------------------------------------------


def test_precio_del_buzo_es_24999_90():
    assert calcular_subtotal([item("buzo")]) == Decimal("24999.90")


def test_precio_de_la_remera_es_11999_50():
    assert calcular_subtotal([item("remera")]) == Decimal("11999.50")


def test_precio_de_la_campera_es_47999_99():
    assert calcular_subtotal([item("campera")]) == Decimal("47999.99")


def test_subtotal_de_tres_buzos_es_exacto_al_centavo():
    assert calcular_subtotal([item("buzo", cantidad=3)]) == Decimal("74999.70")


def test_subtotal_suma_los_tres_productos():
    carrito = [item("buzo"), item("remera"), item("campera")]

    assert calcular_subtotal(carrito) == Decimal("84999.39")


def test_subtotal_es_decimal_y_no_float():
    resultado = calcular_subtotal([item("buzo")])

    assert isinstance(resultado, Decimal)


@pytest.mark.parametrize(
    "producto",
    ["zapatillas", "BUZO", "Buzo", " buzo ", "buzo ", "", None, 123],
)
def test_producto_que_no_es_exactamente_del_catalogo_es_inexistente(producto):
    assert codigo_de_error(validar_item, item(producto)) == "PRODUCTO_INEXISTENTE"


def test_subtotal_con_producto_inexistente_lanza_error_en_vez_de_omitirlo():
    carrito = [item("zapatillas")]

    assert codigo_de_error(calcular_subtotal, carrito) == "PRODUCTO_INEXISTENTE"


def test_producto_inexistente_en_el_segundo_item_no_se_omite_en_silencio():
    carrito = [item("buzo"), item("zapatillas")]

    assert codigo_de_error(calcular_subtotal, carrito) == "PRODUCTO_INEXISTENTE"


@pytest.mark.parametrize("precio_del_cliente", [1, 0, -500])
def test_el_precio_propio_del_item_se_ignora(precio_del_cliente):
    carrito = [item("buzo", precio=precio_del_cliente)]

    assert calcular_subtotal(carrito) == Decimal("24999.90")


def test_las_claves_extra_del_item_se_ignoran():
    carrito = [item("remera", color="rojo")]

    assert calcular_subtotal(carrito) == Decimal("11999.50")


def test_el_producto_se_valida_antes_que_talle_y_cantidad():
    problematico = item("zapatillas", talle="XXXL", cantidad=99)

    assert codigo_de_error(validar_item, problematico) == "PRODUCTO_INEXISTENTE"


# ---------------------------------------------------------------------------
# R2 — Talles
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("talle", ["XS", "S", "M", "L", "XL", "XXL"])
def test_cada_talle_valido_es_aceptado(talle):
    assert validar_item(item(talle=talle)) is None


@pytest.mark.parametrize("talle", ["m", "xxl", "Xl", "xL"])
def test_el_talle_no_distingue_mayuscula_de_minuscula(talle):
    assert validar_item(item(talle=talle)) is None


@pytest.mark.parametrize("talle", ["  M ", " M", "M ", " xl "])
def test_el_talle_ignora_espacios_al_principio_y_al_final(talle):
    assert validar_item(item(talle=talle)) is None


@pytest.mark.parametrize(
    "talle",
    ["XXXL", "XXS", "Z", "Medium", "", "   ", "X L"],
)
def test_talle_que_no_existe_es_invalido(talle):
    assert codigo_de_error(validar_item, item(talle=talle)) == "TALLE_INVALIDO"


@pytest.mark.parametrize("talle", [None, 5])
def test_talle_que_no_es_texto_es_invalido_y_no_otra_excepcion(talle):
    assert codigo_de_error(validar_item, item(talle=talle)) == "TALLE_INVALIDO"


def test_el_talle_no_cambia_el_precio():
    assert calcular_subtotal([item("buzo", talle=" m ")]) == Decimal("24999.90")


def test_el_talle_se_valida_antes_que_la_cantidad():
    problematico = item("buzo", talle="XXXL", cantidad=99)

    assert codigo_de_error(validar_item, problematico) == "TALLE_INVALIDO"