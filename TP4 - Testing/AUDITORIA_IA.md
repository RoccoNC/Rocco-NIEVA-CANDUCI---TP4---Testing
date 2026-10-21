# AUDITORIA.md

Auditoría de la suite de la IA (`test_checkout_ia.py`) y de los tres módulos
(`checkout.py`, `pedidos.py`, `api.py`). Todo se contrastó con `ESPECIFICACION.md`.

---

## Sección 1 — Los tests de la IA

### 1.1 Clasificación de los ocho tests

| # | Test | Clasificación | Por qué |
|---|---|---|---|
| 1 | `test_subtotal` | Tautológico | El valor esperado sale de `CATALOGO` y de la misma multiplicación `float` del código, así que si el precio estuviera mal el test igual pasa. |
| 2 | `test_total_funciona` | Inútil | `assert resultado is not None` no comprueba ningún importe: un diccionario nunca es `None`. |
| 3 | `test_total_positivo` | Débil | `total > 0` lo cumple cualquier total equivocado que sea positivo. |
| 4 | `test_cupon_egresados` | Débil | Compara contra `100000 * 0.15`, que es la misma fórmula `float` del código, con un subtotal redondo que oculta el redondeo, una sola fecha y sin probar vencimiento. |
| 5 | `test_envio_caba` | Útil | Compara contra un valor de la especificación (2500) que no depende del código, aunque cubre una sola zona y no prueba el límite de $ 60.000. |
| 6 | `test_descuento_por_cantidad` | Débil | El valor esperado es correcto, pero usa 6 prendas y no 5, que es el límite donde está el error `> 5`. |
| 7 | `test_talle_valido` | Inútil | No tiene ningún `assert`: pasa mientras no explote, y solo prueba el camino feliz. |
| 8 | `test_no_explota_con_varios_productos` | Inútil | El `try/except Exception: pass` se traga cualquier error, así que el test no puede fallar nunca. |

Resumen: 1 útil, 3 débiles, 1 tautológico y 3 inútiles. Ninguno prueba un `CheckoutError`.

### 1.2 Puntaje de mutación

Comando:

```bash
python mutar.py --tests test_checkout_ia.py
```

Resultado (Python 3.12.3):

```
Mutantes generados : 29
Muertos            : 17
Sobrevivientes     : 12
Puntaje de mutación: 58.6%
```

Mutantes que sobrevivieron (el cambio no hizo fallar ningún test):

| Línea | Cambio | Código |
|---|---|---|
| 40 | `<` → `<=` | `if not (1 <= item["cantidad"] < 10):` |
| 40 | `10` → `11` | `if not (1 <= item["cantidad"] < 10):` |
| 60 | `>` → `>=` | `if cantidad_prendas > 5:` |
| 72 | `<` → `<=` | `if not fecha < datos["vence"]:` |
| 76 | `==` → `!=` | `elif datos["tipo"] == "fijo":` |
| 77 | `<` → `<=` | `if subtotal < datos["minimo"]:` |
| 82 | `+` → `-` | `descuento += datos["valor"]` |
| 96 | `>=` → `>` | `if subtotal >= 60000:` |
| 96 | `60000` → `60001` | `if subtotal >= 60000:` |
| 107 | `+` → `-` | `prendas = prendas + item["cantidad"]` |
| 111 | `+` → `-` | `total = subtotal - descuento + envio` |
| 111 | `-` → `+` | `total = subtotal - descuento + envio` |

### 1.3 Por qué una suite con casi 80% de cobertura no detecta ninguna falla

La cobertura mide qué líneas **se ejecutaron**, no si algún test **verificó** el resultado de
esas líneas. Los datos de este TP:

```bash
pytest test_checkout_ia.py --cov=checkout --cov-branch --cov-report=term-missing
```

```
checkout.py      62     14     26      6    73%   7-9, 38, 41, 50-51, 67, 73, 76-82, 91
```

Sin contar ramas, la cobertura de líneas es del 77% (14 de 62 líneas sin ejecutar). Las
causas de que ese 77% no detecte nada son estas:

1. **Los asserts no comprueban el valor.** `test_total_funciona` (`is not None`) y
   `test_total_positivo` (`> 0`) recorren todo `calcular_total`, incluida la línea 111
   (`total = subtotal - descuento + envio`), pero aceptan cualquier total positivo. Por eso
   los mutantes `+` → `-` y `-` → `+` de esa línea sobreviven.
2. **Hay tests que no pueden fallar.** `test_talle_valido` no tiene `assert` y
   `test_no_explota_con_varios_productos` captura todas las excepciones. Ejecutan las líneas
   (suman cobertura) y no verifican nada.
3. **El valor esperado sale del propio código.** `test_subtotal` usa `CATALOGO` y
   `test_cupon_egresados` usa `0.15` en `float`. Si el código tuviera un precio o un
   porcentaje equivocado, el test lo repetiría.
4. **Las entradas están lejos de los límites.** Se usa 6 prendas (el límite es 5), una
   cantidad de 1 y 2 (el límite superior es 10), un subtotal de $ 100.000 y un envío de
   $ 10.000 (el límite es $ 60.000), y una fecha del 01/10/2026 (el límite es el 30/11).
   Por eso `>` contra `>=`, `<` contra `<=` y `60000` contra `60001` sobreviven.
5. **No hay ningún test de error.** Ninguno espera un `CheckoutError`, así que las
   validaciones (líneas 38, 41, 67, 73, 91) casi no se ejecutan y, cuando se ejecutan, nadie
   mira el resultado.
6. **Se prueban las funciones sueltas y casi nunca juntas.** Las fallas que están en la
   combinación (acumular cupón y descuento por cantidad, o calcular el envío con el subtotal
   sin descuento) quedan afuera.

Con 29 mutantes, la suite mata 17 (58,6%). Los 12 que sobreviven coinciden con los
límites, el cálculo del total y el cupón fijo, que son justo las zonas con fallas.

---

## Sección 2 — Hallazgos

### 2.1 `ruff check checkout.py`

```bash
ruff check checkout.py
```

```
F401 `json` imported but unused           checkout.py:1:8
E722 Do not use bare `except`             checkout.py:50:9
B008 Do not perform function call `date.today` in argument defaults   checkout.py:57:70
E711 Comparison to `None` should be `cond is not None`                checkout.py:63:17
B008 Do not perform function call `date.today` in argument defaults   checkout.py:102:53
Found 5 errors.
```

Cada aviso de `ruff` está asociado a un hallazgo de las tablas de abajo: F401 es C-01, E722
es C-05, los dos B008 son C-13 y E711 es C-18.

### 2.2 Criterio de severidad

- **Alta:** pierde dinero o datos, deja una puerta abierta, o devuelve un error `500` o un
  resultado equivocado en el flujo principal de compra.
- **Media:** rechaza o acepta mal un dato en un caso concreto, sin pérdida de dinero ni de
  datos.
- **Baja:** limpieza de código o un caso que difícilmente ocurre.

La columna "Cómo la encontré" indica el caso de `CASOS.md` que la muestra al ejecutarlo
contra el código, o `ruff`, o lectura del código.

### 2.3 Hallazgos de `checkout.py`

| ID | Línea | Falla | Categoría | Regla | Cómo la encontré | Sev. |
|---|---|---|---|---|---|---|
| C-01 | 1 | `import json` sin usar. | code smell | — | `ruff` F401 | Baja |
| C-02 | 13-15, 21-22, 26-31, 45, 54, 61, 74, 84, 97, 111-117 | Todo el módulo usa `float` o `int` en lugar de `Decimal`: los precios, porcentajes, envíos y los cuatro valores que devuelve `calcular_total`. Por ejemplo, 7 buzos dan `174999.3` como `float`. | numéricos | R7 | Casos R7-01 y R7-08; los tipos devueltos son `float` e `int` | Alta |
| C-03 | 23 | Cupón `DEBUG100`, inventado: da 100% de descuento hasta el año 2099. Con 6 o más prendas se acumula con el 10% y supera el subtotal. | alucinación | R6 | Caso R6-22 (debería dar `CUPON_INVALIDO` y da 100% de descuento) | Alta |
| C-04 | 34-41 | `validar_item` no valida el producto, así que un producto fuera del catálogo no lanza `PRODUCTO_INEXISTENTE`. | lógica y límites | R1 y sección 3 | Caso R1-06 | Alta |
| C-05 | 48-51 | `except:` vacío con `continue`: si el producto no está en el catálogo, se omite del subtotal en silencio (`calcular_subtotal([zapatillas])` da `0`). | manejo de errores | R1 | `ruff` E722 y caso R1-06 con `calcular_subtotal` | Alta |
| C-06 | 49 | `item.get("precio", ...)` toma el precio que manda el cliente: un ítem con `"precio": 1` da subtotal `1`. | seguridad | R1 | Caso R1-12 | Alta |
| C-07 | 35 | `validar_item` escribe `item["talle"] = ...upper()`: modifica el carrito que recibe, incluso cuando después falla por otro ítem. | efectos laterales | R4 | Casos R4-08, R4-09 y R4-15 | Alta |
| C-08 | 35 | El talle se pasa a mayúscula pero no se recorta: `"  M "` da `TALLE_INVALIDO`. | strings | R2 | Caso R2-10 | Media |
| C-09 | 40 | `1 <= cantidad < 10` excluye al 10: comprar 10 prendas da `CANTIDAD_INVALIDA`. | lógica y límites | R3 | Caso R3-05 | Media |
| C-10 | 40 | La cantidad no se valida como entero: `2.5` y `True` pasan. | tipos | R3 | Casos R3-11 y R3-16 | Media |
| C-11 | 35-36, 40, 64, 88, 103-106 | Valores que no son del tipo esperado lanzan `AttributeError`, `KeyError` o `TypeError` en vez de `CheckoutError` (talle `None`, cantidad `"3"` o `None`, cupón `123`, zona `None`, carrito `None`, ítem sin `talle`). | manejo de errores | Sección 1 | Casos R2-20, R3-14, R3-15, R6-26, R8-15 y R4-07 | Media |
| C-12 | 102-103 | No hay control de carrito vacío: `calcular_total([], "CABA")` da total `2500`. | lógica y límites | R4 | Casos R4-05 y R4-06 | Media |
| C-13 | 57, 102 | `fecha=date.today()` en el valor por defecto se evalúa **una vez, al importar**. Un servidor que corre varios días sigue usando la fecha del día que arrancó, y el cupón no vence. | fechas | R6 | `ruff` B008 y caso R6-40 | Alta |
| C-14 | 72 | Con `fecha=None` (valor que usa `guardar_pedido` por defecto y que manda la API) y un cupón porcentual, `fecha < vence` lanza `TypeError`. | tipos | R6 y sección 1 | Prueba `calcular_total(..., "EGRESADOS2026", None)`; en la API, `POST` con cupón y sin fecha da `500` | Alta |
| C-15 | 72 | `not fecha < vence` rechaza el 30/11/2026, último día de vigencia (debe ser inclusive). | fechas | R6 | Caso R6-03 | Media |
| C-16 | 60 | `cantidad_prendas > 5`: con exactamente 5 prendas no hay descuento (debe ser `>= 5`). | lógica y límites | R5 | Caso R5-03 | Alta |
| C-17 | 61-82 | `descuento +=` acumula el descuento por cantidad con el cupón; la regla pide aplicar el mayor. Con 6 prendas y `EGRESADOS2026` da 25.000 en vez de 15.000. | lógica y límites | R6 | Prueba con 6 prendas y cupón. R6-27 pasa por casualidad por C-16 | Alta |
| C-18 | 63-64 | `cupon != None`: un cupón `""` o de solo espacios da `CUPON_INVALIDO` en vez de equivaler a no usar cupón. | lógica y límites | R6 | `ruff` E711 y casos R6-18 y R6-19 | Media |
| C-19 | 64 | El cupón se recorta pero no se pasa a mayúscula: `"egresados2026"` da `CUPON_INVALIDO`. | strings | R6 | Caso R6-12 | Media |
| C-20 | 84, 117 | `round()` sobre `float`: el medio centavo no sube. 15% de $ 11.999,50 da `1799.92` en vez de `1799.93`. | numéricos | R7 | Caso R7-13 | Alta |
| C-21 | 84 | Falta el tope "el descuento nunca supera el subtotal". Con los cupones reales no se alcanza, pero con `DEBUG100` sí. | lógica y límites | R6 | Lectura | Baja |
| C-22 | 93 | `ENVIOS.keys().join(', ')`: los `dict_keys` no tienen `join`. Una zona inválida lanza `AttributeError` en vez de `ZONA_INVALIDA`. | alucinación | R8 y sección 1 | Caso R8-09 | Alta |
| C-23 | 110 | `calcular_envio(subtotal, zona)` recibe el subtotal sin descuento; la regla pide el subtotal con descuento. | lógica y límites | R8 | Caso R8-28 | Alta |
| C-24 | 60, 61, 96, 105-107 | Números mágicos (`5`, `0.10`, `60000`) y un bucle manual para sumar prendas. | code smell | — | Lectura | Baja |

### 2.4 Hallazgos de `pedidos.py`

| ID | Línea | Falla | Categoría | Regla | Cómo la encontré | Sev. |
|---|---|---|---|---|---|---|
| P-01 | 12-15, 23, 55-58, 68, 88-91, 97 | Los importes se guardan como `REAL`, se convierten con `float()` y se leen con `Decimal(float)`: el valor leído arrastra el error binario (el descuento de $ 1.799,93 vuelve como `1799.9200000000000727...`). | numéricos | R10 y R7 | Caso R10-13 | Alta |
| P-02 | 39-50 | `con.commit()` en la línea 48 guarda el pedido **antes** de calcular el total. Si `calcular_total` lanza `CheckoutError`, queda un pedido con todos los importes en cero. | efectos laterales | R10 | Caso R10-01 (queda 1 pedido y 0 ítems) | Alta |
| P-03 | 52-71 | No hay `commit` después del `UPDATE` de importes ni del `INSERT` de los ítems: otra conexión ve el pedido con importes en cero y sin ítems, y al cerrar la conexión se pierden. | efectos laterales | R10 | Casos R10-11 y R10-12 | Alta |
| P-04 | 64 | `item.get("precio", ...)` guarda como `precio_unitario` el precio que manda el cliente (un buzo a $ 1). | seguridad | R10 y R1 | Caso R10-17 | Alta |
| P-05 | 107 | `pedidos_de` arma la consulta con un f-string: `' OR '1'='1` devuelve los pedidos de todos, y un email con apóstrofe (`o'brien@mail.com`) lanza `OperationalError`. | seguridad | R10 | Casos R10-38, R10-40 y R10-41 | Alta |
| P-06 | 4, 64, 109 | La lógica de precios está duplicada (se importa `CATALOGO` en vez de reutilizar `checkout`) y `pedidos_de` hace una consulta por cada pedido (N+1). | code smell | — | Lectura | Baja |

### 2.5 Hallazgos de `api.py`

| ID | Línea | Falla | Categoría | Regla | Cómo la encontré | Sev. |
|---|---|---|---|---|---|---|
| A-01 | 18 | `json.dumps(..., default=float)` envía los `Decimal` como números JSON (`24999.9`), no como texto con dos decimales. | numéricos | R11 | Casos R11-01 y R11-03 | Alta |
| A-02 | 53-54, 67-68 | Un solo `except Exception` responde `500` a todo: un `CheckoutError` no da `422`, un JSON roto no da `400`, y el cuerpo es `{"error": "texto"}` en vez de `{"error": {"code", "message"}}`. | manejo de errores | R11 | Casos R11-18 a R11-35: todos devuelven `500` | Alta |
| A-03 | 54, 68 | El `500` devuelve `str(e)`: expone mensajes internos de Python y de SQLite al cliente. | seguridad | R11 | Lectura y prueba con `GET /api/v1/pedidos/99999999999999999999` | Baja |
| A-04 | 41 | La `fecha` llega como texto y se pasa tal cual a `checkout`, que espera un `date`. Es la falla del paso de información entre `api.py` y `checkout.py`: con cupón, `POST` da `500` (`'<' not supported between 'str' and 'date'`). | tipos | R11 y R6 | Casos R11-01 y R11-08 | Alta |
| A-05 | 30-42 | No se valida nada del cuerpo: sin `email`, `zona` o `carrito`, o con otro tipo, o con un cuerpo que no es un objeto, da `500` en vez de `400 DATOS_INCOMPLETOS`. Una fecha como `"30/11/2026"` ni se mira, así que nunca hay `FECHA_INVALIDA`. | lógica y límites | R11 | Casos R11-36 a R11-46 y R11-47 a R11-54 | Alta |
| A-06 | 66 | Si el pedido no existe responde `200` con el cuerpo `null`, en vez de `404 PEDIDO_INEXISTENTE`. | lógica y límites | R11 | Caso R11-55 | Media |
| A-07 | 64 | Un id numérico muy grande hace que SQLite lance `OverflowError` y se responde `500` en vez de `404`. | manejo de errores | R11 | Prueba con `GET /api/v1/pedidos/99999999999999999999` | Baja |
| A-08 | 34-44 | La conexión se cierra solo en el camino sin error: si algo lanza una excepción, queda abierta. | efectos laterales | — | Lectura | Baja |

### 2.6 Tabla final (de la más grave a la menos grave)

| # | ID | Archivo:línea | Falla | Categoría | Regla | Sev. |
|--:|---|---|---|---|---|---|
| 1 | C-03 | `checkout.py:23` | Cupón `DEBUG100` inventado (100% de descuento) | alucinación | R6 | Alta |
| 2 | P-05 | `pedidos.py:107` | Inyección SQL en `pedidos_de` | seguridad | R10 | Alta |
| 3 | C-06 | `checkout.py:49` | Se usa el precio que manda el cliente | seguridad | R1 | Alta |
| 4 | P-04 | `pedidos.py:64` | `precio_unitario` guardado con el precio del cliente | seguridad | R10, R1 | Alta |
| 5 | P-03 | `pedidos.py:52-71` | Falta el `commit` final: importes en cero y sin ítems | efectos laterales | R10 | Alta |
| 6 | P-02 | `pedidos.py:39-50` | `commit` antes de calcular: pedido huérfano si hay error | efectos laterales | R10 | Alta |
| 7 | P-01 | `pedidos.py:12-23, 55-97` | Importes como `REAL`/`float` y lectura con `Decimal(float)` | numéricos | R10, R7 | Alta |
| 8 | A-02 | `api.py:53-54, 67-68` | Todo error responde `500` | manejo de errores | R11 | Alta |
| 9 | A-04 | `api.py:41` | La fecha llega como texto y no como `date` | tipos | R11, R6 | Alta |
| 10 | C-22 | `checkout.py:93` | `.keys().join()` no existe: zona inválida lanza `AttributeError` | alucinación | R8 | Alta |
| 11 | C-17 | `checkout.py:61-82` | Se acumulan cupón y descuento por cantidad | lógica y límites | R6 | Alta |
| 12 | C-23 | `checkout.py:110` | El envío gratis se decide con el subtotal sin descuento | lógica y límites | R8 | Alta |
| 13 | C-05 | `checkout.py:48-51` | `except:` vacío omite el producto inexistente | manejo de errores | R1 | Alta |
| 14 | C-04 | `checkout.py:34-41` | `validar_item` no valida el producto | lógica y límites | R1 | Alta |
| 15 | C-07 | `checkout.py:35` | `validar_item` modifica el carrito | efectos laterales | R4 | Alta |
| 16 | C-02 | `checkout.py` (varias) | `float` e `int` en lugar de `Decimal` | numéricos | R7 | Alta |
| 17 | C-20 | `checkout.py:84, 117` | `round()` sobre `float` no sube el medio centavo | numéricos | R7 | Alta |
| 18 | C-16 | `checkout.py:60` | `> 5` en vez de `>= 5` | lógica y límites | R5 | Alta |
| 19 | C-13 | `checkout.py:57, 102` | `date.today()` evaluado al importar | fechas | R6 | Alta |
| 20 | C-14 | `checkout.py:72` | `fecha=None` lanza `TypeError` con cupón porcentual | tipos | R6 | Alta |
| 21 | A-01 | `api.py:18` | Los montos viajan como número JSON | numéricos | R11 | Alta |
| 22 | A-05 | `api.py:30-42` | Sin `DATOS_INCOMPLETOS` ni `FECHA_INVALIDA` | lógica y límites | R11 | Alta |
| 23 | C-15 | `checkout.py:72` | El cupón vence el 30/11 en vez de el 01/12 | fechas | R6 | Media |
| 24 | C-12 | `checkout.py:102-103` | Falta `CARRITO_VACIO` | lógica y límites | R4 | Media |
| 25 | C-09 | `checkout.py:40` | La cantidad 10 se rechaza | lógica y límites | R3 | Media |
| 26 | C-08 | `checkout.py:35` | El talle no se recorta | strings | R2 | Media |
| 27 | C-18 | `checkout.py:63-64` | Cupón vacío o de espacios da `CUPON_INVALIDO` | lógica y límites | R6 | Media |
| 28 | C-19 | `checkout.py:64` | El cupón no se pasa a mayúscula | strings | R6 | Media |
| 29 | C-10 | `checkout.py:40` | La cantidad acepta `2.5` y `True` | tipos | R3 | Media |
| 30 | C-11 | `checkout.py` (varias) | Se lanzan excepciones que no son `CheckoutError` | manejo de errores | Sección 1 | Media |
| 31 | A-06 | `api.py:66` | Pedido inexistente da `200 null` | lógica y límites | R11 | Media |
| 32 | A-03 | `api.py:54, 68` | `str(e)` expone mensajes internos | seguridad | R11 | Baja |
| 33 | A-07 | `api.py:64` | Id enorme da `500` | manejo de errores | R11 | Baja |
| 34 | A-08 | `api.py:34-44` | Conexión sin cerrar si hay error | efectos laterales | — | Baja |
| 35 | C-21 | `checkout.py:84` | Falta el tope "el descuento no supera el subtotal" | lógica y límites | R6 | Baja |
| 36 | C-24 | `checkout.py:60, 61, 96, 105-107` | Números mágicos y bucle manual | code smell | — | Baja |
| 37 | C-01 | `checkout.py:1` | `import json` sin usar | code smell | — | Baja |
| 38 | P-06 | `pedidos.py:4, 64, 109` | Precios duplicados y consultas N+1 | code smell | — | Baja |

Total: 38 hallazgos (24 en `checkout.py`, 6 en `pedidos.py` y 8 en `api.py`): 22 de severidad
alta, 9 media y 7 baja.