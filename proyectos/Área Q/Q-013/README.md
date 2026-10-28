# Q-013 · Extracción de tablas Word hacia Excel

**Código adaptado del flujo original, sin datos ni identificadores empresariales.**

Convierte eventos descritos en tablas `.docx` a una planilla `.xlsx` con zona, lugar, fechas, observaciones, acciones, resultado y enlaces. Reconoce encabezados `CASO N:` y `EVENTO N:` y dos órdenes de fechas.

```bash
python -m pip install -r requirements.txt
python word_a_excel.py ejemplo.docx reporte.xlsx
```

- Entrada: documento Word con una tabla cuya primera fila contiene cabeceras. Las tres primeras columnas son `Zona`, `Lugar` y `Descripción`.
- La salida no sobrescribe archivos a menos que se utilice `--overwrite`.
- Los textos con prefijo de fórmula de Excel se convierten a texto literal.
- No consulta servicios externos ni accede a carpetas internas.
- La adaptación es portable, con nombres y ejemplos completamente ficticios. No es una copia byte a byte ni certifica equivalencia integral con el flujo de origen.
- La publicación pública sigue pendiente de aprobación.
