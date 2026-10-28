# D-005 · Auditoría de fechas y leyendas PDF (alternativa segura)

La implementación histórica modificaba fechas y eliminaba leyendas de documentos. **Ese comportamiento no se incorpora al portafolio**. Esta herramienta ofrece una alternativa de solo lectura: detecta fechas y advertencias en archivos PDF y produce un CSV para revisión humana.

```bash
pip install -r requirements.txt
python pdf_audit.py carpeta_pdfs informe.csv
```

No cambia ni guarda PDFs originales, no permite simular autenticidad ni retirar advertencias. Usa archivos ficticios y documenta su limitación de alcance. La adopción pública requiere aprobación.
