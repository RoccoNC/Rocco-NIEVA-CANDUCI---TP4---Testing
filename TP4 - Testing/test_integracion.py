from datetime import date
from decimal import Decimal

import pytest

import pedidos
from checkout import CheckoutError, calcular_total

HOY_VIGENTE = date(2026, 10, 1)


@pytest.fixture
def ruta(tmp_path):
    return str(tmp_path / "tienda.db")


@pytest.fixture
def con(ruta):
    conexion = pedidos.conectar(ruta)
    pedidos.crear_esquema(conexion)
    yield conexion
    conexion.close()


def item(producto="buzo", talle="M", cantidad=1, **extra):
    return {"producto": producto, "talle": talle, "cantidad": cantidad, **extra}


def contar(ruta, tabla):
    assert tabla in ("pedidos", "items")
    otra = pedidos.conectar(ruta)
    try:
        return otra.execute(f"SELECT COUNT(*) FROM {tabla}").fetchone()[0]
    finally:
        otra.close()


def test_un_id_inexistente_devuelve_none(con):
    assert pedidos.obtener_pedido(con, 999) is None


def test_guardar_pedido_devuelve_un_id_entero_y_recuperable(con):
    pedido_id = pedidos.guardar_pedido(
        con,
        "ana@mail.com",
        [item("buzo")],
        "CABA",
        None,
        HOY_VIGENTE,
    )
    recuperado = pedidos.obtener_pedido(con, pedido_id)

    assert isinstance(pedido_id, int)
    assert recuperado["id"] == pedido_id


def test_si_checkout_falla_no_queda_pedido_ni_items_guardados(con, ruta):
    carrito = [item("buzo"), item("remera", talle="XXXL")]

    with pytest.raises(CheckoutError) as error:
        pedidos.guardar_pedido(
            con,
            "ana@mail.com",
            carrito,
            "CABA",
            None,
            HOY_VIGENTE,
        )

    assert error.value.code == "TALLE_INVALIDO"
    assert contar(ruta, "pedidos") == 0
    assert contar(ruta, "items") == 0


def test_pedido_exitoso_es_visible_completo_desde_otra_conexion(con, ruta):
    pedido_id = pedidos.guardar_pedido(
        con,
        "ana@mail.com",
        [
            item("buzo", talle="M", cantidad=2),
            item("remera", talle="S", cantidad=1),
        ],
        "CABA",
        None,
        HOY_VIGENTE,
    )

    otra = pedidos.conectar(ruta)
    try:
        recuperado = pedidos.obtener_pedido(otra, pedido_id)
    finally:
        otra.close()

    assert recuperado is not None
    assert recuperado["subtotal"] == Decimal("61999.30")
    assert recuperado["descuento"] == Decimal("0.00")
    assert recuperado["envio"] == Decimal("0.00")
    assert recuperado["total"] == Decimal("61999.30")
    assert recuperado["items"] == [
        {
            "producto": "buzo",
            "talle": "M",
            "cantidad": 2,
            "precio_unitario": Decimal("24999.90"),
        },
        {
            "producto": "remera",
            "talle": "S",
            "cantidad": 1,
            "precio_unitario": Decimal("11999.50"),
        },
    ]


def test_montos_recuperados_son_decimal_e_identicos_a_checkout(con):
    carrito = [item("remera")]
    esperado = calcular_total(
        carrito,
        "CABA",
        "EGRESADOS2026",
        HOY_VIGENTE,
    )

    pedido_id = pedidos.guardar_pedido(
        con,
        "ana@mail.com",
        carrito,
        "CABA",
        "EGRESADOS2026",
        HOY_VIGENTE,
    )
    recuperado = pedidos.obtener_pedido(con, pedido_id)

    for campo in ("subtotal", "descuento", "envio", "total"):
        assert isinstance(recuperado[campo], Decimal)
        assert recuperado[campo] == esperado[campo]


def test_precio_unitario_siempre_sale_del_catalogo(con):
    pedido_id = pedidos.guardar_pedido(
        con,
        "ana@mail.com",
        [item("buzo", precio=Decimal("1.00"))],
        "CABA",
        None,
        HOY_VIGENTE,
    )
    recuperado = pedidos.obtener_pedido(con, pedido_id)

    assert recuperado["items"][0]["precio_unitario"] == Decimal("24999.90")


def test_datos_se_guardan_normalizados(con):
    pedido_id = pedidos.guardar_pedido(
        con,
        "  ANA@MAIL.COM  ",
        [item("remera", talle="  m  ")],
        "  caba  ",
        "  egresados2026  ",
        HOY_VIGENTE,
    )
    recuperado = pedidos.obtener_pedido(con, pedido_id)

    assert recuperado["email"] == "ana@mail.com"
    assert recuperado["zona"] == "CABA"
    assert recuperado["cupon"] == "EGRESADOS2026"
    assert recuperado["items"][0]["talle"] == "M"


def test_cupon_vacio_se_guarda_como_none(con):
    pedido_id = pedidos.guardar_pedido(
        con,
        "ana@mail.com",
        [item("buzo")],
        "CABA",
        "   ",
        HOY_VIGENTE,
    )
    recuperado = pedidos.obtener_pedido(con, pedido_id)

    assert recuperado["cupon"] is None


def test_obtener_pedido_tiene_el_formato_completo_especificado(con):
    pedido_id = pedidos.guardar_pedido(
        con,
        "ana@mail.com",
        [item("remera")],
        "RETIRO",
        None,
        HOY_VIGENTE,
    )
    recuperado = pedidos.obtener_pedido(con, pedido_id)

    assert set(recuperado) == {
        "id",
        "email",
        "zona",
        "cupon",
        "subtotal",
        "descuento",
        "envio",
        "total",
        "items",
    }
    assert set(recuperado["items"][0]) == {
        "producto",
        "talle",
        "cantidad",
        "precio_unitario",
    }


def test_pedidos_de_ignora_mayusculas_y_espacios_del_email(con):
    pedido_id = pedidos.guardar_pedido(
        con,
        "ana@mail.com",
        [item("buzo")],
        "CABA",
        None,
        HOY_VIGENTE,
    )

    resultado = pedidos.pedidos_de(con, "  ANA@MAIL.COM  ")

    assert [pedido["id"] for pedido in resultado] == [pedido_id]


def test_pedidos_de_devuelve_del_mas_reciente_al_mas_antiguo(con):
    primero = pedidos.guardar_pedido(
        con,
        "ana@mail.com",
        [item("buzo")],
        "CABA",
        None,
        HOY_VIGENTE,
    )
    segundo = pedidos.guardar_pedido(
        con,
        "ana@mail.com",
        [item("remera")],
        "RETIRO",
        None,
        HOY_VIGENTE,
    )

    resultado = pedidos.pedidos_de(con, "ana@mail.com")

    assert [pedido["id"] for pedido in resultado] == [segundo, primero]


@pytest.mark.parametrize(
    "email_malicioso",
    [
        "' OR '1'='1",
        "x' OR 1=1 --",
    ],
)
def test_pedidos_de_no_permite_inyeccion_sql(con, email_malicioso):
    pedidos.guardar_pedido(
        con,
        "ana@mail.com",
        [item("buzo")],
        "CABA",
        None,
        HOY_VIGENTE,
    )

    resultado = pedidos.pedidos_de(con, email_malicioso)

    assert resultado == []


def test_email_con_apostrofe_es_un_dato_valido_y_no_codigo_sql(con):
    pedido_id = pedidos.guardar_pedido(
        con,
        "o'brien@mail.com",
        [item("remera")],
        "RETIRO",
        None,
        HOY_VIGENTE,
    )

    resultado = pedidos.pedidos_de(con, "o'brien@mail.com")

    assert [pedido["id"] for pedido in resultado] == [pedido_id]
