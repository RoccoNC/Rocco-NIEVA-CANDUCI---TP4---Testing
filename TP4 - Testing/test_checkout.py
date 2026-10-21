import copy
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


# ---------------------------------------------------------------------------
# R3 — Cantidad
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("cantidad", [1, 2, 5, 9, 10])
def test_cantidad_entera_entre_1_y_10_es_valida(cantidad):
    assert validar_item(item(cantidad=cantidad)) is None


@pytest.mark.parametrize("cantidad", [0, -1, -10, 11, 100])
def test_cantidad_entera_fuera_de_rango_es_invalida(cantidad):
    assert codigo_de_error(validar_item, item(cantidad=cantidad)) == "CANTIDAD_INVALIDA"


@pytest.mark.parametrize("cantidad", [2.5, 0.5, 10.5])
def test_cantidad_no_entera_es_invalida(cantidad):
    assert codigo_de_error(validar_item, item(cantidad=cantidad)) == "CANTIDAD_INVALIDA"


@pytest.mark.parametrize("cantidad", ["3", None, True, float("nan")])
def test_cantidad_que_no_es_un_numero_entero_es_invalida_y_no_otra_excepcion(cantidad):
    assert codigo_de_error(validar_item, item(cantidad=cantidad)) == "CANTIDAD_INVALIDA"


def test_diez_buzos_se_calculan_sin_error():
    assert calcular_subtotal([item("buzo", cantidad=10)]) == Decimal("249999.00")


def test_diez_remeras_se_calculan_sin_error():
    assert calcular_subtotal([item("remera", cantidad=10)]) == Decimal("119995.00")


def test_el_error_de_cantidad_se_propaga_desde_calcular_subtotal():
    carrito = [item("buzo", cantidad=11)]

    assert codigo_de_error(calcular_subtotal, carrito) == "CANTIDAD_INVALIDA"


def test_se_informa_primero_el_item_con_error_de_cantidad_aunque_el_segundo_tambien_falle():
    carrito = [item("buzo", cantidad=0), item("zapatillas")]

    assert codigo_de_error(calcular_subtotal, carrito) == "CANTIDAD_INVALIDA"


# ---------------------------------------------------------------------------
# R4 — Carrito
# ---------------------------------------------------------------------------


def test_carrito_con_un_solo_item_es_valido():
    assert calcular_subtotal([item("buzo")]) == Decimal("24999.90")


def test_carrito_con_productos_distintos_suma_los_subtotales():
    carrito = [item("buzo"), item("remera")]

    assert calcular_subtotal(carrito) == Decimal("36999.40")


def test_carrito_con_el_mismo_producto_en_dos_talles_suma_las_cantidades():
    carrito = [item("buzo", talle="M", cantidad=1), item("buzo", talle="L", cantidad=2)]

    assert calcular_subtotal(carrito) == Decimal("74999.70")


def test_el_limite_de_10_es_por_item_y_no_por_carrito():
    carrito = [item("buzo", cantidad=10), item("remera", cantidad=10)]

    assert calcular_subtotal(carrito) == Decimal("369994.00")


def test_carrito_vacio_en_calcular_subtotal_es_carrito_vacio():
    assert codigo_de_error(calcular_subtotal, []) == "CARRITO_VACIO"


def test_carrito_vacio_en_calcular_total_es_carrito_vacio():
    assert codigo_de_error(calcular_total, [], "CABA") == "CARRITO_VACIO"


def test_carrito_que_no_es_una_lista_lanza_checkout_error():
    with pytest.raises(CheckoutError):
        calcular_total(None, "CABA")


def test_validar_item_no_modifica_el_item_que_recibe():
    original = item(talle=" m ")
    copia = copy.deepcopy(original)

    validar_item(original)

    assert original == copia


def test_calcular_subtotal_no_modifica_el_carrito():
    carrito = [item("buzo", talle=" m ", cantidad=2)]
    copia = copy.deepcopy(carrito)

    calcular_subtotal(carrito)

    assert carrito == copia


def test_calcular_total_no_modifica_el_carrito():
    carrito = [item("buzo", talle=" m ", cantidad=2)]
    copia = copy.deepcopy(carrito)

    calcular_total(carrito, "CABA")

    assert carrito == copia


def test_calcular_total_con_cupon_no_modifica_el_carrito():
    carrito = [item("buzo", talle=" m "), item("remera", talle="xl")]
    copia = copy.deepcopy(carrito)

    calcular_total(carrito, "CABA", "EGRESADOS2026", HOY_VIGENTE)

    assert carrito == copia


def test_calcular_subtotal_conserva_las_claves_extra_del_item():
    carrito = [item("buzo", talle="m", precio=1, color="rojo")]
    copia = copy.deepcopy(carrito)

    calcular_subtotal(carrito)

    assert carrito == copia


def test_calcular_total_conserva_el_largo_y_el_orden_del_carrito():
    carrito = [item("campera", talle="s"), item("buzo", talle="m"), item("remera", talle="l")]
    copia = copy.deepcopy(carrito)

    calcular_total(carrito, "CABA")

    assert carrito == copia


def test_un_talle_invalido_no_modifica_el_item():
    original = item(talle=" xxxl ")
    copia = copy.deepcopy(original)

    codigo_de_error(validar_item, original)

    assert original == copia


def test_un_error_en_el_segundo_item_no_deja_modificado_al_primero():
    carrito = [item("buzo", talle="m"), item("zapatillas", talle="m")]
    copia = copy.deepcopy(carrito)

    codigo_de_error(calcular_subtotal, carrito)

    assert carrito == copia


def test_un_cupon_invalido_no_modifica_el_carrito():
    carrito = [item("buzo", talle=" m ")]
    copia = copy.deepcopy(carrito)

    codigo_de_error(calcular_total, carrito, "CABA", "NOEXISTE", HOY_VIGENTE)

    assert carrito == copia


def test_el_carrito_vacio_se_informa_antes_que_una_zona_invalida():
    assert codigo_de_error(calcular_total, [], "MARTE") == "CARRITO_VACIO"


def test_el_carrito_vacio_se_informa_antes_que_un_cupon_invalido():
    assert codigo_de_error(calcular_total, [], "CABA", "NOEXISTE") == "CARRITO_VACIO"


def test_el_item_invalido_se_informa_antes_que_el_cupon_y_la_zona():
    carrito = [item("zapatillas")]

    assert codigo_de_error(calcular_total, carrito, "MARTE", "NOEXISTE") == "PRODUCTO_INEXISTENTE"


# ---------------------------------------------------------------------------
# R5 — Descuento por cantidad
# ---------------------------------------------------------------------------


def test_cuatro_prendas_no_aplican_descuento_por_cantidad():
    descuento = calcular_descuento(Decimal("100000.00"), 4)

    assert descuento == Decimal("0.00")


def test_cinco_prendas_aplican_diez_por_ciento_de_descuento():
    descuento = calcular_descuento(Decimal("100000.00"), 5)

    assert descuento == Decimal("10000.00")


def test_seis_prendas_aplican_diez_por_ciento_de_descuento():
    descuento = calcular_descuento(Decimal("100000.00"), 6)

    assert descuento == Decimal("10000.00")


def test_diez_prendas_aplican_diez_por_ciento_de_descuento():
    descuento = calcular_descuento(Decimal("249999.00"), 10)

    assert descuento == Decimal("24999.90")


def test_cinco_buzos_aplican_descuento_en_calcular_total():
    carrito = [item("buzo", cantidad=5)]

    resultado = calcular_total(carrito, "CABA")

    assert resultado["descuento"] == Decimal("12499.95")


def test_siete_buzos_aplican_diez_por_ciento():
    carrito = [item("buzo", cantidad=7)]

    resultado = calcular_total(carrito, "CABA")

    assert resultado["descuento"] == Decimal("17499.93")


def test_cinco_prendas_repartidas_en_varios_items_aplican_descuento():
    carrito = [
        item("buzo", cantidad=3),
        item("remera", cantidad=2),
    ]

    resultado = calcular_total(carrito, "CABA")

    assert resultado["descuento"] == Decimal("9899.87")


def test_cuatro_prendas_repartidas_no_aplican_descuento():
    carrito = [
        item("buzo", cantidad=2),
        item("remera", cantidad=2),
    ]

    resultado = calcular_total(carrito, "CABA")

    assert resultado["descuento"] == Decimal("0.00")


def test_veinte_prendas_repartidas_aplican_un_solo_diez_por_ciento():
    carrito = [
        item("buzo", cantidad=10),
        item("remera", cantidad=10),
    ]

    resultado = calcular_total(carrito, "CABA")

    assert resultado["descuento"] == Decimal("36999.40")


def test_descuento_por_cantidad_devuelve_decimal():
    descuento = calcular_descuento(Decimal("100000.00"), 5)

    assert isinstance(descuento, Decimal)


def test_descuento_por_cantidad_redondea_medio_centavo_hacia_arriba():
    descuento = calcular_descuento(Decimal("100.05"), 5)

    assert descuento == Decimal("10.01")


def test_descuento_por_cantidad_redondea_menos_de_medio_centavo_hacia_abajo():
    descuento = calcular_descuento(Decimal("100.04"), 5)

    assert descuento == Decimal("10.00")