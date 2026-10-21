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