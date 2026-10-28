# D-001 · Extracción de recursos desde HTML (offline)

El original consultaba un portal de contenido protegido. Esta adaptación transforma **archivos HTML ficticios locales** en un CSV de metadatos. No incluye scraping de portales privados, autenticación, cookies, nombres de proveedores ni endpoints originales.

```bash
pip install -r requirements.txt
python local_resources.py html_ficticio/ recursos.csv
```

Cada página de prueba contiene etiquetas `<article data-demo-id="...">`, título en `h2/h3`, descripción en `p` y enlace opcional. Solo conserva URL bajo `https://example.org/` o enlaces relativos. Se niega a sobrescribir y se defiende de fórmulas al abrir CSV en Excel. Esta versión **no es equivalente a un scraper remoto** y está pendiente de autorización pública.
