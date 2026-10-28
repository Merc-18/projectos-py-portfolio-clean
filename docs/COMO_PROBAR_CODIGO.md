# Ejecución y pruebas de las cinco adaptaciones

Esta guía corresponde al código Python **adaptado y saneado** de cinco tickets, no al código literal de origen.

## Instalar dependencias

```bash
python -m venv .venv
# Active el entorno virtual según su sistema operativo.
python -m pip install -r requirements-tickets.txt
```

En Q-003 también necesita **Tesseract** instalado localmente con el idioma elegido. Se recomienda definir la ruta del ejecutable con `TESSERACT_CMD` si no se encuentra en PATH. Para las 18 pruebas actuales no es necesario procesar imágenes reales ni disponer de conexión a Internet.

## Ejecutar las pruebas

```bash
python -m unittest discover -s tests -p 'test_migraciones_tickets.py' -v
```

**Resultado de verificación local del 28 de octubre de 2026:** 18 pruebas correctas, sin archivos de la empresa y sin realizar solicitudes de red.

## Proyectos con código

| Código | Descripción | Archivo |
|---|---|---|
| D-004 | Separar PDF por páginas | [Código](<../proyectos/Área D/D-004/separar_pdf.py>) |
| D-007 | Segmentar PDF por blancos | [Código](<../proyectos/Área D/D-007/separar_pdf_blancas.py>) |
| Q-002 | Consolidar indicadores Excel | [Código](<../proyectos/Área Q/Q-002/consolidar_indicadores.py>) |
| Q-003 | OCR local de imágenes a Word | [Código](<../proyectos/Área Q/Q-003/ocr_a_word.py>) |
| Q-007 | Copiar PDF por tipo y período | [Código](<../proyectos/Área Q/Q-007/copiar_documentos.py>) |

Las pruebas cubren separación, clasificación, archivo Excel, exportación DOCX y prevención de sobrescrituras. **No equivalen a una validación integral** de OCR en fotografías difíciles, documentos corporativos, ni situaciones operativas reales.

**Mantener el repositorio privado:** el permiso de publicación del código todavía no está confirmado.


## Lote 03: Word → Excel y similitud PDF

```bash
python -m pip install -r 'proyectos/Área Q/Q-013/requirements.txt'
python -m pip install -r 'proyectos/Área Q/Q-015/requirements.txt'
python -m pip install pytest reportlab
python -m pytest -q tests/test_q013_q015.py
```

Q-013 necesita un documento Word sintético con columnas Zona, Lugar y Descripción. Q-015 requiere pares de PDF ficticios, con nombres similares. Las salidas se guardan en ubicaciones proporcionadas por el usuario y no se sobrescriben por defecto. El score pHash no verifica autenticidad de firmas.
