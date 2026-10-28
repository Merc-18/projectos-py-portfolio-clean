# PDF Field Extractor

Herramienta local para extraer cuatro etiquetas genericas (`Title`, `Reference`, `Date`, `Location`) de PDFs con texto seleccionable. Procesa un archivo o los PDFs de una carpeta y exporta CSV legible en Excel con estados `COMPLETE`, `PARTIAL` y `NO_TEXT`.

## Demostracion local

```bash
python -m pip install -r requirements.txt
python generate_demo.py --dir demo_pdfs
python extractor.py demo_pdfs resultado.csv
python -m unittest discover -s tests -v
```

Los documentos del ejemplo se generan con datos inventados. No hay conexion a Internet, claves, acceso a servicios corporativos ni escrituras en los PDFs de entrada. Una salida existente no se sobrescribe sin `--overwrite`.

**Limites:** requiere PDFs con capa de texto; no ejecuta OCR. Busca campos que aparezcan al comienzo de una linea con el formato `Label: value`. No valida semantica ni fechas; solo registra el primer valor encontrado por campo. Procesa por defecto hasta 30 paginas por archivo (`--max-pages`).

Version nueva y autonoma creada para el portafolio; no incorpora codigo ni datos del repositorio fuente.
