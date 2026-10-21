## R1 — Catálogo y precios

**Regla:** Tres productos con precio fijo: `buzo` $24.999,90, `remera` $11.999,50 y `campera` $47.999,99. El nombre se escribe exactamente así, en minúscula. El precio sale siempre del catálogo y se ignora si el ítem trae uno propio.

### Particiones

| ID | Partición | Tipo |
|---|---|---|
| P1 | Producto `buzo` | Válida |
| P2 | Producto `remera` | Válida |
| P3 | Producto `campera` | Válida |
| P4 | Nombre que no está en el catálogo (`"gorra"`) | Inválida |
| P5 | Nombre correcto con mayúsculas (`"BUZO"`, `"Buzo"`) | Inválida |
| P6 | Nombre con espacios alrededor (`" buzo "`) | Inválida |
| P7 | Nombre vacío (`""`) | Inválida |
| P8 | Valor que no es texto (`None`, `123`) | Inválida |
| P9 | Ítem con precio propio | Válida (el precio se ignora) |

### Casos

| ID | Partición | Entrada | Resultado esperado | Nivel |
|---|---|---|---|---|
| R1-01 | P1 | `calcular_subtotal([{"producto": "buzo", "talle": "M", "cantidad": 1}])` | `Decimal("24999.90")` | unitario |
| R1-02 | P2 | `calcular_subtotal([{"producto": "remera", "talle": "M", "cantidad": 1}])` | `Decimal("11999.50")` | unitario |
| R1-03 | P3 | `calcular_subtotal([{"producto": "campera", "talle": "M", "cantidad": 1}])` | `Decimal("47999.99")` | unitario |
| R1-04 | P4 | `validar_item({"producto": "gorra", "talle": "M", "cantidad": 1})` | `PRODUCTO_INEXISTENTE` | unitario |
| R1-05 | P5 | `validar_item({"producto": "BUZO", "talle": "M", "cantidad": 1})` | `PRODUCTO_INEXISTENTE` | unitario |
| R1-06 | P6 | `validar_item({"producto": " buzo ", "talle": "M", "cantidad": 1})` | `PRODUCTO_INEXISTENTE` | unitario |
| R1-07 | P7 | `validar_item({"producto": "", "talle": "M", "cantidad": 1})` | `PRODUCTO_INEXISTENTE` | unitario |
| R1-08 | P8 | `validar_item({"producto": None, "talle": "M", "cantidad": 1})` | `PRODUCTO_INEXISTENTE` | unitario |
| R1-09 | P9 | `calcular_subtotal([{"producto": "buzo", "talle": "M", "cantidad": 1, "precio": 10}])` | `Decimal("24999.90")` | unitario |