# Auditoría de la IA

Auditoría de la suite de la IA (`test_checkout_ia.py`). Contrastado con `ESPECIFICACION.md`.

## 1. Clasificación de los ocho tests

1. **`test_subtotal`**
   * **Clasificación:** Tautológico
   * **Qué verifica realmente:** Ejecuta la misma multiplicación del código.
   * **Qué error dejaría pasar:** Si el precio de catálogo es incorrecto, el test usaría el mismo precio erróneo y pasaría.
   * **Cómo se arregla:** Afirmar contra el valor fijo escrito a mano: `assert subtotal == Decimal("49999.80")`.

2. **`test_total_funciona`**
   * **Clasificación:** Inútil / Débil
   * **Qué verifica realmente:** Solo que el resultado no sea `None`.
   * **Qué error dejaría pasar:** Un total mal calculado o negativo.
   * **Cómo se arregla:** Afirmar contra un diccionario exacto.

3. **`test_total_positivo`**
   * **Clasificación:** Débil
   * **Qué verifica realmente:** Solo que el total sea mayor a 0.
   * **Qué error dejaría pasar:** Cualquier total numérico incorrecto (ej. cobrar $10 en lugar de $100.000).
   * **Cómo se arregla:** Afirmar contra el total exacto.

4. **`test_cupon_egresados`**
   * **Clasificación:** Tautológico
   * **Qué verifica realmente:** Multiplica por `0.15` igual que el código.
   * **Qué error dejaría pasar:** Errores de redondeo de `float` a `Decimal`.
   * **Cómo se arregla:** Afirmar contra el valor exacto redondeado.

5. **`test_envio_caba`**
   * **Clasificación:** Útil pero insuficiente
   * **Qué verifica realmente:** Que a CABA se cobre $2500.
   * **Qué error dejaría pasar:** El límite de envío gratis de $60.000.
   * **Cómo se arregla:** Probar el límite de $60.000 y zonas inválidas.

6. **`test_descuento_por_cantidad`**
   * **Clasificación:** Débil
   * **Qué verifica realmente:** Que aplique descuento a 6 prendas.
   * **Qué error dejaría pasar:** Que no aplique a 5 prendas (falla de límite `> 5` vs `>= 5`).
   * **Cómo se arregla:** Probar exactamente con 5 prendas.

7. **`test_talle_valido`**
   * **Clasificación:** Inútil
   * **Qué verifica realmente:** Nada, no tiene `assert`.
   * **Qué error dejaría pasar:** Cualquier error silencioso o retorno inesperado.
   * **Cómo se arregla:** Validar con `pytest.raises` un talle inválido.

8. **`test_no_explota_con_varios_productos`**
   * **Clasificación:** Inútil
   * **Qué verifica realmente:** Oculta errores con un `try/except Exception: pass`.
   * **Qué error dejaría pasar:** El código podría explotar por completo y el test daría verde.
   * **Cómo se arregla:** Borrar el `try/except` y afirmar el resultado real.

## 2. Puntaje de Mutación
* **Puntaje:** 58.6% (Sobreviven 12 de 29 mutantes).
* **Sobrevivientes clave:** Sobreviven los mutantes en los operadores límite (`<` por `<=`, `>` por `>=`) y en el límite del envío gratis (`60000` por `60001`). 

## 3. Párrafo de Cierre
La cobertura mide que la línea corrió, no que el resultado sea correcto. Los tests de la IA tienen asserts débiles o tautológicos. Por eso, aunque la cobertura es alta, la mutación lo confirma: sobrevivieron muchos errores en los bordes críticos. Lo que hace falta no es 100% de cobertura, sino valores esperados escritos a mano que prueben los límites.