# Q-015 · Comparación de similitud visual de PDF

**Adaptación independiente del algoritmo original (pHash sobre la parte inferior de la última página)**. No contiene carpetas ni documentos originales.

Compara pares de documentos PDF con nombres similares y genera un CSV con la distancia visual (0–64) y un gráfico estadístico. Dos archivos con el mismo prefijo de diez caracteres forman un par; grupos ambiguos de tres o más se excluyen.

```bash
python -m pip install -r requirements.txt
python pdf_similarity.py carpeta_de_pdfs carpeta_de_reporte
```

- Funciona sin red, sin Poppler y sin cuentas de empresa, utilizando PyMuPDF y SciPy.
- El directorio de salida debe ser diferente de las entradas; no sobrescribe reportes salvo con `--overwrite`.
- Una coincidencia de pHash **no significa autenticidad, identidad ni validez de firma**. Los umbrales son descriptivos, no decisiones legales.
- Validado con PDFs ficticios. Pendiente de revisión adicional antes de publicación pública.
