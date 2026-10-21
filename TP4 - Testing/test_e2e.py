import json
import threading
import urllib.error
import urllib.request

import pytest

import api

RUTA = "/api/v1/pedidos"


@pytest.fixture
def url(tmp_path):
    servidor = api.crear_servidor(str(tmp_path / "tienda.db"), 0)
    threading.Thread(
        target=servidor.serve_forever,
        kwargs={"poll_interval": 0.05},
        daemon=True,
    ).start()

    yield f"http://127.0.0.1:{servidor.server_address[1]}"

    servidor.shutdown()
    servidor.server_close()


def pedir(url, metodo, ruta, cuerpo=None, crudo=None):
    datos = (
        crudo
        if crudo is not None
        else (json.dumps(cuerpo).encode() if cuerpo is not None else None)
    )

    req = urllib.request.Request(
        url + ruta,
        data=datos,
        method=metodo,
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(req, timeout=5) as respuesta:
            return respuesta.status, json.loads(respuesta.read() or b"null")
    except urllib.error.HTTPError as error:
        return error.code, json.loads(error.read() or b"null")


def compra(**cambios):
    cuerpo = {
        "email": "ana@mail.com",
        "zona": "CABA",
        "carrito": [
            {
                "producto": "buzo",
                "talle": "M",
                "cantidad": 1,
            }
        ],
    }
    cuerpo.update(cambios)
    return cuerpo


def assert_error(cuerpo, codigo):
    assert set(cuerpo) == {"error"}
    assert cuerpo["error"]["code"] == codigo
    assert isinstance(cuerpo["error"]["message"], str)


# ---------------------------------------------------------------------------
# R11 — POST /api/v1/pedidos
# ---------------------------------------------------------------------------


def test_post_valido_devuelve_201_y_montos_como_texto(url):
    status, cuerpo = pedir(
        url,
        "POST",
        RUTA,
        compra(),
    )

    assert status == 201
    assert isinstance(cuerpo["id"], int)
    assert cuerpo["subtotal"] == "24999.90"
    assert cuerpo["descuento"] == "0.00"
    assert cuerpo["envio"] == "2500.00"
    assert cuerpo["total"] == "27499.90"


def test_post_con_cupon_y_fecha_valida_devuelve_calculo_correcto(url):
    status, cuerpo = pedir(
        url,
        "POST",
        RUTA,
        compra(
            carrito=[
                {
                    "producto": "remera",
                    "talle": "M",
                    "cantidad": 1,
                }
            ],
            cupon="EGRESADOS2026",
            fecha="2026-11-30",
        ),
    )

    assert status == 201
    assert cuerpo["subtotal"] == "11999.50"
    assert cuerpo["descuento"] == "1799.93"
    assert cuerpo["envio"] == "2500.00"
    assert cuerpo["total"] == "12699.57"


def test_checkout_error_devuelve_422_y_codigo_del_error(url):
    status, cuerpo = pedir(
        url,
        "POST",
        RUTA,
        compra(
            carrito=[
                {
                    "producto": "buzo",
                    "talle": "XXXL",
                    "cantidad": 1,
                }
            ]
        ),
    )

    assert status == 422
    assert_error(cuerpo, "TALLE_INVALIDO")


def test_json_invalido_devuelve_400_json_invalido(url):
    status, cuerpo = pedir(
        url,
        "POST",
        RUTA,
        crudo=b'{"email": "ana@mail.com",',
    )

    assert status == 400
    assert_error(cuerpo, "JSON_INVALIDO")


@pytest.mark.parametrize(
    "cuerpo",
    [
        {
            "zona": "CABA",
            "carrito": [{"producto": "buzo", "talle": "M", "cantidad": 1}],
        },
        {
            "email": "ana@mail.com",
            "carrito": [{"producto": "buzo", "talle": "M", "cantidad": 1}],
        },
        {
            "email": "ana@mail.com",
            "zona": "CABA",
        },
        {
            "email": 123,
            "zona": "CABA",
            "carrito": [{"producto": "buzo", "talle": "M", "cantidad": 1}],
        },
        {
            "email": "ana@mail.com",
            "zona": 123,
            "carrito": [{"producto": "buzo", "talle": "M", "cantidad": 1}],
        },
        {
            "email": "ana@mail.com",
            "zona": "CABA",
            "carrito": "no-es-lista",
        },
    ],
)
def test_datos_faltantes_o_de_tipo_incorrecto_devuelven_400(url, cuerpo):
    status, respuesta = pedir(
        url,
        "POST",
        RUTA,
        cuerpo,
    )

    assert status == 400
    assert_error(respuesta, "DATOS_INCOMPLETOS")


@pytest.mark.parametrize(
    "fecha_invalida",
    [
        "30/11/2026",
        "2026/11/30",
        "2026-13-01",
        "no-es-fecha",
    ],
)
def test_fecha_invalida_devuelve_400_fecha_invalida(url, fecha_invalida):
    status, cuerpo = pedir(
        url,
        "POST",
        RUTA,
        compra(
            cupon="EGRESADOS2026",
            fecha=fecha_invalida,
        ),
    )

    assert status == 400
    assert_error(cuerpo, "FECHA_INVALIDA")


# ---------------------------------------------------------------------------
# R11 — GET /api/v1/pedidos/{id}
# ---------------------------------------------------------------------------


def test_post_y_get_recuperan_el_pedido_completo(url):
    status_post, creado = pedir(
        url,
        "POST",
        RUTA,
        compra(),
    )

    assert status_post == 201

    status_get, pedido = pedir(
        url,
        "GET",
        f"{RUTA}/{creado['id']}",
    )

    assert status_get == 200
    assert pedido == {
        "id": creado["id"],
        "email": "ana@mail.com",
        "zona": "CABA",
        "cupon": None,
        "subtotal": "24999.90",
        "descuento": "0.00",
        "envio": "2500.00",
        "total": "27499.90",
        "items": [
            {
                "producto": "buzo",
                "talle": "M",
                "cantidad": 1,
                "precio_unitario": "24999.90",
            }
        ],
    }


def test_get_de_pedido_inexistente_devuelve_404(url):
    status, cuerpo = pedir(
        url,
        "GET",
        f"{RUTA}/999999",
    )

    assert status == 404
    assert_error(cuerpo, "PEDIDO_INEXISTENTE")


# ---------------------------------------------------------------------------
# R11 — Rutas inexistentes
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("metodo", "ruta"),
    [
        ("GET", "/api/v1/otra"),
        ("GET", "/api/v1/pedidos/no-es-id"),
        ("POST", "/api/v1/otra"),
    ],
)
def test_ruta_inexistente_devuelve_404(url, metodo, ruta):
    status, cuerpo = pedir(
        url,
        metodo,
        ruta,
        compra() if metodo == "POST" else None,
    )

    assert status == 404
    assert_error(cuerpo, "RUTA_INEXISTENTE")
