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


# ---------------------------------------------------------------------------
# R6 — Cupones
# ---------------------------------------------------------------------------


def test_egresados2026_aplica_quince_por_ciento():
    descuento = calcular_descuento(Decimal("100000.00"), 1, "EGRESADOS2026", date(2026, 10, 1))
    assert descuento == Decimal("15000.00")


def test_egresados2026_acepta_minusculas_y_espacios():
    descuento = calcular_descuento(Decimal("100000.00"), 1, "  egresados2026  ", date(2026, 10, 1))
    assert descuento == Decimal("15000.00")


def test_egresados2026_es_valido_el_30_de_noviembre_inclusive():
    descuento = calcular_descuento(Decimal("100000.00"), 1, "EGRESADOS2026", date(2026, 11, 30))
    assert descuento == Decimal("15000.00")


def test_egresados2026_esta_vencido_desde_el_1_de_diciembre():
    assert codigo_de_error(
        calcular_descuento, Decimal("100000.00"), 1, "EGRESADOS2026", date(2026, 12, 1)
    ) == "CUPON_VENCIDO"


def test_bienvenida_descuenta_3000_con_subtotal_exactamente_20000():
    descuento = calcular_descuento(Decimal("20000.00"), 1, "BIENVENIDA", date(2026, 10, 1))
    assert descuento == Decimal("3000.00")


def test_bienvenida_acepta_minusculas_y_espacios():
    descuento = calcular_descuento(Decimal("25000.00"), 1, "  bienvenida  ", date(2026, 10, 1))
    assert descuento == Decimal("3000.00")


def test_bienvenida_rechaza_subtotal_menor_a_20000():
    assert codigo_de_error(
        calcular_descuento, Decimal("19999.99"), 1, "BIENVENIDA", date(2026, 10, 1)
    ) == "CUPON_MINIMO_NO_ALCANZADO"


@pytest.mark.parametrize("cupon", [None, "", "   "])
def test_cupon_ausente_o_vacio_equivale_a_no_usar_cupon(cupon):
    descuento = calcular_descuento(Decimal("10000.00"), 1, cupon, date(2026, 10, 1))
    assert descuento == Decimal("0.00")


def test_debug100_no_es_un_cupon_valido():
    assert codigo_de_error(
        calcular_descuento, Decimal("100000.00"), 1, "DEBUG100", date(2026, 10, 1)
    ) == "CUPON_INVALIDO"


def test_codigo_de_cupon_desconocido_es_invalido():
    assert codigo_de_error(
        calcular_descuento, Decimal("100000.00"), 1, "NOEXISTE", date(2026, 10, 1)
    ) == "CUPON_INVALIDO"


def test_cupon_y_descuento_por_cantidad_no_se_acumulan_y_gana_el_mayor():
    descuento = calcular_descuento(Decimal("100000.00"), 5, "EGRESADOS2026", date(2026, 10, 1))
    assert descuento == Decimal("15000.00")


def test_descuento_por_cantidad_gana_si_es_mayor_que_cupon_fijo():
    descuento = calcular_descuento(Decimal("100000.00"), 5, "BIENVENIDA", date(2026, 10, 1))
    assert descuento == Decimal("10000.00")


def test_descuento_de_cupon_porcentual_usa_redondeo_comercial():
    descuento = calcular_descuento(Decimal("11999.50"), 1, "EGRESADOS2026", date(2026, 10, 1))
    assert descuento == Decimal("1799.93")


def test_calcular_total_normaliza_cupon_y_aplica_el_mayor_descuento():
    carrito = [item("buzo", cantidad=5)]
    resultado = calcular_total(carrito, "CABA", "  egresados2026  ", date(2026, 10, 1))
    assert resultado["descuento"] == Decimal("18749.93")


# ---------------------------------------------------------------------------
# R8 — Envío
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("zona", "esperado"),
    [
        ("CABA", Decimal("2500")),
        ("GBA", Decimal("4000")),
        ("INTERIOR", Decimal("6500")),
        ("RETIRO", Decimal("0")),
    ],
)
def test_cada_zona_tiene_el_costo_de_envio_especificado(zona, esperado):
    envio = calcular_envio(Decimal("59999.99"), zona)

    assert envio == esperado


@pytest.mark.parametrize(
    ("zona", "esperado"),
    [
        (" caba ", Decimal("2500")),
        ("gba", Decimal("4000")),
        (" interior ", Decimal("6500")),
        ("retiro", Decimal("0")),
    ],
)
def test_la_zona_ignora_mayusculas_minusculas_y_espacios(zona, esperado):
    envio = calcular_envio(Decimal("59999.99"), zona)

    assert envio == esperado


def test_subtotal_con_descuento_de_60000_tiene_envio_gratis():
    envio = calcular_envio(Decimal("60000.00"), "CABA")

    assert envio == Decimal("0")


def test_subtotal_con_descuento_mayor_a_60000_tiene_envio_gratis():
    envio = calcular_envio(Decimal("60000.01"), "INTERIOR")

    assert envio == Decimal("0")


def test_subtotal_con_descuento_de_59999_99_paga_envio():
    envio = calcular_envio(Decimal("59999.99"), "CABA")

    assert envio == Decimal("2500")


def test_zona_inexistente_lanza_checkout_error_zona_invalida():
    assert codigo_de_error(
        calcular_envio,
        Decimal("10000.00"),
        "MARTE",
    ) == "ZONA_INVALIDA"


def test_calcular_total_evalua_envio_gratis_despues_del_descuento():
    carrito = [item("campera"), item("remera")]

    resultado = calcular_total(
        carrito,
        "CABA",
        "BIENVENIDA",
        date(2026, 10, 1),
    )

    assert resultado["subtotal"] == Decimal("59999.49")
    assert resultado["descuento"] == Decimal("3000.00")
    assert resultado["envio"] == Decimal("2500")


def test_calcular_total_no_da_envio_gratis_si_el_descuento_baja_de_60000():
    carrito = [
        item("buzo", cantidad=2),
        item("remera"),
    ]

    resultado = calcular_total(
        carrito,
        "CABA",
        "BIENVENIDA",
        date(2026, 10, 1),
    )

    assert resultado["subtotal"] == Decimal("61999.30")
    assert resultado["descuento"] == Decimal("3000.00")
    assert resultado["envio"] == Decimal("2500")


def test_calcular_total_da_envio_gratis_si_luego_del_descuento_quedan_60000_o_mas():
    carrito = [
        item("buzo", cantidad=2),
        item("remera", cantidad=2),
    ]

    resultado = calcular_total(
        carrito,
        "CABA",
        None,
        date(2026, 10, 1),
    )

    assert resultado["subtotal"] == Decimal("73998.80")
    assert resultado["descuento"] == Decimal("0.00")
    assert resultado["envio"] == Decimal("0")


# ---------------------------------------------------------------------------
# R7 — Dinero y redondeo
# ---------------------------------------------------------------------------


def test_calcular_envio_devuelve_decimal():
    envio = calcular_envio(Decimal("10000.00"), "CABA")

    assert isinstance(envio, Decimal)


def test_envio_gratis_devuelve_decimal():
    envio = calcular_envio(Decimal("60000.00"), "CABA")

    assert isinstance(envio, Decimal)


def test_calcular_total_devuelve_todos_los_importes_como_decimal():
    carrito = [item("remera")]

    resultado = calcular_total(
        carrito,
        "CABA",
        "EGRESADOS2026",
        date(2026, 10, 1),
    )

    assert isinstance(resultado["subtotal"], Decimal)
    assert isinstance(resultado["descuento"], Decimal)
    assert isinstance(resultado["envio"], Decimal)
    assert isinstance(resultado["total"], Decimal)


def test_descuento_porcentual_redondea_1799_925_a_1799_93():
    descuento = calcular_descuento(
        Decimal("11999.50"),
        1,
        "EGRESADOS2026",
        date(2026, 10, 1),
    )

    assert descuento == Decimal("1799.93")


# ---------------------------------------------------------------------------
# R9 — Total
# ---------------------------------------------------------------------------


def test_total_es_subtotal_menos_descuento_mas_envio_sin_descuento():
    carrito = [item("remera")]

    resultado = calcular_total(carrito, "CABA")

    assert resultado == {
        "subtotal": Decimal("11999.50"),
        "descuento": Decimal("0.00"),
        "envio": Decimal("2500"),
        "total": Decimal("14499.50"),
    }


def test_total_con_cupon_porcentual_calcula_todos_los_importes():
    carrito = [item("remera")]

    resultado = calcular_total(
        carrito,
        "CABA",
        "EGRESADOS2026",
        date(2026, 10, 1),
    )

    assert resultado == {
        "subtotal": Decimal("11999.50"),
        "descuento": Decimal("1799.93"),
        "envio": Decimal("2500"),
        "total": Decimal("12699.57"),
    }


def test_total_con_descuento_por_cantidad_y_envio_gratis():
    carrito = [item("buzo", cantidad=5)]

    resultado = calcular_total(carrito, "CABA")

    assert resultado == {
        "subtotal": Decimal("124999.50"),
        "descuento": Decimal("12499.95"),
        "envio": Decimal("0"),
        "total": Decimal("112499.55"),
    }


def test_total_con_bienvenida_y_envio_pago():
    carrito = [
        item("buzo", cantidad=2),
        item("remera"),
    ]

    resultado = calcular_total(
        carrito,
        "GBA",
        "BIENVENIDA",
        date(2026, 10, 1),
    )

    assert resultado == {
        "subtotal": Decimal("61999.30"),
        "descuento": Decimal("3000.00"),
        "envio": Decimal("4000"),
        "total": Decimal("62999.30"),
    }


def test_total_con_retiro_no_agrega_envio():
    carrito = [item("campera")]

    resultado = calcular_total(carrito, "RETIRO")

    assert resultado == {
        "subtotal": Decimal("47999.99"),
        "descuento": Decimal("0.00"),
        "envio": Decimal("0"),
        "total": Decimal("47999.99"),
    }


def test_calcular_total_valida_cupon_antes_que_zona():
    carrito = [item("buzo")]

    assert codigo_de_error(
        calcular_total,
        carrito,
        "MARTE",
        "NOEXISTE",
        date(2026, 10, 1),
    ) == "CUPON_INVALIDO"


def test_calcular_total_valida_zona_despues_de_carrito_items_y_cupon():
    carrito = [item("buzo")]

    assert codigo_de_error(
        calcular_total,
        carrito,
        "MARTE",
        None,
        date(2026, 10, 1),
    ) == "ZONA_INVALIDA"


def test_total_no_modifica_el_carrito_aunque_haya_descuento_y_envio():
    carrito = [
        item("buzo", talle=" m ", cantidad=2),
        item("remera", talle="xl", cantidad=3),
    ]
    copia = copy.deepcopy(carrito)

    calcular_total(
        carrito,
        " gba ",
        " bienvenida ",
        date(2026, 10, 1),
    )

    assert carrito == copia

