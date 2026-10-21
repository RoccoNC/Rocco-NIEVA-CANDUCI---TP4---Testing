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