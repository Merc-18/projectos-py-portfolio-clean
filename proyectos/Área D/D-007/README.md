# D-007 - Separacion de PDF escaneados

Version saneada de la logica original: renderizar cada pagina, estimar su
porcentaje de pixeles oscuros, clasificar como blanco/contenido/indefinido y
separar bloques. Los ambiguos se guardan en `revisar/` y no se asumen validos.

```bash
python -m pip install -r requirements.txt
python separar_pdf_blancas.py ejemplo.pdf --output resultados
```

El archivo original no se modifica y la herramienta no sobrescribe resultados.
La deteccion depende de la calidad del escaneo; revise manualmente la salida.
Sin datos de origen ni autorizacion de publicacion publica.
