# Q-012 · Organización de documentos desde Excel

Versión independiente y segura de la organización por categorías y códigos. El código del origen dependía de documentos de identidad; esta adaptación usa **códigos ficticios** (`Tipo`, `Zona`, `Codigo`) y no incluye datos personales.

```bash
pip install -r requirements.txt
python organize_from_excel.py mapa.xlsx documentos salida
python organize_from_excel.py mapa.xlsx documentos salida --execute
```

El primer comando solo presenta el plan; el segundo ejecuta copias sin sobreescritura. Bloquea segmentos `..`, rutas absolutas y caracteres peligrosos, y no modifica entradas. No intenta inferir identidades reales ni validar documentos oficiales. Requiere autorización antes de publicar.
