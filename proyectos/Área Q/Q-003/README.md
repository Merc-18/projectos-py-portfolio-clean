# Q-003 - OCR de imagenes a Word

Adaptacion del flujo original: ordenamiento numerico, ampliacion, contraste,
mascara de nitidez, binarizacion Otsu, Tesseract OCR y exportacion a DOCX.

```bash
python -m pip install -r requirements.txt
python ocr_a_word.py imagenes_ficticias/ --output resultados --lang spa
```

Necesita Tesseract instalado con el idioma elegido (`spa` por defecto). Si no
se encuentra en PATH, defina `TESSERACT_CMD` con el ejecutable del sistema.
Sin servicios remotos, rutas personales ni datos empresariales. No se
sobrescriben documentos. Antes de procesar documentos propios, revise las
transcripciones: OCR no garantiza precision perfecta.
