from datetime import date
from decimal import Decimal, ROUND_HALF_UP


class CheckoutError(Exception):
    def __init__(self, code, mensaje):
        super().__init__(mensaje)
        self.code = code
        self.mensaje = mensaje


CATALOGO = {
    "buzo": Decimal("24999.90"),
    "remera": Decimal("11999.50"),
    "campera": Decimal("47999.99"),
}

TALLES = ["XS", "S", "M", "L", "XL", "XXL"]

CUPONES = {
    "EGRESADOS2026": {
        "tipo": "porcentaje",
        "valor": Decimal("0.15"),
        "vence": date(2026, 11, 30),
    },
    "BIENVENIDA": {
        "tipo": "fijo",
        "valor": Decimal("3000"),
        "minimo": Decimal("20000"),
    },
}

ENVIOS = {
    "CABA": Decimal("2500"),
    "GBA": Decimal("4000"),
    "INTERIOR": Decimal("6500"),
    "RETIRO": Decimal("0"),
}


def validar_item(item):
    producto = item["producto"]

    if not isinstance(producto, str) or producto not in CATALOGO:
        raise CheckoutError(
            "PRODUCTO_INEXISTENTE",
            f"Producto inexistente: {producto!r}",
        )

    talle = item["talle"]

    if not isinstance(talle, str) or talle.strip().upper() not in TALLES:
        raise CheckoutError(
            "TALLE_INVALIDO",
            f"Talle inválido: {talle!r}",
        )

    cantidad = item["cantidad"]

    if (
        isinstance(cantidad, bool)
        or not isinstance(cantidad, int)
        or not (1 <= cantidad <= 10)
    ):
        raise CheckoutError(
            "CANTIDAD_INVALIDA",
            "La cantidad debe ser un entero entre 1 y 10",
        )


def calcular_subtotal(carrito):
    if not isinstance(carrito, (list, tuple)) or len(carrito) == 0:
        raise CheckoutError(
            "CARRITO_VACIO",
            "El carrito no tiene ítems",
        )

    subtotal = Decimal("0")

    for item in carrito:
        validar_item(item)
        subtotal += CATALOGO[item["producto"]] * item["cantidad"]

    return subtotal


def calcular_descuento(
    subtotal,
    cantidad_prendas,
    cupon=None,
    fecha=None,
):
    descuento_cantidad = Decimal("0.00")
    descuento_cupon = Decimal("0.00")

    if cantidad_prendas >= 5:
        descuento_cantidad = (
            subtotal * Decimal("0.10")
        ).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

    if cupon is not None:
        codigo = cupon.strip().upper()

        if codigo != "":
            if codigo not in CUPONES:
                raise CheckoutError(
                    "CUPON_INVALIDO",
                    "El cupón no existe",
                )

            datos = CUPONES[codigo]

            if datos["tipo"] == "porcentaje":
                fecha_actual = fecha if fecha is not None else date.today()

                if fecha_actual > datos["vence"]:
                    raise CheckoutError(
                        "CUPON_VENCIDO",
                        "El cupón está vencido",
                    )

                descuento_cupon = (
                    subtotal * datos["valor"]
                ).quantize(
                    Decimal("0.01"),
                    rounding=ROUND_HALF_UP,
                )

            elif datos["tipo"] == "fijo":
                if subtotal < datos["minimo"]:
                    raise CheckoutError(
                        "CUPON_MINIMO_NO_ALCANZADO",
                        f"El cupón requiere una compra mínima de ${datos['minimo']}",
                    )

                descuento_cupon = datos["valor"].quantize(
                    Decimal("0.01")
                )

    descuento = max(
        descuento_cantidad,
        descuento_cupon,
    )

    if descuento > subtotal:
        descuento = subtotal

    return descuento.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )


def calcular_envio(subtotal_con_descuento, zona):
    zona = zona.strip().upper()

    if zona not in ENVIOS:
        raise CheckoutError(
            "ZONA_INVALIDA",
            f"Zona inválida. Opciones: {', '.join(ENVIOS.keys())}",
        )

    if subtotal_con_descuento >= Decimal("60000"):
        return Decimal("0")

    return ENVIOS[zona]


def calcular_total(
    carrito,
    zona,
    cupon=None,
    fecha=None,
):
    subtotal = calcular_subtotal(carrito)

    prendas = 0

    for item in carrito:
        prendas += item["cantidad"]

    descuento = calcular_descuento(
        subtotal,
        prendas,
        cupon,
        fecha,
    )

    subtotal_con_descuento = subtotal - descuento

    envio = calcular_envio(
        subtotal_con_descuento,
        zona,
    )

    total = subtotal - descuento + envio

    resultado = {
        "subtotal": subtotal,
        "descuento": descuento,
        "envio": envio,
        "total": total.quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        ),
    }

    return resultado