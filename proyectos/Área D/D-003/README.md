# D-003 · Generador de documentos de demostración

El desarrollo original generaba documentos personalizados utilizando una plantilla Word empresarial. Para no reproducir certificados ni identidades reales, esta adaptación **genera únicamente PDF ficticios claramente marcados “SIN VALIDEZ OFICIAL”**.

```bash
pip install -r requirements.txt
python make_demo_documents.py nombres_ficticios.xlsx salida
```

La planilla requiere `Nombre` y `Codigo` (identificadores inventados). Cada documento queda marcado como demostración, no contiene logos ni firmas, y no se sobrescribe. Esta es una adaptación de seguridad, no una reproducción exacta de los certificados originales.
