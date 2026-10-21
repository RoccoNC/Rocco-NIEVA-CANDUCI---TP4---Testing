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


---

## R6 — Cupones

**Regla:** existen solo dos cupones.

| Código | Beneficio | Condición |
|---|---|---|
| `EGRESADOS2026` | 15% | Válido hasta el 30/11/2026 inclusive |
| `BIENVENIDA` | $ 3.000 | Subtotal de $ 20.000 o más |

- No se distingue mayúscula de minúscula y se ignoran los espacios alrededor.
- `None`, `""` o solo espacios equivalen a no usar cupón (no es error).
- Código inexistente → `CUPON_INVALIDO`. `EGRESADOS2026` vencido → `CUPON_VENCIDO`.
  `BIENVENIDA` bajo el mínimo → `CUPON_MINIMO_NO_ALCANZADO`.
- El cupón no se acumula con el descuento por cantidad (R5): se calculan los dos y se
  aplica el mayor.
- El descuento nunca puede superar el subtotal.
- Si no se recibe `fecha`, se usa la fecha del día de la llamada.
- Los descuentos porcentuales se redondean al centavo con redondeo comercial (R7).

### Particiones

| ID | Partición | Tipo |
|---|---|---|
| P1 | `EGRESADOS2026` con fecha anterior al 30/11/2026 | Válida |
| P2 | `EGRESADOS2026` en el último día de vigencia (30/11/2026) | Válida |
| P3 | `EGRESADOS2026` con fecha posterior al 30/11/2026 | Inválida (vencido) |
| P4 | `BIENVENIDA` con subtotal mayor que $ 20.000 | Válida |
| P5 | `BIENVENIDA` con subtotal exactamente $ 20.000 | Válida |
| P6 | `BIENVENIDA` con subtotal menor que $ 20.000 | Inválida (mínimo) |
| P7 | `BIENVENIDA` con cualquier fecha (no tiene vencimiento) | Válida |
| P8 | Código válido en minúscula o con mayúsculas mezcladas | Válida |
| P9 | Código válido con espacios alrededor | Válida |
| P10 | `None` | Sin cupón |
| P11 | Texto vacío `""` | Sin cupón |
| P12 | Texto de solo espacios | Sin cupón |
| P13 | Código que no existe (`"DESCUENTO10"`, `"DEBUG100"`) | Inválida |
| P14 | Código casi correcto (`"EGRESADOS2025"`, `"EGRESADOS 2026"`, `"EGRESADOS2026X"`) | Inválida |
| P15 | Valor que no es texto (`123`) | Inválida |
| P16 | Cupón mayor que el descuento por cantidad | Se aplica el cupón |
| P17 | Descuento por cantidad mayor que el cupón | Se aplica el de cantidad |
| P18 | Cupón y descuento por cantidad iguales | Se aplica uno solo, no la suma |
| P19 | Cupón inválido o vencido en un carrito que además tiene descuento por cantidad | Error, sin volver al 10% |
| P20 | `fecha` omitida | Se usa el día de la llamada |
| P21 | Redondeo del 15% con medio centavo exacto | Redondeo |

### Valores límite

| Límite | Valores a probar | Resultado |
|---|---|---|
| Vencimiento de `EGRESADOS2026` | 29/11/2026, 30/11/2026, 01/12/2026 | válido, válido, vencido |
| Mínimo de `BIENVENIDA` | $ 19.999,99 / $ 20.000,00 / $ 20.000,01 | error / válido / válido |
| Cupón vs. cantidad | subtotal $ 25.000 / $ 30.000 / $ 100.000 con 5 prendas y `BIENVENIDA` | gana el cupón ($ 3.000) / empate ($ 3.000) / gana el 10% ($ 10.000) |
| Prendas con cupón porcentual | 4 / 5 prendas con `EGRESADOS2026` | 15% / 15% (el 10% de R5 no se suma) |
| Texto del cupón | `""` y `"   "` / `"A"` | sin cupón / `CUPON_INVALIDO` |

### Casos

Se prueba `calcular_descuento(subtotal, cantidad_prendas, cupon, fecha)` y
`calcular_total`. `VIGENTE` es el 01/10/2026. Salvo que se indique, el carrito es válido
y la zona es `CABA`.

**Cupón `EGRESADOS2026` y su fecha**

| ID | Partición | Entrada | Resultado esperado |
|---|---|---|---|
| R6-01 | P1 | `calcular_descuento(Decimal("100000.00"), 1, "EGRESADOS2026", VIGENTE)` | `Decimal("15000.00")` |
| R6-02 | P1 (un día antes del límite) | igual, con fecha `2026-11-29` | `Decimal("15000.00")` |
| R6-03 | P2 (límite, inclusive) | igual, con fecha `2026-11-30` | `Decimal("15000.00")` |
| R6-04 | P3 (un día después del límite) | igual, con fecha `2026-12-01` | `CheckoutError`, `code="CUPON_VENCIDO"` |
| R6-05 | P3 | igual, con fecha `2027-06-01` | `CUPON_VENCIDO` |

**Cupón `BIENVENIDA` y su mínimo**

| ID | Partición | Entrada | Resultado esperado |
|---|---|---|---|
| R6-06 | P4 | `calcular_descuento(Decimal("24999.90"), 1, "BIENVENIDA", VIGENTE)` | `Decimal("3000.00")` |
| R6-07 | P5 (límite) | `calcular_descuento(Decimal("20000.00"), 1, "BIENVENIDA", VIGENTE)` | `Decimal("3000.00")` |
| R6-08 | P5 (justo arriba del límite) | `calcular_descuento(Decimal("20000.01"), 1, "BIENVENIDA", VIGENTE)` | `Decimal("3000.00")` |
| R6-09 | P6 (justo debajo del límite) | `calcular_descuento(Decimal("19999.99"), 1, "BIENVENIDA", VIGENTE)` | `CheckoutError`, `code="CUPON_MINIMO_NO_ALCANZADO"` |
| R6-10 | P6 con precio real | `calcular_total([(remera, M, 1)], "CABA", "BIENVENIDA", VIGENTE)` (subtotal $ 11.999,50) | `CUPON_MINIMO_NO_ALCANZADO` |
| R6-11 | P7 | `calcular_descuento(Decimal("24999.90"), 1, "BIENVENIDA", date(2030, 1, 1))` | `Decimal("3000.00")` (no vence) |

**Normalización del código**

| ID | Partición | Entrada | Resultado esperado |
|---|---|---|---|
| R6-12 | P8 | cupón `"egresados2026"`, subtotal `100000.00`, 1 prenda, `VIGENTE` | `Decimal("15000.00")` |
| R6-13 | P8 | cupón `"Egresados2026"` | `Decimal("15000.00")` |
| R6-14 | P8 | cupón `"bienvenida"`, subtotal `24999.90` | `Decimal("3000.00")` |
| R6-15 | P9 | cupón `"  EGRESADOS2026 "` | `Decimal("15000.00")` |
| R6-16 | P8 + P9 | cupón `"  bienvenida  "`, subtotal `24999.90` | `Decimal("3000.00")` |

**Sin cupón**

| ID | Partición | Entrada | Resultado esperado |
|---|---|---|---|
| R6-17 | P10 | `calcular_descuento(Decimal("100000.00"), 1, None, VIGENTE)` | `Decimal("0.00")` |
| R6-18 | P11 | cupón `""` | `Decimal("0.00")` (no es error) |
| R6-19 | P12 | cupón `"   "` | `Decimal("0.00")` (no es error) |
| R6-20 | P10, P11, P12 en `calcular_total` | el mismo carrito con cupón `None`, `""` y `"   "` | los tres resultados son idénticos |

**Cupones inválidos**

| ID | Partición | Entrada | Resultado esperado |
|---|---|---|---|
| R6-21 | P13 | cupón `"DESCUENTO10"` | `CheckoutError`, `code="CUPON_INVALIDO"` |
| R6-22 | P13 | cupón `"DEBUG100"` | `CUPON_INVALIDO` |
| R6-23 | P14 | cupón `"EGRESADOS2025"` | `CUPON_INVALIDO` |
| R6-24 | P14 | cupón `"EGRESADOS 2026"` | `CUPON_INVALIDO` |
| R6-25 | P14 | cupón `"EGRESADOS2026X"` | `CUPON_INVALIDO` |
| R6-26 | P15 | cupón `123` | `CheckoutError` (nunca otra excepción) |

**Cupón contra descuento por cantidad (no se acumulan, gana el mayor)**

Estos casos llaman directo a `calcular_descuento`: con los precios del catálogo, 5 prendas
nunca dan un subtotal tan bajo, pero el contrato de la función acepta cualquier subtotal.

| ID | Partición | Entrada | Resultado esperado |
|---|---|---|---|
| R6-27 | P16 | `calcular_descuento(Decimal("100000.00"), 5, "EGRESADOS2026", VIGENTE)` | `Decimal("15000.00")` (no 25.000: no se suman) |
| R6-28 | P16 (justo debajo del empate) | `calcular_descuento(Decimal("25000.00"), 5, "BIENVENIDA", VIGENTE)` | `Decimal("3000.00")` (el 10% daría 2.500) |
| R6-29 | P18 (empate) | `calcular_descuento(Decimal("30000.00"), 5, "BIENVENIDA", VIGENTE)` | `Decimal("3000.00")` (no 6.000) |
| R6-30 | P17 | `calcular_descuento(Decimal("100000.00"), 5, "BIENVENIDA", VIGENTE)` | `Decimal("10000.00")` (el 10% supera a los $ 3.000) |
| R6-31 | Cupón con menos de 5 prendas | `calcular_descuento(Decimal("100000.00"), 4, "EGRESADOS2026", VIGENTE)` | `Decimal("15000.00")` |
| R6-32 | P19, cupón vencido con 5 prendas | `calcular_descuento(Decimal("100000.00"), 5, "EGRESADOS2026", date(2026, 12, 1))` | `CUPON_VENCIDO` (no cae al 10%) |
| R6-33 | P19, cupón inexistente con 5 prendas | `calcular_descuento(Decimal("100000.00"), 5, "NOEXISTE", VIGENTE)` | `CUPON_INVALIDO` (no cae al 10%) |

**Redondeo (R7)**

| ID | Partición | Entrada | Resultado esperado |
|---|---|---|---|
| R6-34 | P21 (ejemplo de la especificación) | `calcular_descuento(Decimal("11999.50"), 1, "EGRESADOS2026", VIGENTE)` | `Decimal("1799.93")` (15% = 1.799,925) |
| R6-35 | P21 | `calcular_descuento(Decimal("24999.90"), 1, "EGRESADOS2026", VIGENTE)` | `Decimal("3749.99")` (15% = 3.749,985) |
| R6-36 | Redondeo sin empate | `calcular_descuento(Decimal("47999.99"), 1, "EGRESADOS2026", VIGENTE)` | `Decimal("7200.00")` (15% = 7.199,9985) |
| R6-37 | Tipo del resultado (R7) | `calcular_descuento(Decimal("100000.00"), 1, "EGRESADOS2026", VIGENTE)` | el resultado es `Decimal`, no `float` |

**Fecha omitida**

Estos casos necesitan simular el día de hoy. Cómo hacerlo se resuelve al escribir los tests
(Parte 3). Acá se define solo el comportamiento esperado.

| ID | Partición | Entrada | Resultado esperado |
|---|---|---|---|
| R6-38 | P20 | `calcular_descuento(Decimal("100000.00"), 1, "EGRESADOS2026")` con hoy = `2026-11-30` | `Decimal("15000.00")` |
| R6-39 | P20 | la misma llamada con hoy = `2026-12-01` | `CUPON_VENCIDO` |
| R6-40 | P20, el "hoy" se evalúa en cada llamada | dos llamadas seguidas en el mismo proceso: primero con hoy = `2026-11-30`, después con hoy = `2026-12-01` | primero `15000.00`, después `CUPON_VENCIDO` |
| R6-41 | P20 en `calcular_total` | `calcular_total([(remera, M, 1)], "CABA", "EGRESADOS2026")` con hoy = `2026-12-01` | `CUPON_VENCIDO` |

**Efecto en el total (R9) y orden de validación**

| ID | Partición | Entrada | Resultado esperado |
|---|---|---|---|
| R6-42 | Ejemplo de la especificación | `calcular_total([(remera, M, 1)], "CABA", "EGRESADOS2026", date(2026, 11, 30))` | subtotal `11999.50`, descuento `1799.93`, envío `2500.00`, total `12699.57` |
| R6-43 | P4 en el total | `calcular_total([(buzo, M, 1)], "CABA", "BIENVENIDA", VIGENTE)` | subtotal `24999.90`, descuento `3000.00`, envío `2500.00`, total `24499.90` |
| R6-44 | P16 en el total | `calcular_total([(buzo, M, 5)], "CABA", "EGRESADOS2026", VIGENTE)` | subtotal `124999.50`, descuento `18749.93`, envío `0.00`, total `106249.57` |
| R6-45 | P16 en el total, con envío pago | `calcular_total([(remera, M, 5)], "CABA", "EGRESADOS2026", VIGENTE)` | subtotal `59997.50`, descuento `8999.63`, envío `2500.00`, total `53497.87` |
| R6-46 | Orden de validación (sección 3) | `calcular_total([(buzo, M, 1)], "MARTE", "NOEXISTE", VIGENTE)` | `CUPON_INVALIDO` (el cupón se informa antes que la zona) |
| R6-47 | Orden de validación (sección 3) | `calcular_total([(buzo, M, 1)], "MARTE", "EGRESADOS2026", date(2026, 12, 1))` | `CUPON_VENCIDO` (antes que la zona) |
| R6-48 | Orden de validación (sección 3) | `calcular_total([(remera, M, 1)], "MARTE", "BIENVENIDA", VIGENTE)` | `CUPON_MINIMO_NO_ALCANZADO` (antes que la zona) |
| R6-49 | Orden de validación (sección 3) | `calcular_total([(zapatillas, M, 1)], "CABA", "NOEXISTE", VIGENTE)` | `PRODUCTO_INEXISTENTE` (el ítem se informa antes que el cupón) |

### Decisiones de interpretación

- **El mínimo de `BIENVENIDA` se mide sobre el subtotal**, antes de aplicar descuentos. La
  regla dice "subtotal de $ 20.000 o más". Por eso R6-09 usa `19999.99` y R6-07 usa
  `20000.00`.
- **El tope "el descuento nunca supera el subtotal"** no se puede alcanzar con los dos
  cupones reales: `BIENVENIDA` exige un subtotal de al menos $ 20.000 y descuenta $ 3.000, y
  el 15% y el 10% son siempre menores que el subtotal. Se verifica de forma indirecta:
  cualquier cupón fuera de los dos (como `DEBUG100`, R6-22) da `CUPON_INVALIDO`, y en todos
  los casos con resultado el descuento es menor que el subtotal.
- **R6-26 (cupón no textual):** igual que en R1 a R3, la sección 1 exige `CheckoutError` ante
  cualquier dato inválido. Un cupón `123` no es ningún código existente. En los tests
  unitarios se comprueba solo que sea `CheckoutError`, sin fijar el `code`.
- **R6-24:** el espacio en el medio de `"EGRESADOS 2026"` no es un espacio "alrededor", así
  que no se recorta.
- **R6-32 y R6-33:** un cupón inválido o vencido es un error aunque el descuento por
  cantidad aplicara. La especificación no dice que se ignore el cupón y se siga con el 10%.
- **Fechas anteriores al 30/11/2026:** la especificación dice "válido hasta el 30/11/2026
  inclusive" y no da fecha de inicio. Cualquier fecha anterior se toma como vigente.
- **R6-40:** "la fecha del día en que se hace la llamada" quiere decir que el día se
  consulta en cada llamada. Un proceso que corre varios días debería comportarse distinto
  de un día al siguiente.
- **R6-28 y R6-29:** no se pueden armar con precios reales, porque 5 prendas ya superan los
  $ 59.000. Se llama directo a `calcular_descuento`, cuyo contrato recibe el subtotal como
  parámetro. Sirven para distinguir "gana el mayor" de "siempre el 10%", "siempre el cupón" o
  "se suman".


---

## R7 — Dinero y redondeo

**Regla:** todos los importes se manejan como `Decimal`, nunca como `float`. Los
descuentos porcentuales se redondean al centavo con redondeo comercial: el medio centavo
redondea hacia arriba. Ejemplo de la especificación: 15% de $ 11.999,50 = $ 1.799,925, que
da **$ 1.799,93**.

### Particiones

| ID | Partición | Tipo |
|---|---|---|
| P1 | Resultado de cada función con valor distinto de cero (`calcular_subtotal`, `calcular_descuento`, `calcular_envio` y los cuatro campos de `calcular_total`) | Tipo `Decimal` |
| P2 | Resultado cero (descuento sin cupón, envío `RETIRO`, envío gratis) | Tipo `Decimal` |
| P3 | Carrito cuyo subtotal con `float` daría error binario (por ejemplo, 7 buzos) | Exactitud |
| P4 | Descuento porcentual que da menos de medio centavo | Redondea hacia abajo |
| P5 | Descuento porcentual que da exactamente medio centavo | Redondea hacia arriba |
| P6 | Descuento porcentual que da más de medio centavo | Redondea hacia arriba |
| P7 | Descuento porcentual que ya es un número exacto de centavos | No cambia |
| P8 | Medio centavo exacto con el dígito anterior impar y con el dígito anterior par | Redondea hacia arriba en ambos |
| P9 | Importe fijo (cupón `BIENVENIDA`, envío) | No se redondea |
| P10 | Total de una compra con descuento redondeado | Consistente con R9 |

### Valores límite

| Límite | Valores a probar | Resultado |
|---|---|---|
| 15% alrededor del medio centavo | subtotal $ 11.999,49 / $ 11.999,50 / $ 11.999,51 | $ 1.799,92 / $ 1.799,93 / $ 1.799,93 |
| 10% alrededor del medio centavo | subtotal $ 100,04 / $ 100,05 / $ 100,06 | $ 10,00 / $ 10,01 / $ 10,01 |
| Dígito anterior al medio centavo | $ 100,05 (10,005, dígito 0 par) y $ 100,25 (10,025, dígito 2 par) | $ 10,01 y $ 10,03 |

### Casos

`VIGENTE` es el 01/10/2026. Las llamadas a `calcular_descuento` con 5 prendas aplican el
10% de R5. Los casos con cupón usan `EGRESADOS2026` (15%) y 1 prenda, salvo que se indique.
Los subtotales de los casos de redondeo se pasan directo a `calcular_descuento`, porque el
contrato de la función acepta cualquier subtotal.

**Tipo `Decimal`**

| ID | Partición | Entrada | Resultado esperado |
|---|---|---|---|
| R7-01 | P1 | `calcular_subtotal([(buzo, M, 1)])` | el resultado es `Decimal`, con valor `24999.90` |
| R7-02 | P1 | `calcular_descuento(Decimal("100000.00"), 1, "EGRESADOS2026", VIGENTE)` | el resultado es `Decimal`, con valor `15000.00` |
| R7-03 | P1 | `calcular_envio(Decimal("10000.00"), "CABA")` | el resultado es `Decimal`, con valor `2500.00` |
| R7-04 | P1 | `calcular_total([(buzo, M, 5)], "CABA", "EGRESADOS2026", VIGENTE)` | `subtotal`, `descuento`, `envio` y `total` son los cuatro `Decimal` |
| R7-05 | P2, descuento cero | `calcular_descuento(Decimal("100000.00"), 1, None, VIGENTE)` | el resultado es `Decimal`, con valor `0.00` |
| R7-06 | P2, envío `RETIRO` | `calcular_total([(remera, M, 1)], "RETIRO", None, VIGENTE)` | `descuento`, `envio` y `total` son `Decimal`, con valores `0.00`, `0.00` y `11999.50` |
| R7-07 | P2, envío gratis | `calcular_envio(Decimal("60000.00"), "CABA")` | el resultado es `Decimal`, con valor `0.00` |

**Exactitud**

| ID | Partición | Entrada | Resultado esperado |
|---|---|---|---|
| R7-08 | P3 | `calcular_subtotal([(buzo, M, 7)])` | `Decimal("174999.30")` (con `float` da 174999.30000000002) |
| R7-09 | P3 | `calcular_subtotal([(campera, M, 10)])` | `Decimal("479999.90")` |
| R7-10 | P3 | `calcular_subtotal([(buzo, M, 3), (remera, M, 2)])` | `Decimal("98998.70")` |
| R7-11 | P3 en el total | `calcular_total([(buzo, M, 7)], "CABA", None, VIGENTE)` | subtotal `174999.30`, descuento `17499.93`, envío `0.00`, total `157499.37` |

**Redondeo del 15% (cupón `EGRESADOS2026`)**

| ID | Partición | Subtotal de entrada | Resultado esperado |
|---|---|---|---|
| R7-12 | P4 (justo debajo del medio centavo) | `Decimal("11999.49")` | `Decimal("1799.92")` (15% = 1.799,9235) |
| R7-13 | P5 (medio centavo exacto, ejemplo de la especificación) | `Decimal("11999.50")` | `Decimal("1799.93")` (15% = 1.799,925) |
| R7-14 | P6 (justo arriba del medio centavo) | `Decimal("11999.51")` | `Decimal("1799.93")` (15% = 1.799,9265) |
| R7-15 | P5 con precio real | `Decimal("24999.90")` | `Decimal("3749.99")` (15% = 3.749,985) |
| R7-16 | P6 con precio real | `Decimal("47999.99")` | `Decimal("7200.00")` (15% = 7.199,9985) |
| R7-17 | P4 | `Decimal("100.03")` | `Decimal("15.00")` (15% = 15,0045) |
| R7-18 | P7 | `Decimal("100000.00")` | `Decimal("15000.00")` (15% exacto) |

**Redondeo del 10% (descuento por cantidad, sin cupón, 5 prendas)**

| ID | Partición | Subtotal de entrada | Resultado esperado |
|---|---|---|---|
| R7-19 | P4 (justo debajo del medio centavo) | `Decimal("100.04")` | `Decimal("10.00")` (10% = 10,004) |
| R7-20 | P5 (medio centavo exacto) | `Decimal("100.05")` | `Decimal("10.01")` (10% = 10,005) |
| R7-21 | P6 (justo arriba del medio centavo) | `Decimal("100.06")` | `Decimal("10.01")` (10% = 10,006) |
| R7-22 | P8 (medio centavo exacto, dígito anterior par) | `Decimal("100.25")` | `Decimal("10.03")` (10% = 10,025) |

**Importes fijos y total**

| ID | Partición | Entrada | Resultado esperado |
|---|---|---|---|
| R7-23 | P9 | `calcular_descuento(Decimal("24999.90"), 1, "BIENVENIDA", VIGENTE)` | `Decimal("3000.00")` (importe fijo, sin redondeo) |
| R7-24 | P10 | `calcular_total([(remera, M, 5)], "CABA", "EGRESADOS2026", VIGENTE)` | subtotal `59997.50`, descuento `8999.63` (15% = 8.999,625), envío `2500.00`, total `53497.87` |
| R7-25 | P10 (suma exacta) | el mismo cálculo | `total == subtotal - descuento + envio`, comparado como `Decimal`, sin diferencia de centavos |
| R7-26 | P10, ejemplo de la sección 5 | `calcular_total([(buzo, M, 2)], "CABA", None, VIGENTE)` | subtotal `49999.80`, descuento `0.00`, envío `2500.00`, total `52499.80` |

### Decisiones de interpretación

- **Comparación por valor:** `Decimal("2500")` y `Decimal("2500.00")` son iguales. Los tests
  unitarios comparan el valor y, aparte, el tipo (`Decimal`, no `float`). El formato con dos
  decimales en texto (`"2500.00"`) aparece en la API (R11), y se prueba en esa sección.
- **Qué se redondea:** solo los descuentos porcentuales, que son los únicos que pueden
  producir más de dos decimales. El subtotal (precio con dos decimales por una cantidad
  entera), el cupón fijo y el envío ya son centavos exactos. Por eso el total no necesita un
  redondeo propio y R7-25 exige que la suma sea exacta.
- **Redondeo comercial contra otros redondeos:** los casos R7-13, R7-15, R7-20 y R7-22 son
  medios centavos exactos. Un redondeo "al par" daría 1.799,92, 3.749,98, 10,00 y 10,02, un
  truncado daría un centavo menos, y solo el redondeo comercial da los valores de la
  tabla. Los pares con dígito anterior par e impar (R7-13 con 2 y R7-20 con 0) comprueban
  que no se esté usando el redondeo al par.
- **P3:** los precios con centavos no se representan exactos en `float`. R7-08 muestra el
  error de 7 buzos y sirve para detectar si en algún punto se pasó por `float`.
- **Entradas `Decimal`:** el contrato de las funciones recibe el subtotal como `Decimal`,
  por eso los casos de redondeo lo pasan así. La especificación no define qué pasa si
  llega un `float`, y no se escribe ningún test sobre eso.


---

## R8 — Envío

**Regla:**

| Zona | Costo |
|---|---|
| `CABA` | $ 2.500 |
| `GBA` | $ 4.000 |
| `INTERIOR` | $ 6.500 |
| `RETIRO` | $ 0 (retiro en el colegio) |

- No se distingue mayúscula de minúscula y se ignoran los espacios alrededor.
- El envío es **gratis** si el subtotal **ya con el descuento aplicado** es de
  **$ 60.000 o más**.
- Zona que no existe → `ZONA_INVALIDA`.

### Particiones

| ID | Partición | Tipo |
|---|---|---|
| P1 | Zona `CABA` | Válida |
| P2 | Zona `GBA` | Válida |
| P3 | Zona `INTERIOR` | Válida |
| P4 | Zona `RETIRO` | Válida |
| P5 | Zona válida en minúscula o con mayúsculas mezcladas (`"caba"`, `"Gba"`) | Válida |
| P6 | Zona válida con espacios alrededor (`" INTERIOR "`) | Válida |
| P7 | Zona que no existe (`"MARTE"`, `"CABA2"`, `"Buenos Aires"`) | Inválida |
| P8 | Zona vacía (`""`) | Inválida |
| P9 | Zona de solo espacios (`"   "`) | Inválida |
| P10 | Zona válida con un espacio en el medio (`"C ABA"`) | Inválida |
| P11 | Valor que no es texto (`None`, `5`) | Inválida |
| P12 | Subtotal con descuento menor que $ 60.000 | Paga la tarifa de la zona |
| P13 | Subtotal con descuento exactamente $ 60.000 | Envío gratis |
| P14 | Subtotal con descuento mayor que $ 60.000 | Envío gratis |
| P15 | Subtotal sin descuento de $ 60.000 o más, pero con descuento menor que $ 60.000 | Paga la tarifa de la zona |
| P16 | `RETIRO` con subtotal bajo | $ 0 (no es un cobro) |
| P17 | Zona inválida con un subtotal que daría envío gratis | Error |

### Valores límite

| Límite | Valores a probar | Resultado |
|---|---|---|
| Envío gratis | subtotal con descuento $ 59.999,99 / $ 60.000,00 / $ 60.000,01 | paga la tarifa / gratis / gratis |
| Envío gratis en cada zona | `CABA`, `GBA` e `INTERIOR` con $ 59.999,99 y con $ 60.000,00 | tarifa propia / gratis |
| Texto de la zona | `""` y `"   "` / `"A"` | `ZONA_INVALIDA` en ambos |
| Con precios reales | remera + campera = $ 59.999,49 | paga el envío (el límite está a 51 centavos) |

### Casos

La función directa es `calcular_envio(subtotal_con_descuento, zona)`. Los casos con
`calcular_total` usan el formato de R7. `VIGENTE` es el 01/10/2026.

**Tarifas y normalización**

| ID | Partición | Entrada | Resultado esperado |
|---|---|---|---|
| R8-01 | P1 | `calcular_envio(Decimal("10000.00"), "CABA")` | `Decimal("2500.00")` |
| R8-02 | P2 | `calcular_envio(Decimal("10000.00"), "GBA")` | `Decimal("4000.00")` |
| R8-03 | P3 | `calcular_envio(Decimal("10000.00"), "INTERIOR")` | `Decimal("6500.00")` |
| R8-04 | P4 | `calcular_envio(Decimal("10000.00"), "RETIRO")` | `Decimal("0.00")` |
| R8-05 | P5 | `calcular_envio(Decimal("10000.00"), "caba")` | `Decimal("2500.00")` |
| R8-06 | P5 | `calcular_envio(Decimal("10000.00"), "Gba")` | `Decimal("4000.00")` |
| R8-07 | P6 | `calcular_envio(Decimal("10000.00"), "  interior ")` | `Decimal("6500.00")` |
| R8-08 | P5 + P6 con `RETIRO` | `calcular_envio(Decimal("10000.00"), " retiro ")` | `Decimal("0.00")` (no lanza error) |

**Zonas inválidas**

| ID | Partición | Entrada | Resultado esperado |
|---|---|---|---|
| R8-09 | P7 | `calcular_envio(Decimal("10000.00"), "MARTE")` | `CheckoutError`, `code="ZONA_INVALIDA"` |
| R8-10 | P7 | zona `"CABA2"` | `ZONA_INVALIDA` |
| R8-11 | P7 | zona `"Buenos Aires"` | `ZONA_INVALIDA` |
| R8-12 | P8 | zona `""` | `ZONA_INVALIDA` |
| R8-13 | P9 | zona `"   "` | `ZONA_INVALIDA` |
| R8-14 | P10 | zona `"C ABA"` | `ZONA_INVALIDA` |
| R8-15 | P11 | zona `None` | `CheckoutError` (nunca otra excepción) |
| R8-16 | P11 | zona `5` | `CheckoutError` (nunca otra excepción) |
| R8-17 | P17 | `calcular_envio(Decimal("100000.00"), "MARTE")` | `ZONA_INVALIDA` (la zona se valida aunque el envío fuera gratis) |

**Límite del envío gratis**

| ID | Partición | Entrada | Resultado esperado |
|---|---|---|---|
| R8-18 | P12 (justo debajo del límite) | `calcular_envio(Decimal("59999.99"), "CABA")` | `Decimal("2500.00")` |
| R8-19 | P13 (límite) | `calcular_envio(Decimal("60000.00"), "CABA")` | `Decimal("0.00")` |
| R8-20 | P14 (justo arriba del límite) | `calcular_envio(Decimal("60000.01"), "CABA")` | `Decimal("0.00")` |
| R8-21 | P12 en `GBA` | `calcular_envio(Decimal("59999.99"), "GBA")` | `Decimal("4000.00")` |
| R8-22 | P13 en `GBA` | `calcular_envio(Decimal("60000.00"), "GBA")` | `Decimal("0.00")` |
| R8-23 | P12 en `INTERIOR` | `calcular_envio(Decimal("59999.99"), "INTERIOR")` | `Decimal("6500.00")` |
| R8-24 | P13 en `INTERIOR` | `calcular_envio(Decimal("60000.00"), "INTERIOR")` | `Decimal("0.00")` |
| R8-25 | P16 | `calcular_envio(Decimal("100.00"), "RETIRO")` | `Decimal("0.00")` |

**Con `calcular_total` (precios reales, descuentos y orden de validación)**

| ID | Partición | Entrada | Resultado esperado |
|---|---|---|---|
| R8-26 | P12 con precios reales (límite) | `calcular_total([(remera, M, 1), (campera, M, 1)], "CABA", None, VIGENTE)` | subtotal `59999.49`, descuento `0.00`, envío `2500.00`, total `62499.49` |
| R8-27 | P14 | `calcular_total([(buzo, M, 2), (remera, M, 1)], "CABA", None, VIGENTE)` | subtotal `61999.30`, descuento `0.00`, envío `0.00`, total `61999.30` |
| R8-28 | P15 | `calcular_total([(buzo, M, 2), (remera, M, 1)], "CABA", "EGRESADOS2026", VIGENTE)` | subtotal `61999.30`, descuento `9299.90`, envío `2500.00`, total `55199.40` (con descuento queda en $ 52.699,40) |
| R8-29 | P14 con descuento | `calcular_total([(buzo, M, 5)], "GBA", None, VIGENTE)` | subtotal `124999.50`, descuento `12499.95`, envío `0.00`, total `112499.55` |
| R8-30 | P12 con descuento | `calcular_total([(remera, M, 5)], "CABA", None, VIGENTE)` | subtotal `59997.50`, descuento `5999.75`, envío `2500.00`, total `56497.75` |
| R8-31 | P3 en el total | `calcular_total([(buzo, M, 1)], "interior", None, VIGENTE)` | subtotal `24999.90`, descuento `0.00`, envío `6500.00`, total `31499.90` |
| R8-32 | P4 en el total | `calcular_total([(buzo, M, 1)], "RETIRO", None, VIGENTE)` | subtotal `24999.90`, descuento `0.00`, envío `0.00`, total `24999.90` |
| R8-33 | P7 en el total | `calcular_total([(buzo, M, 1)], "MARTE", None, VIGENTE)` | `ZONA_INVALIDA` |
| R8-34 | P17 en el total | `calcular_total([(buzo, M, 5)], "MARTE", None, VIGENTE)` | `ZONA_INVALIDA` (aunque el envío sería gratis) |
| R8-35 | Orden de validación (sección 3) | `calcular_total([(buzo, M, 1)], "MARTE", "NOEXISTE", VIGENTE)` | `CUPON_INVALIDO` (la zona se informa en último lugar) |
| R8-36 | Orden de validación (sección 3) | `calcular_total([], "MARTE", None, VIGENTE)` | `CARRITO_VACIO` |

### Decisiones de interpretación

- **"Subtotal ya con el descuento aplicado":** el envío gratis se decide con
  `subtotal - descuento`, donde el descuento es el que corresponda (cantidad o cupón). El
  caso R8-28 lo muestra: el subtotal sin descuento es $ 61.999,30, que superaría el límite,
  pero con el cupón queda en $ 52.699,40, así que se paga el envío. Si el código decidiera
  con el subtotal sin descuento, daría envío gratis.
- **El límite es inclusive:** "de $ 60.000 o más" incluye los $ 60.000,00 exactos (R8-19,
  R8-22 y R8-24).
- **Casos de límite exacto:** con los precios del catálogo ninguna compra termina justo en
  $ 60.000,00 (la más cercana es la de R8-26, a 51 centavos). Por eso el límite exacto se
  prueba llamando directo a `calcular_envio`, cuyo contrato recibe el subtotal con descuento
  como parámetro.
- **`RETIRO` y envío gratis dan el mismo resultado** ($ 0). Se prueba cada uno aparte
  (R8-04 y R8-25 para `RETIRO`, R8-19 a R8-24 para gratis) para que un error en uno no
  quede tapado por el otro.
- **R8-17 y R8-34:** la especificación dice que una zona que no existe da
  `ZONA_INVALIDA`, sin excepciones. Un envío gratis no la convierte en válida.
- **R8-15 y R8-16:** como en las reglas anteriores, ante un dato que no es texto la sección 1
  exige `CheckoutError`. En los tests unitarios se comprueba solo el tipo de excepción.
- **R8-36:** el orden de validación de la sección 3 pone el carrito vacío antes que la zona.
  El orden completo (ítems, cupón, zona) se cubre en R4, R6 y acá.


---

## R9 — Total

**Regla:** `total = subtotal − descuento + envío`. `calcular_total` devuelve un diccionario
con las claves `subtotal`, `descuento`, `envio` y `total`.

### Particiones

| ID | Partición | Tipo |
|---|---|---|
| P1 | Sin descuento y con envío pago (ejemplo de la sección 5) | Válida |
| P2 | Con descuento (cupón) y con envío pago | Válida |
| P3 | Sin descuento y sin envío (`RETIRO` o envío gratis) | Válida |
| P4 | Con descuento y sin envío (envío gratis) | Válida |
| P5 | Carrito con varios productos y talles distintos | Válida |
| P6 | Estructura del resultado | Estructura |
| P7 | Coherencia entre `calcular_total` y las otras funciones | Consistencia |

### Valores límite

No hay rangos numéricos propios. El límite relevante es la combinación de los dos sumandos:
descuento 0 o mayor que 0, y envío 0 o mayor que 0 (las cuatro combinaciones P1 a P4).

### Casos

`VIGENTE` es el 01/10/2026.

| ID | Partición | Entrada | Resultado esperado |
|---|---|---|---|
| R9-01 | P1 (ejemplo de la especificación) | `calcular_total([(buzo, M, 2)], "CABA", None, VIGENTE)` | subtotal `49999.80`, descuento `0.00`, envío `2500.00`, total `52499.80` |
| R9-02 | P2 (ejemplo de la especificación) | `calcular_total([(remera, M, 1)], "CABA", "EGRESADOS2026", date(2026, 11, 30))` | subtotal `11999.50`, descuento `1799.93`, envío `2500.00`, total `12699.57` |
| R9-03 | P2 con cupón fijo | `calcular_total([(buzo, M, 1)], "CABA", "BIENVENIDA", VIGENTE)` | subtotal `24999.90`, descuento `3000.00`, envío `2500.00`, total `24499.90` |
| R9-04 | P3 con `RETIRO` | `calcular_total([(remera, M, 1)], "RETIRO", None, VIGENTE)` | subtotal `11999.50`, descuento `0.00`, envío `0.00`, total `11999.50` |
| R9-05 | P3 con envío gratis | `calcular_total([(buzo, M, 3)], "CABA", None, VIGENTE)` | subtotal `74999.70`, descuento `0.00`, envío `0.00`, total `74999.70` |
| R9-06 | P4 | `calcular_total([(buzo, M, 5)], "GBA", None, VIGENTE)` | subtotal `124999.50`, descuento `12499.95`, envío `0.00`, total `112499.55` |
| R9-07 | P5 (5 prendas en 3 ítems) | `calcular_total([(buzo, M, 2), (remera, S, 2), (campera, XL, 1)], "INTERIOR", None, VIGENTE)` | subtotal `121998.79`, descuento `12199.88`, envío `0.00`, total `109798.91` |
| R9-08 | P5 (un ítem de cada producto) | `calcular_total([(buzo, M, 1), (remera, M, 1), (campera, M, 1)], "INTERIOR", None, VIGENTE)` | subtotal `84999.39`, descuento `0.00`, envío `0.00`, total `84999.39` |
| R9-09 | P6 | cualquier llamada válida a `calcular_total` | el resultado tiene exactamente las claves `subtotal`, `descuento`, `envio` y `total` |
| R9-10 | P7 | los escenarios de R9-01 a R9-08 | `subtotal == calcular_subtotal(carrito)`, `descuento == calcular_descuento(subtotal, prendas, cupon, fecha)` y `envio == calcular_envio(subtotal - descuento, zona)` |
| R9-11 | P7 (identidad) | los escenarios de R9-01 a R9-08 | `total == subtotal - descuento + envio`, comparado como `Decimal`, sin diferencia de centavos |
| R9-12 | P7 (invariantes) | los escenarios de R9-01 a R9-08 | `0 <= descuento <= subtotal` y `total >= envio` |
| R9-13 | P7 (sin estado oculto) | la misma llamada hecha dos veces seguidas con el mismo carrito | los dos resultados son iguales |

### Decisiones de interpretación

- **R9-10:** la especificación define el total como la composición de las otras reglas (R5 a
  R8). Comprobar que cada campo coincide con la función correspondiente detecta un
  `calcular_total` que calcule por su cuenta algo distinto.
- **R9-13:** si una función modificara el carrito que recibe (R4), la segunda llamada daría
  otro resultado.
- **Los valores de R9-07 y R9-08** salen de los precios del catálogo y de R5 y R8. Se
  repiten en R5, R7 y R8 con otros carritos, así que cualquier discrepancia aparecería en
  varios lugares.

---

## R10 — Persistencia (`pedidos.py`)

**Reglas:**

- `guardar_pedido` calcula los importes con `calcular_total`. Si eso lanza `CheckoutError`,
  el error se propaga y **no queda nada guardado**: ni el pedido ni sus ítems.
- Cuando `guardar_pedido` termina, el pedido es **definitivo**: cualquier otra conexión a la
  misma base lo ve completo, con todos sus ítems.
- Los montos que devuelve `obtener_pedido` son **idénticos** a los que calculó `checkout`:
  `Decimal`, mismo valor, sin ninguna pérdida.
- `precio_unitario` es el precio del catálogo, nunca uno enviado por el cliente.
- Los datos se guardan normalizados: el email en minúscula y sin espacios alrededor; zona,
  talle y cupón en mayúscula y sin espacios alrededor. Un cupón vacío se guarda como `None`.
- `obtener_pedido` de un id que no existe devuelve `None`.
- `pedidos_de` no distingue mayúsculas ni espacios en el email y devuelve los pedidos del
  más reciente al más antiguo. El email es un dato que escribe el usuario: ningún valor puede
  alterar la consulta a la base.

### Convenciones de esta sección

- `guardar(email, carrito, zona, cupon, fecha)` es `pedidos.guardar_pedido(con, ...)`.
- `OTRA` es una segunda conexión abierta a la misma base (archivo en disco, no `:memory:`).
- `contar(tabla)` es la cantidad de filas de `pedidos` o `items` vista desde `OTRA`.
- Cada test usa una base nueva y vacía. `EMAIL` es `"ana@mail.com"` y `VIGENTE` es el 01/10/2026.

### Particiones

| ID | Partición | Tipo |
|---|---|---|
| P1 | `guardar_pedido` falla con un `CheckoutError` (uno por cada código) | Error, sin datos guardados |
| P2 | Falla en el segundo ítem de un carrito de varios | Error, sin ítems parciales |
| P3 | Falla un pedido cuando ya hay otro guardado | El anterior queda intacto |
| P4 | `guardar_pedido` terminó bien y otra conexión consulta | Definitivo y completo |
| P5 | Montos con centavos (subtotal, descuento, envío, total) | Exactitud `Decimal` |
| P6 | `precio_unitario` con un precio propio en el ítem | Catálogo, no cliente |
| P7 | Email con mayúsculas y espacios | Normalizado |
| P8 | Zona con minúsculas y espacios | Normalizada |
| P9 | Talle con minúsculas y espacios | Normalizado |
| P10 | Cupón con minúsculas y espacios | Normalizado |
| P11 | Cupón `None`, `""` o solo espacios | Se guarda `None` |
| P12 | `obtener_pedido` con id que existe | Pedido completo |
| P13 | `obtener_pedido` con id que no existe (`999`, `0`, `-1`, el siguiente al último) | `None` |
| P14 | `pedidos_de` con email en otra capitalización o con espacios | Encuentra los pedidos |
| P15 | `pedidos_de` con varios pedidos del mismo email | Del más reciente al más antiguo |
| P16 | `pedidos_de` con pedidos de otros emails en la base | Solo los del email pedido |
| P17 | `pedidos_de` con un email sin pedidos | Lista vacía |
| P18 | `pedidos_de` con un email que contiene SQL (`"' OR '1'='1"`) | Lista vacía, sin alterar la consulta |
| P19 | `pedidos_de` con un email válido que contiene un apóstrofe | Encuentra sus pedidos |
| P20 | Pedido con varios ítems | Todos los ítems, en orden |
| P21 | Ítem con claves extra (`"color"`) | Se ignoran |
| P22 | Carrito recibido por `guardar_pedido` | No se modifica |

### Valores límite

| Límite | Valores a probar | Resultado |
|---|---|---|
| Ids de `obtener_pedido` | último id existente / último + 1 / `0` / `-1` | pedido / `None` / `None` / `None` |
| Cantidad de pedidos guardados tras un error | 0 antes y 0 después / 1 antes y 1 después | no se agrega ninguno |
| Cantidad de ítems guardados tras un error en el segundo ítem | 0 | el primer ítem tampoco queda |

### Casos

**Un error no deja nada guardado (P1, P2, P3)**

| ID | Entrada | Resultado esperado |
|---|---|---|
| R10-01 | `guardar(EMAIL, [(zapatillas, M, 1)], "CABA", None, VIGENTE)` | `CheckoutError` con `code="PRODUCTO_INEXISTENTE"`; `contar("pedidos") == 0` y `contar("items") == 0` |
| R10-02 | `guardar(EMAIL, [(buzo, XXXL, 1)], "CABA", None, VIGENTE)` | `TALLE_INVALIDO`; 0 pedidos y 0 ítems |
| R10-03 | `guardar(EMAIL, [(buzo, M, 0)], "CABA", None, VIGENTE)` | `CANTIDAD_INVALIDA`; 0 pedidos y 0 ítems |
| R10-04 | `guardar(EMAIL, [], "CABA", None, VIGENTE)` | `CARRITO_VACIO`; 0 pedidos y 0 ítems |
| R10-05 | `guardar(EMAIL, [(buzo, M, 1)], "CABA", "NOEXISTE", VIGENTE)` | `CUPON_INVALIDO`; 0 pedidos y 0 ítems |
| R10-06 | `guardar(EMAIL, [(buzo, M, 1)], "CABA", "EGRESADOS2026", date(2026, 12, 1))` | `CUPON_VENCIDO`; 0 pedidos y 0 ítems |
| R10-07 | `guardar(EMAIL, [(remera, M, 1)], "CABA", "BIENVENIDA", VIGENTE)` | `CUPON_MINIMO_NO_ALCANZADO`; 0 pedidos y 0 ítems |
| R10-08 | `guardar(EMAIL, [(buzo, M, 1)], "MARTE", None, VIGENTE)` | `ZONA_INVALIDA`; 0 pedidos y 0 ítems |
| R10-09 | `guardar(EMAIL, [(buzo, M, 1), (zapatillas, M, 1)], "CABA", None, VIGENTE)` | `PRODUCTO_INEXISTENTE`; 0 pedidos y 0 ítems (el primer ítem no queda guardado) |
| R10-10 | primero un `guardar` válido de 1 ítem, después uno inválido (`ZONA_INVALIDA`) | el segundo lanza el error; `contar("pedidos") == 1` y `contar("items") == 1`; el primer pedido sigue intacto |

**El pedido es definitivo (P4)**

| ID | Entrada | Resultado esperado |
|---|---|---|
| R10-11 | `guardar(EMAIL, [(buzo, M, 2), (remera, S, 1)], "CABA", None, VIGENTE)`, sin cerrar ni hacer commit adicional en `con`; después `obtener_pedido(OTRA, id)` | `OTRA` ve el pedido completo, con sus 2 ítems |
| R10-12 | el mismo escenario | `contar("pedidos") == 1` y `contar("items") == 2` |

**Montos exactos (P5)**

| ID | Entrada | Resultado esperado |
|---|---|---|
| R10-13 | `guardar(EMAIL, [(remera, M, 1)], "CABA", "EGRESADOS2026", date(2026, 11, 30))`, después `obtener_pedido` | `subtotal == Decimal("11999.50")`, `descuento == Decimal("1799.93")`, `envio == Decimal("2500.00")`, `total == Decimal("12699.57")`, los cuatro de tipo `Decimal` |
| R10-14 | `guardar(EMAIL, [(buzo, M, 7)], "CABA", None, VIGENTE)` | `subtotal == Decimal("174999.30")`, `descuento == Decimal("17499.93")`, `envio == Decimal("0.00")`, `total == Decimal("157499.37")` |
| R10-15 | cualquiera de los pedidos anteriores | los cuatro montos de `obtener_pedido` son iguales, como `Decimal`, a los de `calcular_total` con los mismos datos |
| R10-16 | un pedido con `buzo`, uno con `remera` y uno con `campera` | `precio_unitario == Decimal("24999.90")`, `Decimal("11999.50")` y `Decimal("47999.99")`, de tipo `Decimal` |

**Precio del catálogo (P6)**

| ID | Entrada | Resultado esperado |
|---|---|---|
| R10-17 | `guardar(EMAIL, [{"producto": "buzo", "talle": "M", "cantidad": 1, "precio": 1}], "CABA", None, VIGENTE)` | `precio_unitario == Decimal("24999.90")` y `subtotal == Decimal("24999.90")` |
| R10-18 | el mismo ítem con `"precio": 0` y con `"precio": -500` | `precio_unitario == Decimal("24999.90")` en ambos |

**Normalización (P7 a P11)**

| ID | Entrada | Resultado esperado |
|---|---|---|
| R10-19 | email `" Ana@Mail.COM "` | `obtener_pedido(...)["email"] == "ana@mail.com"` |
| R10-20 | zona `" caba "` | `["zona"] == "CABA"` |
| R10-21 | talle `" m "` | `["items"][0]["talle"] == "M"` |
| R10-22 | talle `"xl"` | `["items"][0]["talle"] == "XL"` |
| R10-23 | cupón `" egresados2026 "` con fecha `VIGENTE` | `["cupon"] == "EGRESADOS2026"` |
| R10-24 | cupón `""` | `["cupon"] is None` |
| R10-25 | cupón `"   "` | `["cupon"] is None` |
| R10-26 | cupón `None` | `["cupon"] is None` |

**Consultas por id (P12, P13)**

| ID | Entrada | Resultado esperado |
|---|---|---|
| R10-27 | `obtener_pedido(con, id)` con el id devuelto por `guardar` | el pedido, con `["id"] == id` |
| R10-28 | `obtener_pedido(con, 999)` en una base con un pedido | `None` |
| R10-29 | `obtener_pedido(con, 0)` | `None` |
| R10-30 | `obtener_pedido(con, -1)` | `None` |
| R10-31 | `obtener_pedido(con, id_del_último + 1)` | `None` |

**`pedidos_de` (P14 a P19)**

| ID | Entrada | Resultado esperado |
|---|---|---|
| R10-32 | pedido guardado con `"ana@mail.com"`, consulta `pedidos_de(con, "  ANA@mail.com ")` | lista con ese pedido |
| R10-33 | pedido guardado con `" Ana@MAIL.com"`, consulta `pedidos_de(con, "ana@mail.com")` | lista con ese pedido |
| R10-34 | tres pedidos de `EMAIL` guardados en orden (ids `a`, `b`, `c`) | `pedidos_de(con, EMAIL)` devuelve los ids en el orden `c`, `b`, `a` |
| R10-35 | un pedido de `ana@mail.com` y otro de `bruno@mail.com` | `pedidos_de(con, "ana@mail.com")` devuelve solo el de Ana |
| R10-36 | email sin pedidos | `[]` |
| R10-37 | cada elemento devuelto por `pedidos_de` | es igual al que devuelve `obtener_pedido` para ese id (formato completo, con ítems) |
| R10-38 | pedidos de Ana en la base, consulta `pedidos_de(con, "' OR '1'='1")` | `[]` |
| R10-39 | pedidos de Ana en la base, consulta `pedidos_de(con, "x' OR 1=1 --")` | `[]` |
| R10-40 | pedido guardado con `"o'brien@mail.com"`, consulta `pedidos_de(con, "o'brien@mail.com")` | lista con ese pedido, sin excepción |
| R10-41 | pedidos en la base, consulta `pedidos_de(con, "'; DROP TABLE pedidos; --")` | `[]`, sin excepción; `contar("pedidos")` sigue igual que antes |

**Formato, ítems y carrito (P20 a P22)**

| ID | Entrada | Resultado esperado |
|---|---|---|
| R10-42 | el pedido de R10-13 | el diccionario tiene exactamente las claves `id`, `email`, `zona`, `cupon`, `subtotal`, `descuento`, `envio`, `total` e `items`; cada ítem tiene exactamente `producto`, `talle`, `cantidad` y `precio_unitario` |
| R10-43 | `guardar_pedido` devuelve un valor | es un `int` y coincide con el `id` del pedido |
| R10-44 | `guardar(EMAIL, [(buzo, M, 2), (remera, S, 1)], "CABA", None, VIGENTE)` | `items` tiene 2 elementos, en ese orden: `buzo/M/2/24999.90` y `remera/S/1/11999.50` |
| R10-45 | dos pedidos distintos guardados uno tras otro | ids distintos, el segundo mayor; cada `obtener_pedido` devuelve sus propios datos |
| R10-46 | ítem `{"producto": "remera", "talle": "M", "cantidad": 1, "color": "rojo"}` | se guarda sin errores; el ítem devuelto tiene solo las cuatro claves del formato |
| R10-47 | carrito `[{"producto": "buzo", "talle": " m ", "cantidad": 1, "precio": 1}]` | después de `guardar`, el carrito es igual a una copia hecha antes |
| R10-48 | carrito inválido (`TALLE_INVALIDO`) | después de que `guardar` lanza el error, el carrito es igual a una copia hecha antes |

### Decisiones de interpretación

- **"Nada guardado":** se verifica con una conexión distinta (`OTRA`), no con la misma. Una
  conexión puede ver sus propios cambios sin confirmar, y eso escondería el problema.
- **R10-09 y R10-10:** son los casos más importantes de "no queda nada". Un error en un
  ítem posterior no debe dejar el pedido ni los ítems anteriores, y un error nuevo no debe
  tocar lo que ya estaba guardado.
- **R10-11:** "definitivo" quiere decir que otra conexión lo ve sin que nadie más haga
  `commit`. No se cierra `con` antes de consultar.
- **Montos exactos:** los valores de R10-13 y R10-14 tienen centavos que no se representan
  exactos en binario. Comparar con `Decimal("...")` (y no con `float`) detecta cualquier
  pérdida.
- **R10-24 a R10-26:** el cupón vacío se guarda como `None`, no como texto vacío.
- **R10-38 a R10-41:** el email lo escribe el usuario. La especificación dice que ningún valor
  puede alterar la consulta, así que todos los valores de esta tabla deben tratarse como un
  email más, sin error y sin resultados ajenos. R10-40 comprueba además que un email
  legítimo con apóstrofe siga funcionando.
- **R10-47 y R10-48:** R4 dice que "ninguna función modifica el carrito que recibe". Se toma
  `guardar_pedido` como una función más, ya que el frontend reutiliza el objeto.
- **Fecha omitida en `guardar_pedido`:** `fecha=None` significa el día de la llamada. Igual
  que en R6, depende del reloj, así que no hay un caso que dependa del día real.
- **No se prueba el orden por antigüedad con fechas:** el pedido más reciente es el que se
  guardó último. Las fechas no forman parte de lo que guarda la especificación.

---

## R11 — Endpoints HTTP (`api.py`)

**Reglas:**

- `POST /api/v1/pedidos` crea un pedido. Cuerpo JSON con `email`, `zona`, `carrito` y,
  opcionales, `cupon` y `fecha` (texto `AAAA-MM-DD`). Respuesta `201` con `id`, `subtotal`,
  `descuento`, `envio` y `total`.
- `GET /api/v1/pedidos/{id}` devuelve el pedido completo, con el formato de la sección 6.
- **Los montos viajan siempre como texto** (`"1799.93"`), nunca como número JSON.
- Todos los errores tienen el formato `{"error": {"code": "...", "message": "..."}}`.

| Situación | Status | `code` |
|---|:---:|---|
| Cualquier `CheckoutError` | 422 | el `code` del `CheckoutError` |
| El cuerpo no es JSON válido | 400 | `JSON_INVALIDO` |
| Falta email, zona o carrito, o tienen otro tipo | 400 | `DATOS_INCOMPLETOS` |
| La fecha no tiene formato `AAAA-MM-DD` | 400 | `FECHA_INVALIDA` |
| El pedido no existe | 404 | `PEDIDO_INEXISTENTE` |
| La ruta no existe | 404 | `RUTA_INEXISTENTE` |

**Un error nunca puede devolver 500.**

### Convenciones de esta sección

- Cada test levanta su propio servidor, con una base nueva, y manda requests HTTP reales.
- `POST(cuerpo)` es `POST /api/v1/pedidos` con ese cuerpo; `GET(ruta)` es un GET a esa ruta.
- La compra base es `{"email": "ana@mail.com", "zona": "CABA", "carrito": [buzo, M, 1]}`.
  Cada caso indica solo lo que cambia.
- Una **respuesta de error correcta** cumple tres cosas: el status de la tabla, el cuerpo
  con exactamente la clave `error` que contiene `code` y `message`, y `message` es un texto
  no vacío.

### Particiones

| ID | Partición | Tipo |
|---|---|---|
| P1 | `POST` con compra válida, con cupón y fecha | `201` |
| P2 | `POST` con compra válida, sin cupón ni fecha | `201` |
| P3 | `GET` de un pedido que existe | `200` |
| P4 | Montos como texto, no como número | Formato |
| P5 | `POST` con un error de negocio (uno por cada uno de los 8 códigos) | `422` |
| P6 | Cuerpo que no es JSON (texto, vacío, bytes inválidos) | `400 JSON_INVALIDO` |
| P7 | Falta `email`, `zona` o `carrito` | `400 DATOS_INCOMPLETOS` |
| P8 | `email`, `zona` o `carrito` con otro tipo | `400 DATOS_INCOMPLETOS` |
| P9 | JSON válido que no es un objeto (`[]`, `5`, `null`) | `400 DATOS_INCOMPLETOS` |
| P10 | `carrito` vacío (`[]`) | `422 CARRITO_VACIO`, no es un error de datos |
| P11 | Fecha con formato incorrecto | `400 FECHA_INVALIDA` |
| P12 | Fecha válida, incluida la última del cupón | `201` |
| P13 | `GET` de un id que no existe | `404 PEDIDO_INEXISTENTE` |
| P14 | Ruta que no existe (con `GET` y con `POST`) | `404 RUTA_INEXISTENTE` |
| P15 | Un error no deja un pedido guardado | Sin datos |
| P16 | Ítems mal formados o con valores de otro tipo | Error, nunca `500` |
| P17 | Datos normalizados al consultar | Consistencia |

### Valores límite

| Límite | Valores a probar | Resultado |
|---|---|---|
| Fecha del cupón | `"2026-11-30"` / `"2026-12-01"` | `201` / `422 CUPON_VENCIDO` |
| Fecha del calendario | `"2026-02-28"` / `"2026-02-29"` | `201` / `400 FECHA_INVALIDA` (2026 no es bisiesto) |
| Mes y día fuera de rango | `"2026-12-31"` / `"2026-13-01"` | `201` / `400 FECHA_INVALIDA` |
| Ítems del carrito | 0 / 1 | `422 CARRITO_VACIO` / `201` |
| Id del `GET` | un id que existe / `999` / `abc` | `200` / `404 PEDIDO_INEXISTENTE` / `404 RUTA_INEXISTENTE` |

### Casos

**`POST` exitoso (P1, P2, P4, P12)**

| ID | Partición | Entrada | Resultado esperado |
|---|---|---|---|
| R11-01 | P1 (ejemplo de la especificación) | `POST({"email": "ana@mail.com", "zona": "CABA", "carrito": [{"producto": "remera", "talle": "M", "cantidad": 1}], "cupon": "EGRESADOS2026", "fecha": "2026-11-30"})` | `201`; el cuerpo tiene exactamente `id`, `subtotal`, `descuento`, `envio` y `total`; `id` es entero; los montos son `"11999.50"`, `"1799.93"`, `"2500.00"` y `"12699.57"` |
| R11-02 | P2 | `POST` de 2 buzos M a `CABA`, sin cupón ni fecha | `201`; `"49999.80"`, `"0.00"`, `"2500.00"`, `"52499.80"` |
| R11-03 | P4 | las respuestas de R11-01 y R11-02 | `subtotal`, `descuento`, `envio` y `total` son de tipo texto (`str`), nunca número |
| R11-04 | P2 con montos exactos | `POST` de 7 buzos M a `CABA` | `201`; `"174999.30"`, `"17499.93"`, `"0.00"`, `"157499.37"` |
| R11-05 | P2 con cupón fijo | `POST` de 1 buzo M a `CABA`, cupón `"BIENVENIDA"` | `201`; `"24999.90"`, `"3000.00"`, `"2500.00"`, `"24499.90"` |
| R11-06 | P2 | dos `POST` seguidos con compras válidas | los dos devuelven `201`, con ids distintos y el segundo mayor que el primero |
| R11-07 | P12 | `POST` con `"fecha": "2026-02-28"` y sin cupón | `201` |
| R11-08 | P12 (último día de vigencia) | `POST` con cupón `"EGRESADOS2026"` y `"fecha": "2026-11-30"` | `201` (igual que R11-01) |
| R11-09 | Precio del cliente | `POST` con ítem `{"producto": "buzo", "talle": "M", "cantidad": 1, "precio": 1}` | `201`; `subtotal == "24999.90"` |

**`GET` de un pedido (P3, P4, P17)**

| ID | Partición | Entrada | Resultado esperado |
|---|---|---|---|
| R11-10 | P3 | `POST` de R11-01 y después `GET /api/v1/pedidos/{id}` con el `id` devuelto | `200` y el cuerpo es `{"id": id, "email": "ana@mail.com", "zona": "CABA", "cupon": "EGRESADOS2026", "subtotal": "11999.50", "descuento": "1799.93", "envio": "2500.00", "total": "12699.57", "items": [{"producto": "remera", "talle": "M", "cantidad": 1, "precio_unitario": "11999.50"}]}` |
| R11-11 | P4 | la respuesta de R11-10 | `subtotal`, `descuento`, `envio`, `total` y `precio_unitario` son texto; `id` y `cantidad` son números |
| R11-12 | P3 | el `POST` y el `GET` del mismo pedido | los cuatro montos del `GET` son iguales a los del `POST` |
| R11-13 | P17 | `POST` con email `" Ana@Mail.COM "`, zona `" caba "`, talle `" m "`, cupón `" egresados2026 "`; después `GET` | `email == "ana@mail.com"`, `zona == "CABA"`, `items[0].talle == "M"`, `cupon == "EGRESADOS2026"` |
| R11-14 | P17 | `POST` sin cupón y después `GET` | `"cupon": null` |
| R11-15 | Precio del cliente | `POST` con `"precio": 1` en el ítem y después `GET` | `items[0].precio_unitario == "24999.90"` |
| R11-16 | Varios ítems | `POST` con `[buzo M 2, remera S 1]` y después `GET` | `items` tiene 2 elementos, en ese orden, con los talles, cantidades y precios correctos |
| R11-17 | Pedidos independientes | dos `POST` distintos y un `GET` de cada uno | cada `GET` devuelve los datos de su propio pedido |

**Errores de negocio, `422` (P5, P10)**

Cada caso cambia solo el dato indicado de la compra base. Todos deben dar la respuesta de
error correcta con status `422`.

| ID | Cambio sobre la compra base | `code` esperado |
|---|---|---|
| R11-18 | producto `"zapatillas"` | `PRODUCTO_INEXISTENTE` |
| R11-19 | talle `"XXXL"` | `TALLE_INVALIDO` |
| R11-20 | cantidad `0` | `CANTIDAD_INVALIDA` |
| R11-21 | cantidad `11` | `CANTIDAD_INVALIDA` |
| R11-22 | `carrito: []` | `CARRITO_VACIO` |
| R11-23 | `"cupon": "NOEXISTE"` | `CUPON_INVALIDO` |
| R11-24 | `"cupon": "EGRESADOS2026"` y `"fecha": "2026-12-01"` | `CUPON_VENCIDO` |
| R11-25 | `"cupon": "BIENVENIDA"` con 1 remera | `CUPON_MINIMO_NO_ALCANZADO` |
| R11-26 | `"zona": "MARTE"` | `ZONA_INVALIDA` |
| R11-27 | cantidad `2.5` | `CANTIDAD_INVALIDA` |
| R11-28 | cantidad `true` | `CANTIDAD_INVALIDA` |
| R11-29 | talle `null` | `TALLE_INVALIDO` |
| R11-30 | producto `null` | `PRODUCTO_INEXISTENTE` |
| R11-31 | formato del error | el cuerpo de cualquier error tiene la forma exacta `{"error": {"code": ..., "message": ...}}`, sin otras claves |

**`400 JSON_INVALIDO` (P6)**

| ID | Cuerpo enviado | Resultado esperado |
|---|---|---|
| R11-32 | `{no es json` | `400`, `code="JSON_INVALIDO"` |
| R11-33 | cuerpo vacío | `400`, `JSON_INVALIDO` |
| R11-34 | bytes que no son texto UTF-8 (`\xff\xfe`) | `400`, `JSON_INVALIDO` |
| R11-35 | texto plano `hola` | `400`, `JSON_INVALIDO` |

**`400 DATOS_INCOMPLETOS` (P7, P8, P9)**

| ID | Cuerpo enviado | Resultado esperado |
|---|---|---|
| R11-36 | sin la clave `email` | `400`, `code="DATOS_INCOMPLETOS"` |
| R11-37 | sin la clave `zona` | `400`, `DATOS_INCOMPLETOS` |
| R11-38 | sin la clave `carrito` | `400`, `DATOS_INCOMPLETOS` |
| R11-39 | `"email": 123` | `400`, `DATOS_INCOMPLETOS` |
| R11-40 | `"zona": 5` | `400`, `DATOS_INCOMPLETOS` |
| R11-41 | `"carrito": "abc"` | `400`, `DATOS_INCOMPLETOS` |
| R11-42 | `"carrito": {}` | `400`, `DATOS_INCOMPLETOS` |
| R11-43 | `"email": null` | `400`, `DATOS_INCOMPLETOS` |
| R11-44 | cuerpo `[]` (JSON válido que no es un objeto) | `400`, `DATOS_INCOMPLETOS` |
| R11-45 | cuerpo `5` | `400`, `DATOS_INCOMPLETOS` |
| R11-46 | cuerpo `null` | `400`, `DATOS_INCOMPLETOS` |

**`400 FECHA_INVALIDA` (P11)**

| ID | Fecha enviada | Resultado esperado |
|---|---|---|
| R11-47 | `"30/11/2026"` | `400`, `code="FECHA_INVALIDA"` |
| R11-48 | `"2026-13-01"` (mes 13) | `400`, `FECHA_INVALIDA` |
| R11-49 | `"2026-02-30"` | `400`, `FECHA_INVALIDA` |
| R11-50 | `"2026-02-29"` (2026 no es bisiesto) | `400`, `FECHA_INVALIDA` |
| R11-51 | `"20261130"` (sin guiones) | `400`, `FECHA_INVALIDA` |
| R11-52 | `"2026-1-5"` (sin ceros) | `400`, `FECHA_INVALIDA` |
| R11-53 | `""` | `400`, `FECHA_INVALIDA` |
| R11-54 | `"hoy"` | `400`, `FECHA_INVALIDA` |

**`404` (P13, P14)**

| ID | Request | Resultado esperado |
|---|---|---|
| R11-55 | `GET /api/v1/pedidos/999` en una base vacía | `404`, `code="PEDIDO_INEXISTENTE"` |
| R11-56 | `GET /api/v1/otra` | `404`, `code="RUTA_INEXISTENTE"` |
| R11-57 | `POST /api/v1/otra` con una compra válida | `404`, `RUTA_INEXISTENTE` |
| R11-58 | `GET /api/v1/pedidos/abc` | `404`, `RUTA_INEXISTENTE` |
| R11-59 | `GET /api/v1/pedidos/1/extra` | `404`, `RUTA_INEXISTENTE` |
| R11-60 | `GET /api/v1/pedidos` (sin id) | `404`, `RUTA_INEXISTENTE` |
| R11-61 | `POST /api/v1/pedidos/1` con una compra válida | `404`, `RUTA_INEXISTENTE` |
| R11-62 | `GET /` | `404`, `RUTA_INEXISTENTE` |

**Un error no guarda nada (P15)**

| ID | Entrada | Resultado esperado |
|---|---|---|
| R11-63 | `POST` con error de negocio (`ZONA_INVALIDA`) y después `GET /api/v1/pedidos/1` | `404`, `PEDIDO_INEXISTENTE` |
| R11-64 | `POST` con `JSON_INVALIDO` y después `GET /api/v1/pedidos/1` | `404`, `PEDIDO_INEXISTENTE` |
| R11-65 | `POST` con `FECHA_INVALIDA` y después `GET /api/v1/pedidos/1` | `404`, `PEDIDO_INEXISTENTE` |
| R11-66 | `POST` con error, después `POST` válido, después `GET` del `id` devuelto | `201` y después `200` con los datos del pedido válido |

**Nunca `500` (P16)**

Estos casos no fijan el `code` (la especificación no lo define para ítems mal formados),
pero sí exigen que la respuesta sea un error correcto con status `400` o `422`, y nunca `500`.

| ID | Cambio sobre la compra base | Resultado esperado |
|---|---|---|
| R11-67 | `"carrito": [5]` | status `400` o `422`, nunca `500`; cuerpo con formato de error |
| R11-68 | `"carrito": [null]` | status `400` o `422`, nunca `500` |
| R11-69 | ítem `{"producto": "buzo"}` (faltan `talle` y `cantidad`) | status `400` o `422`, nunca `500` |
| R11-70 | ítem `{"talle": "M", "cantidad": 1}` (falta `producto`) | status `400` o `422`, nunca `500` |
| R11-71 | `"cantidad": "diez"` | `422`, `CANTIDAD_INVALIDA` |
| R11-72 | `"cupon": ""` (cupón vacío) | `201` (no es error: equivale a no usar cupón) |
| R11-73 | todos los casos de error de esta sección | ninguno devuelve status `500` |

### Decisiones de interpretación

- **Montos como texto:** `R11-03`, `R11-11` y los valores de `0.00` en las respuestas
  prueban a la vez dos cosas: que el tipo JSON sea texto y que tenga **dos decimales**
  (`"0.00"`, `"2500.00"`), como muestran los ejemplos de la especificación. El valor en sí
  se prueba como `Decimal` en R7.
- **`precio_unitario` como texto:** la sección 6 lo muestra como `Decimal` y R11 dice que los
  montos viajan siempre como texto. Se toma `precio_unitario` como un monto más.
- **R11-44 a R11-46:** un JSON válido que no es un objeto no trae email, zona ni carrito,
  así que cae en `DATOS_INCOMPLETOS`. No es `JSON_INVALIDO`, porque el texto es JSON bien
  formado.
- **R11-22 contra R11-38:** un carrito vacío (`[]`) es un dato presente y de tipo correcto, y
  es un error de negocio (`422 CARRITO_VACIO`). Un carrito ausente o de otro tipo es un error
  de datos (`400 DATOS_INCOMPLETOS`).
- **R11-51 y R11-52:** la especificación pide el formato `AAAA-MM-DD`. Un texto como
  `"20261130"` o `"2026-1-5"` se puede interpretar como fecha con algunas librerías, pero no
  tiene el formato pedido.
- **R11-58 a R11-62:** la especificación define solo `POST /api/v1/pedidos` y
  `GET /api/v1/pedidos/{id}`. Cualquier otra combinación de método y ruta es "una ruta que
  no existe". R11-58 toma `abc` como una ruta, porque un id es un número.
- **R11-63 a R11-65:** con una base nueva, el primer pedido que se guardara tendría el id 1.
  Que `GET /api/v1/pedidos/1` dé `404` indica que el error no dejó nada guardado (es el
  efecto de R10 visto desde HTTP).
- **R11-67 a R11-70:** la sección 1 pide `CheckoutError` ante cualquier dato inválido, pero
  no dice qué `code` corresponde a un ítem que no es un objeto o al que le faltan claves.
  Por eso solo se exige que no sea un `500`.
- **No se prueban (la especificación no los define):** otros métodos HTTP (`PUT`,
  `DELETE`), un `cupon` o una `fecha` de otro tipo que texto, `"cupon": null`,
  `"fecha": null`, ni la fecha omitida con un cupón con vencimiento (depende del reloj).