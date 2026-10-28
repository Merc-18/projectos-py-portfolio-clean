# D-004 - Separador PDF

Adaptacion funcional del algoritmo original que extrae cada pagina de un PDF
con PyMuPDF (`insert_pdf`). Se eliminan referencias al entorno de origen.

## Ejecutar

```bash
python -m pip install -r requirements.txt
python separar_pdf.py ejemplo.pdf --output resultados
```

No altera el PDF de entrada ni sobrescribe archivos existentes. Incluye
pruebas sinteticas en `tests/test_migraciones.py` dentro del paquete de migracion.
El codigo original sigue en el repositorio privado de origen y esta adaptacion
no esta autorizada para publicacion publica.
