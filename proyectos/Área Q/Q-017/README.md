# Q-017 · Consolidación de reportes Excel

Adaptación de la lógica de recopilación de observaciones y reportes, eliminando rutas de red, nombres empresariales y esquemas internos. Busca planillas `.xlsx` recursivamente, lee columnas `Codigo` y `Observacion` y genera un reporte en tres pestañas.

```bash
pip install -r requirements.txt
python merge_reports.py carpeta_de_pruebas resumen.xlsx
```

- Utiliza archivos creados por el usuario; no se incluyen datos originales.
- No elimina ni sobrescribe entradas; el informe nuevo no puede sobrescribirse.
- El resultado incluye fuentes, observaciones y un resumen de planillas vacías.
- La estructura original de plantillas no está publicada. Esta versión no acredita equivalencia completa.
