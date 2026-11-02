# Auditoría de equivalencia histórica — 2026-10-29

**Estado: PARCIAL / NO CERTIFICADA.** Este informe registra verificaciones de lectura sobre los repositorios privados; no constituye autorización de publicación ni acceso a archivos de clientes.

## Alcance y evidencia reproducible
- Origen: `Merc-18/projectos-py`, árbol de `main` `9852bc69d691b36faa792f6e1f6247cbf87ee908` (SHA de árbol).
- Destino: `Merc-18/projectos-py-portfolio-clean`, commit de `main` `447dd5255c59a78e4867be27e761666d1e2510fb`.
- En origen, la carpeta histórica `00_archivos_anteriores/` presenta 91 blobs y 78 archivos `.py`. Este conteo **no representa necesariamente 71 trabajos** ni establece correspondencia unívoca entre archivos y fichas.
- En destino, `historical_manifest.json` contiene exactamente 69 fichas visibles. Por estado: 51 `OFFLINE_RECONSTRUCTION`, 6 `LINKED_EXISTING_DEMO`, 8 `RELATED_NO_DUPLICATE_CODE`, 2 `DUPLICATE_NO_CODE`, 2 `RESTRICTED_NO_SOURCE`.
- Los 51 ejemplos reconstruidos poseen un `run.py`, pero son wrappers de `_shared/core.py`. La presencia de código, por sí sola, no prueba fidelidad respecto del programa histórico.
- La prueba `test_every_wrapper_with_fictional_inputs` **define** 51 ejecuciones con datos sintéticos; no se ejecutó la suite de pruebas en esta auditoría. Su resultado real actual es **NO VERIFICADO**.

## Comparación funcional de muestras (lectura estática)

| Grupo | Evidencia original | Destino revisado | Dictamen |
|---|---|---|---|
| Correo a Word | `00_archivos_anteriores/eml_to_word_ATC/eml_to_word_ATC.py`: 1146 líneas; clases `ExcelManager`, `EMLProcessor`; imports para DOCX, PDF, Excel, imágenes y combinación de PDF | `H050/run.py`: 9 líneas, delega en `_shared/core.py` con `eml_to_docx` | **NO EQUIVALENTE COMO APLICACIÓN COMPLETA**: la demostración cubre una idea funcional limitada, no se demuestra el flujo multiproducto |
| Comparación de Excel | `00_archivos_anteriores/excel_compare/excel_compare.py`: 303 líneas, clase `VLookupComparator`, bibliotecas pandas, numpy, fuzzywuzzy y openpyxl con formato | Métodos generales `compare_headers` y `fuzzy_csv` en `_shared/core.py`; ejemplos separados | **NO CERTIFICADA**: normalización/comparación genérica no demuestra equivalencia con la comparación enriquecida del original |
| OCR de PDF | `00_archivos_anteriores/pdf_ocr_converter/pdf_ocr_converter.py`: 236 líneas, clase `PDFOCRConverter`, PyMuPDF, pytesseract, PIL y FPDF | `ocr_pdf` en `_shared/core.py` y varios wrappers OCR | **NO CERTIFICADA**: no hay comparación de la totalidad de salidas, opciones y comportamiento con PDFs sintéticos |

Ninguna de estas observaciones autoriza trasladar código original al destino. Las comparaciones son de estructura y capacidad inferible; no se ha hecho ejecución diferencial.

## Matriz de situación
1. **69/69 fichas inventariadas:** comprobado por manifiesto.
2. **51 wrappers de reconstrucción:** comprobado por árbol del destino.
3. **6 demos enlazadas, 10 variantes/duplicados referenciados, 2 restringidas:** comprobado por manifiesto.
4. **69/69 equivalentes al original:** **NO DEMOSTRADO**.
5. **Auditoría dinámica, seguridad de historial, licencias y derechos de redistribución:** **PENDIENTE**.
6. **Publicación:** **PROHIBIDA** mientras falten autorización y revisión.

## Plan de cierre sin doble trabajo
- Construir matriz individual por H-ID con referencia de origen autorizada, entradas, salidas, decisiones de negocio, interfaz, errores y dependencias. Los 2 reservados permanecerán sin identidad ni detalles.
- Identificar si el H-ID es reconstrucción parcial, demo equivalente en alcance reducido, variante, duplicado o restringido. No presentar las demos como reproducciones completas.
- Preparar fixtures ficticios por caso y ejecutar **ambos** programas solo en un entorno aislado y autorizado; comparar salidas y efectos secundarios, sin datos corporativos reales.
- Registrar la diferencia funcional y recomendar reimplementación independiente para cada brecha; no importar código de origen ni secretos.
- Ejecutar tests y auditorías sobre **todas** las ramas, commits, etiquetas, archivos, binarios y metadatos antes de un eventual lanzamiento.
- Registrar revisión de licencia, titularidad y autorización de redistribución por artefacto, y mantener el repositorio privado hasta aprobación expresa.

## Conclusión
La **migración de presentación/inventario está cubierta**, pero la **equivalencia completa no está certificada**. Esta auditoría estática detecta brechas significativas y reduce el riesgo de declarar terminado un traslado fiel que todavía no se ha probado.

## Evidencia de pruebas automatizadas — 2026-10-30

- Ejecución GitHub Actions: https://github.com/Merc-18/projectos-py-portfolio-clean/actions/runs/41073313228
- Commit probado: `5dbe26147525710008fe2c233f7997c5a3974024`.
- `python -m compileall -q proyectos tests`: **PASS**.
- `python -m pytest -q tests proyectos --disable-warnings`: **171 passed, 11 subtests passed** en 13.20 segundos, **0 fallidos**.
- Configuración de CI corregida: dependencias Python de PDF, HTML, comparación, navegador (Playwright/Chromium) y OCR local (Tesseract). Se repararon las rutas relativas del manifiesto y se eliminó la dependencia de ruta fija a Chromium en la prueba.
- Alcance: **pruebas sintéticas automatizadas del portafolio**, incluyendo ejecución de los 51 wrappers de reconstrucciones históricas. Esta evidencia **no** valida equivalencia integral de cada código original con su reconstrucción, licencias, historial ni preparación para publicación.
- No se cambió `main` ni la visibilidad privada.

**Dictamen actualizado:** pruebas de regresión del portafolio en verde. Auditoría diferencial de equivalencia y auditoría integral de publicación siguen **pendientes**.
