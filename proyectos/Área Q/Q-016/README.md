# Q-016 · Detector de duplicados PDF

Herramienta portátil de clasificación de duplicados: SHA-256 para duplicados exactos y un hash visual de la primera y última página para **candidatos a revisión manual**. El original integraba más heurísticas y tratamiento por categorías, que no se trasladan para no exponer reglas internas.

```bash
pip install -r requirements.txt
python pdf_duplicates.py pdfs_ficticios/ informe.csv
```

- No elimina ni mueve PDF; límite de 200 archivos por lote.
- `REVISAR_SIMILITUD` es una alerta heurística, **no prueba autenticidad ni duplicación fraudulenta**.
- Salida CSV protegida contra fórmulas y sobrescritura.
- Sin rutas de empresa ni documentos reales. Requiere revisión de licencias antes de publicación.
