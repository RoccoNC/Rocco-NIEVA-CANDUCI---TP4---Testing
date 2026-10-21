# CASOS.md — Casos de caja negra

Trabajo hecho solo a partir de `ESPECIFICACION.md`, antes de modificar `checkout.py`.

Convenciones:
- Los ítems se escriben como `(producto, talle, cantidad)`.
- Los importes son `Decimal`.
- En cada regla se aísla la variable bajo prueba: lo demás se deja en valores válidos
  (talle `"M"`, cantidad dentro de rango, etc.).

---

## R1 — Catálogo y precios

**Regla:** tres productos con precio fijo: `buzo` $24.999,90, `remera` $11.999,50 y
`campera` $47.999,99. El nombre se escribe exactamente así, en minúscula. El precio sale
siempre del catálogo y un precio propio del ítem se ignora. Un producto que no está en el
catálogo da `PRODUCTO_INEXISTENTE`.

### Particiones

| ID | Partición | Tipo |
|---|---|---|
| P1 | Producto `buzo` | Válida |
| P2 | Producto `remera` | Válida |
| P3 | Producto `campera` | Válida |
| P4 | Nombre que no está en el catálogo (`"zapatillas"`) | Inválida |
| P5 | Nombre correcto con otra capitalización (`"BUZO"`, `"Buzo"`) | Inválida |
| P6 | Nombre correcto con espacios alrededor (`" buzo "`) | Inválida |
| P7 | Nombre vacío (`""`) | Inválida |
| P8 | Valor que no es texto (`None`, `123`) | Inválida |
| P9 | Ítem con precio propio (`"precio": 1`) | Válida (el precio se ignora) |
| P10 | Ítem con claves extra (`"color": "rojo"`) | Válida (se ignoran) |

### Valores límite

- **Coincidencia exacta del texto:** `"buzo"` es válido; `"buzo "`, `" buzo"` y `"Buzo"`
  están a un carácter de distancia y son inválidos.
- **Centavos exactos:** los precios terminan en `.90`, `.50` y `.99`. El subtotal tiene que
  ser un `Decimal` exacto. Con `float`, 24999.90 × 3 da 74999.70000000001.

### Casos

| ID | Partición | Entrada | Resultado esperado |
|---|---|---|---|
| R1-01 | P1 | `calcular_subtotal([(buzo, M, 1)])` | `Decimal("24999.90")` |
| R1-02 | P2 | `calcular_subtotal([(remera, M, 1)])` | `Decimal("11999.50")` |
| R1-03 | P3 | `calcular_subtotal([(campera, M, 1)])` | `Decimal("47999.99")` |
| R1-04 | P1 + centavos exactos | `calcular_subtotal([(buzo, M, 3)])` | `Decimal("74999.70")` |
| R1-05 | P1, P2 y P3 juntos | `calcular_subtotal([(buzo, M, 1), (remera, M, 1), (campera, M, 1)])` | `Decimal("84999.39")` |
| R1-06 | P4 | `validar_item({"producto": "zapatillas", "talle": "M", "cantidad": 1})` | `CheckoutError`, `code="PRODUCTO_INEXISTENTE"` |
| R1-07 | P5 | `validar_item({"producto": "BUZO", "talle": "M", "cantidad": 1})` | `PRODUCTO_INEXISTENTE` |
| R1-08 | P5 | `validar_item({"producto": "Buzo", "talle": "M", "cantidad": 1})` | `PRODUCTO_INEXISTENTE` |
| R1-09 | P6 | `validar_item({"producto": " buzo ", "talle": "M", "cantidad": 1})` | `PRODUCTO_INEXISTENTE` |
| R1-10 | P7 | `validar_item({"producto": "", "talle": "M", "cantidad": 1})` | `PRODUCTO_INEXISTENTE` |
| R1-11 | P8 | `validar_item({"producto": None, "talle": "M", "cantidad": 1})` | `PRODUCTO_INEXISTENTE` (nunca otra excepción) |
| R1-12 | P9 | `calcular_subtotal([{"producto": "buzo", "talle": "M", "cantidad": 1, "precio": 1}])` | `Decimal("24999.90")` |
| R1-13 | P9 | mismo ítem con `"precio": 0` y con `"precio": -500` | `Decimal("24999.90")` en ambos |
| R1-14 | P10 | `calcular_subtotal([{"producto": "remera", "talle": "M", "cantidad": 1, "color": "rojo"}])` | `Decimal("11999.50")` |
| R1-15 | Orden de validación (sección 3) | `validar_item({"producto": "zapatillas", "talle": "XXXL", "cantidad": 99})` | `PRODUCTO_INEXISTENTE` (el producto se valida antes que talle y cantidad) |

### Decisiones de interpretación

- **P6:** R2 dice que se ignoran los espacios en el talle, pero R1 no dice lo mismo del
  producto y pide "exactamente así". Se toma como inválido.
- **P8:** la sección 1 dice que ante cualquier dato inválido se lanza `CheckoutError` y
  nunca otro tipo de excepción. Un producto `None` o numérico da `PRODUCTO_INEXISTENTE`,
  no un `TypeError`.


---

## R2 — Talles

**Regla:** los talles válidos son `XS`, `S`, `M`, `L`, `XL` y `XXL`. No se distingue
mayúscula de minúscula (`"m"` es válido) y se ignoran los espacios al principio y al final
(`"  M "` es válido). Cualquier otro valor da `TALLE_INVALIDO`.

### Particiones

| ID | Partición | Tipo |
|---|---|---|
| P1 | Cada talle válido en mayúscula (`XS`, `S`, `M`, `L`, `XL`, `XXL`) | Válida |
| P2 | Talle válido en minúscula (`"m"`, `"xxl"`) | Válida |
| P3 | Talle válido con mayúsculas y minúsculas mezcladas (`"Xl"`, `"xL"`) | Válida |
| P4 | Talle válido con espacios al principio y/o al final (`"  M "`) | Válida |
| P5 | Talle válido con minúscula y espacios a la vez (`" xl "`) | Válida |
| P6 | Talle que no existe (`"XXXL"`, `"XXS"`, `"Z"`, `"Medium"`) | Inválida |
| P7 | Talle vacío (`""`) | Inválida |
| P8 | Talle de solo espacios (`"   "`) | Inválida |
| P9 | Talle válido con espacios en el medio (`"X L"`) | Inválida |
| P10 | Valor que no es texto (`None`, `5`) | Inválida |

### Valores límite

- **Extremos de la escala:** `XXL` es válido y `XXXL` no; `XS` es válido y `XXS` no.
- **Vacío después de recortar:** `""` y `"   "` quedan vacíos, y ninguno es un talle.
- **Espacios:** `" M"` y `"M "` son válidos (espacio solo de un lado), pero `"X L"` no
  (el espacio está en el medio, no en el borde).

### Casos

Producto `buzo` y cantidad `1` en todos, para aislar R2. La función probada es
`validar_item`, salvo donde se indica.

| ID | Partición | Talle de entrada | Resultado esperado |
|---|---|---|---|
| R2-01 | P1 | `"XS"` | no lanza error |
| R2-02 | P1 | `"S"` | no lanza error |
| R2-03 | P1 | `"M"` | no lanza error |
| R2-04 | P1 | `"L"` | no lanza error |
| R2-05 | P1 | `"XL"` | no lanza error |
| R2-06 | P1 (límite superior) | `"XXL"` | no lanza error |
| R2-07 | P2 | `"m"` | no lanza error |
| R2-08 | P2 | `"xxl"` | no lanza error |
| R2-09 | P3 | `"Xl"` | no lanza error |
| R2-10 | P4 | `"  M "` | no lanza error |
| R2-11 | P4 (espacio de un solo lado) | `" M"` y `"M "` | no lanza error en ninguno |
| R2-12 | P5 | `" xl "` | no lanza error |
| R2-13 | P6 (límite superior) | `"XXXL"` | `CheckoutError`, `code="TALLE_INVALIDO"` |
| R2-14 | P6 (límite inferior) | `"XXS"` | `TALLE_INVALIDO` |
| R2-15 | P6 | `"Z"` | `TALLE_INVALIDO` |
| R2-16 | P6 | `"Medium"` | `TALLE_INVALIDO` |
| R2-17 | P7 | `""` | `TALLE_INVALIDO` |
| R2-18 | P8 | `"   "` | `TALLE_INVALIDO` |
| R2-19 | P9 | `"X L"` | `TALLE_INVALIDO` |
| R2-20 | P10 | `None` | `TALLE_INVALIDO` (nunca otra excepción) |
| R2-21 | P10 | `5` | `TALLE_INVALIDO` (nunca otra excepción) |
| R2-22 | P2 + efecto en el cálculo | `calcular_subtotal([(buzo, "m", 1)])` | `Decimal("24999.90")` (el talle no cambia el precio) |
| R2-23 | Orden de validación (sección 3) | `validar_item({"producto": "buzo", "talle": "XXXL", "cantidad": 99})` | `TALLE_INVALIDO` (el talle se valida antes que la cantidad) |
| R2-24 | Orden de validación (sección 3) | `validar_item({"producto": "zapatillas", "talle": "XXXL", "cantidad": 1})` | `PRODUCTO_INEXISTENTE` (el producto se valida antes que el talle) |

### Decisiones de interpretación

- **P9:** la regla habla de espacios "al principio y al final", así que los espacios
  internos no se recortan y el talle no coincide con ninguno válido.
- **P10:** igual que en R1, la sección 1 dice que nunca se lanza otro tipo de excepción
  que `CheckoutError`. Un talle `None` o numérico da `TALLE_INVALIDO`, no un
  `AttributeError`.
- **Qué se considera "espacio":** la especificación solo menciona espacios. No se
  incluyen tabuladores ni saltos de línea en los casos para no inventar comportamiento
  que el documento no define.
- **Relación con R4:** normalizar el talle (pasarlo a mayúscula y recortarlo) no debe
  modificar el ítem original. Eso se prueba en la sección de R4.
---

## R3 — Cantidad

**Regla:** la cantidad es un número entero entre **1 y 10, ambos inclusive**. Cualquier otro
valor, incluidos los no enteros, da `CANTIDAD_INVALIDA`.

### Particiones

| ID | Partición | Tipo |
|---|---|---|
| P1 | Entero dentro del rango, de 1 a 10 | Válida |
| P2 | Entero menor que 1: cero | Inválida |
| P3 | Entero menor que 1: negativo (`-1`, `-10`) | Inválida |
| P4 | Entero mayor que 10 (`11`, `100`) | Inválida |
| P5 | Número no entero (`2.5`, `0.5`, `10.5`) | Inválida |
| P6 | Texto, aunque parezca un número (`"3"`) | Inválida |
| P7 | `None` | Inválida |
| P8 | Booleano (`True`) | Inválida |
| P9 | Número especial de punto flotante (`nan`) | Inválida |

### Valores límite

| Límite | Valores a probar | Resultado |
|---|---|---|
| Inferior | `0` / `1` / `2` | inválido / válido / válido |
| Superior | `9` / `10` / `11` | válido / válido / inválido |
| No enteros pegados a los límites | `0.5`, `1.5`, `10.5` | todos inválidos |

### Casos

Producto `buzo` y talle `M` en todos, para aislar R3. La función probada es
`validar_item`, salvo donde se indica.

| ID | Partición | Cantidad de entrada | Resultado esperado |
|---|---|---|---|
| R3-01 | P1 (límite inferior) | `1` | no lanza error |
| R3-02 | P1 (justo arriba del límite inferior) | `2` | no lanza error |
| R3-03 | P1 (valor medio) | `5` | no lanza error |
| R3-04 | P1 (justo debajo del límite superior) | `9` | no lanza error |
| R3-05 | P1 (límite superior) | `10` | no lanza error |
| R3-06 | P2 (justo debajo del límite inferior) | `0` | `CheckoutError`, `code="CANTIDAD_INVALIDA"` |
| R3-07 | P3 | `-1` | `CANTIDAD_INVALIDA` |
| R3-08 | P3 | `-10` | `CANTIDAD_INVALIDA` |
| R3-09 | P4 (justo arriba del límite superior) | `11` | `CANTIDAD_INVALIDA` |
| R3-10 | P4 | `100` | `CANTIDAD_INVALIDA` |
| R3-11 | P5 | `2.5` | `CANTIDAD_INVALIDA` |
| R3-12 | P5 (entre 0 y 1) | `0.5` | `CANTIDAD_INVALIDA` |
| R3-13 | P5 (entre 10 y 11) | `10.5` | `CANTIDAD_INVALIDA` |
| R3-14 | P6 | `"3"` | `CANTIDAD_INVALIDA` (nunca otra excepción) |
| R3-15 | P7 | `None` | `CANTIDAD_INVALIDA` (nunca otra excepción) |
| R3-16 | P8 | `True` | `CANTIDAD_INVALIDA` |
| R3-17 | P9 | `float("nan")` | `CANTIDAD_INVALIDA` (nunca otra excepción) |
| R3-18 | P1 + efecto en el cálculo | `calcular_subtotal([(buzo, M, 10)])` | `Decimal("249999.00")` |
| R3-19 | P1 + efecto en el cálculo | `calcular_subtotal([(remera, M, 10)])` | `Decimal("119995.00")` |
| R3-20 | P4 vía `calcular_subtotal` | `calcular_subtotal([(buzo, M, 11)])` | `CANTIDAD_INVALIDA` (el error se propaga) |
| R3-21 | Orden de validación (sección 3) | `validar_item({"producto": "buzo", "talle": "M", "cantidad": 0})` | `CANTIDAD_INVALIDA` (con producto y talle válidos, el único error es la cantidad) |
| R3-22 | Orden entre ítems (sección 3) | carrito con `(buzo, M, 0)` primero y `(zapatillas, M, 1)`

---

## R4 — Carrito

**Regla:** el carrito debe tener al menos un ítem, si no da `CARRITO_VACIO`. Ninguna
función modifica el carrito que recibe: el frontend reutiliza ese objeto y espera
encontrarlo igual.

### Particiones

| ID | Partición | Tipo |
|---|---|---|
| P1 | Carrito con exactamente un ítem | Válida |
| P2 | Carrito con varios ítems de productos distintos | Válida |
| P3 | Carrito con el mismo producto repetido en dos ítems (distinto talle) | Válida |
| P4 | Carrito con muchas prendas en total (más de 10 sumando ítems) | Válida |
| P5 | Carrito vacío (`[]`) | Inválida |
| P6 | Carrito que no es una lista (`None`) | Inválida |
| P7 | Ejecución exitosa: el carrito original no cambia | Efecto lateral |
| P8 | Ejecución con error: el carrito original no cambia | Efecto lateral |

### Valores límite

| Límite | Valores a probar | Resultado |
|---|---|---|
| Cantidad de ítems | 0 / 1 / 2 | inválido / válido / válido |
| Prendas en total | 10 en un ítem / 20 repartidas en dos ítems | ambos válidos (el límite de 10 es **por ítem**, R3) |

### Casos

Talle `M` y cantidades válidas salvo que se indique. Para los casos de no modificación, la
comprobación es: **el carrito después de la llamada es igual, en contenido, orden, claves
y valores, a una copia hecha antes de llamar.**

| ID | Partición | Entrada | Resultado esperado |
|---|---|---|---|
| R4-01 | P1 (límite inferior válido) | `calcular_subtotal([(buzo, M, 1)])` | `Decimal("24999.90")` |
| R4-02 | P2 | `calcular_subtotal([(buzo, M, 1), (remera, M, 1)])` | `Decimal("36999.40")` |
| R4-03 | P3 | `calcular_subtotal([(buzo, M, 1), (buzo, L, 2)])` | `Decimal("74999.70")` |
| R4-04 | P4 | `calcular_subtotal([(buzo, M, 10), (remera, M, 10)])` | `Decimal("369994.00")` |
| R4-05 | P5 (límite inferior inválido) | `calcular_subtotal([])` | `CheckoutError`, `code="CARRITO_VACIO"` |
| R4-06 | P5 | `calcular_total([], "CABA")` | `CARRITO_VACIO` |
| R4-07 | P6 | `calcular_total(None, "CABA")` | `CheckoutError` (nunca otra excepción) |
| R4-08 | P7, `calcular_subtotal` | carrito `[(buzo, " m ", 2)]` | el carrito queda con el talle `" m "`, sin pasar a `"M"` |
| R4-09 | P7, `calcular_total` | carrito `[(buzo, " m ", 2)]`, zona `"CABA"` | resultado correcto y el carrito queda igual |
| R4-10 | P7, `calcular_total` con cupón | carrito de 2 ítems, cupón `"EGRESADOS2026"`, fecha vigente | resultado correcto y el carrito queda igual |
| R4-11 | P7, `validar_item` | ítem `(buzo, " m ", 1)` | no lanza error y el ítem queda con `" m "` |
| R4-12 | P7, claves extra | ítem con `"precio": 1` y `"color": "rojo"` | después de `calcular_subtotal`, el ítem conserva esas dos claves con los mismos valores |
| R4-13 | P7, orden y largo | carrito con 3 ítems | después de `calcular_total`, mismo largo y mismo orden de ítems |
| R4-14 | P8, error de talle | `validar_item` con ítem `(buzo, " xxxl ", 1)` | lanza `TALLE_INVALIDO` y el ítem queda con `" xxxl "` |
| R4-15 | P8, error en el segundo ítem | `calcular_subtotal([(buzo, "m", 1), (zapatillas, "m", 1)])` | lanza `PRODUCTO_INEXISTENTE` y el primer ítem sigue con `"m"` (no llegó a normalizarse) |
| R4-16 | P8, error de cupón | `calcular_total` con carrito válido y cupón `"NOEXISTE"` | lanza `CUPON_INVALIDO` y el carrito queda igual |
| R4-17 | P8, error de zona | `calcular_total` con carrito válido y zona `"MARTE"` | lanza `ZONA_INVALIDA` y el carrito queda igual |
| R4-18 | Orden de validación (sección 3) | `calcular_total([], "MARTE")` | `CARRITO_VACIO` (el carrito vacío se informa antes que la zona inválida) |
| R4-19 | Orden de validación (sección 3) | `calcular_total([], "CABA", "NOEXISTE")` | `CARRITO_VACIO` (antes que el cupón inválido) |
| R4-20 | Orden de validación (sección 3) | `calcular_total([(zapatillas, M, 1)], "MARTE", "NOEXISTE")` | `PRODUCTO_INEXISTENTE` (el ítem se informa antes que cupón y zona) |

### Decisiones de interpretación

- **P6 (carrito `None`):** la especificación dice "al menos un ítem, si no, `CARRITO_VACIO`"
  y que ante cualquier dato inválido se lanza `CheckoutError`. Un carrito `None` no
  tiene ítems, así que `CARRITO_VACIO` es el código que mejor encaja. En los tests
  unitarios se comprueba solo que sea `CheckoutError`, para no depender de esa
  lectura.
- **Qué funciones reciben el carrito:** `calcular_subtotal` y `calcular_total` reciben la
  lista, y `validar_item` recibe un ítem. `calcular_descuento` y `calcular_envio` reciben
  números y texto, así que no hay nada que mutar en ellas.
- **R4-08, R4-11 y R4-14:** el talle se normaliza para comparar (R2), pero esa
  normalización no puede escribirse de vuelta en el ítem que recibió la función.
- **R4-15:** es el caso más delicado. Si una función normaliza el primer ítem y recién
  después falla en el segundo, el carrito queda modificado aunque la llamada haya dado
  error.
- **No se define un máximo de ítems en el carrito.** Solo está limitada la cantidad por
  ítem (R3), por eso R4-04 es válido.

---

## R5 — Descuento por cantidad

**Regla:** si la cantidad total de prendas del carrito (la suma de las cantidades de todos
los ítems) es **5 o más**, se aplica un **10%** sobre el subtotal. El resultado se redondea
al centavo con redondeo comercial (R7): el medio centavo sube.

### Particiones

| ID | Partición | Tipo |
|---|---|---|
| P1 | Menos de 5 prendas en total (1 a 4) | Sin descuento |
| P2 | Exactamente 5 prendas | Con descuento |
| P3 | Más de 5 prendas (6 a 10) en un solo ítem | Con descuento |
| P4 | 5 o más prendas repartidas en varios ítems, con cada ítem por debajo de 5 | Con descuento |
| P5 | Menos de 5 prendas repartidas en varios ítems | Sin descuento |
| P6 | Total mayor que 10, sumando varios ítems (11 a 20) | Con descuento |
| P7 | Descuento cuyo cálculo da un medio centavo exacto | Redondeo |
| P8 | Descuento cuyo cálculo da menos de medio centavo | Redondeo |

### Valores límite

| Límite | Valores a probar | Resultado |
|---|---|---|
| Umbral de prendas | 4 / 5 / 6 | sin descuento / con 10% / con 10% |
| Redondeo | resultado del 10% con exactamente medio centavo | sube al centavo siguiente |
| Máximo del carrito | 10 + 10 prendas (20 en total) | un único 10%, sin escalones |

### Casos

Se prueba `calcular_descuento(subtotal, cantidad_prendas)` sin cupón, y `calcular_total`
para ver el efecto completo. Los subtotales de los ejemplos son los que resultan de los
precios del catálogo (R1) o valores directos cuando se indica.

| ID | Partición | Entrada | Resultado esperado |
|---|---|---|---|
| R5-01 | P1 | `calcular_descuento(Decimal("24999.90"), 1)` | `Decimal("0.00")` |
| R5-02 | P1 (justo debajo del umbral) | `calcular_descuento(Decimal("100000.00"), 4)` | `Decimal("0.00")` |
| R5-03 | P2 (umbral) | `calcular_descuento(Decimal("100000.00"), 5)` | `Decimal("10000.00")` |
| R5-04 | P3 (justo arriba del umbral) | `calcular_descuento(Decimal("100000.00"), 6)` | `Decimal("10000.00")` |
| R5-05 | P3 (máximo en un ítem) | `calcular_descuento(Decimal("249999.00"), 10)` | `Decimal("24999.90")` |
| R5-06 | P2 con precios reales | `calcular_total([(buzo, M, 5)], "CABA")` | `descuento = Decimal("12499.95")` (10% de $124.999,50) |
| R5-07 | P3 con precios reales | `calcular_total([(buzo, M, 7)], "CABA")` | `descuento = Decimal("17499.93")` (10% de $174.999,30) |
| R5-08 | P4, ítems por debajo de 5 | `calcular_total([(buzo, M, 3), (remera, M, 2)], "CABA")` | subtotal `Decimal("98998.70")`, descuento `Decimal("9899.87")` |
| R5-09 | P5 | `calcular_total([(buzo, M, 2), (remera, S, 2)], "CABA")` | subtotal `Decimal("73998.80")`, descuento `Decimal("0.00")` |
| R5-10 | P5 (4 prendas en 4 ítems) | `calcular_total([(buzo, M, 1), (remera, M, 1), (campera, M, 1), (buzo, L, 1)], "CABA")` | descuento `Decimal("0.00")` |
| R5-11 | P6 | `calcular_total([(buzo, M, 10), (remera, M, 10)], "CABA")` | subtotal `Decimal("369994.00")`, descuento `Decimal("36999.40")` |
| R5-12 | P7, medio centavo que sube | `calcular_descuento(Decimal("100.05"), 5)` | `Decimal("10.01")` (10% = 10,005) |
| R5-13 | P7 con precios reales | `calcular_total([(campera, M, 5)], "CABA")`