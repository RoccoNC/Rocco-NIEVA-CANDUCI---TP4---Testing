# HALLAZGOS.md

## Linter (ruff)
`ruff check checkout.py` detectó 5 errores de forma:
- `F401`: import json sin usar.
- `E722`: except desnudo (sin tipo).
- `B008` (x2): uso de `date.today()` en la firma de funciones.
- `E711`: comparación con `None` en lugar de `is None`.

## Fichas de Hallazgos Críticos en `checkout.py`

**1. Float en lugar de Decimal**
* **Ubicación:** `checkout.py`, todo el módulo.
* **Categoría:** numéricos.
* **Regla violada:** R7 (Todo debe ser `Decimal`).
* **Qué pasa:** Genera errores binarios en los centavos.
* **Cómo la encontré:** Lectura del código.
* **Nivel de test:** Unitario.
* **Severidad:** Alta.
* **Test que la demuestra:** `test_precios_deben_ser_decimal`

**2. Cupón Inventado DEBUG100**
* **Ubicación:** `checkout.py`, línea 23.
* **Categoría:** alucinación.
* **Regla violada:** R6 (Solo existen dos cupones).
* **Qué pasa:** Da 100% de descuento.
* **Cómo la encontré:** Lectura del código.
* **Nivel de test:** Unitario.
* **Severidad:** Alta.
* **Test que la demuestra:** `test_cupon_debug_da_error`

**3. Modificación del carrito original**
* **Ubicación:** `checkout.py`, línea 35.
* **Categoría:** estado y efectos laterales.
* **Regla violada:** R4 (Ninguna función modifica lo que recibe).
* **Qué pasa:** Transforma el talle a mayúscula en el diccionario original del cliente.
* **Cómo la encontré:** Lectura del código.
* **Nivel de test:** Unitario.
* **Severidad:** Alta.
* **Test que la demuestra:** `test_no_modifica_el_carrito_original`

**4. Validación del límite de descuento**
* **Ubicación:** `checkout.py`, línea 60.
* **Categoría:** lógica y valores límite.
* **Regla violada:** R5 (Desde 5 prendas).
* **Qué pasa:** Usa `> 5` en lugar de `>= 5`, por lo que 5 prendas no reciben descuento.
* **Cómo la encontré:** Mutación y revisión manual.
* **Nivel de test:** Unitario.
* **Severidad:** Alta.
* **Test que la demuestra:** `test_5_prendas_reciben_descuento`

**5. date.today() en el def**
* **Ubicación:** `checkout.py`, líneas 57 y 102.
* **Categoría:** tiempo y fechas.
* **Regla violada:** R6.
* **Qué pasa:** La fecha se fija al iniciar el servidor y nunca cambia, dejando pasar cupones vencidos.
* **Cómo la encontré:** Linter `ruff` (B008).
* **Nivel de test:** Unitario.
* **Severidad:** Alta.
* **Test que la demuestra:** `test_usa_fecha_actual_si_no_se_provee`

## Tabla por Severidad

| Ubicación | Regla | Categoría | Falla | Severidad |
| :--- | :--- | :--- | :--- | :--- |
| `checkout.py` (Líneas Varias) | R7 | numéricos | Uso de `float` en lugar de `Decimal` | Alta |
| `checkout.py` (Línea 23) | R6 | alucinación | Cupón ficticio `DEBUG100` | Alta |
| `checkout.py` (Línea 35) | R4 | efectos laterales | Modifica el talle del carrito original | Alta |
| `checkout.py` (Línea 60) | R5 | valores límite | Usa `> 5` en lugar de `>= 5` | Alta |
| `checkout.py` (Línea 57) | R6 | tiempo | Usa `date.today()` en la firma de función | Alta |