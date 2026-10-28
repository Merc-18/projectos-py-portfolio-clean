# D-002 · Comparador de recursos web (modo offline)

Adaptación segura de la comparación de recursos y enlaces. El original consultaba Internet; esta herramienta **no realiza solicitudes HTTP ni accede a cuentas**. Solo normaliza URL, detecta duplicados y señala formatos sospechosos. **No afirma que los enlaces estén activos**.

```bash
pip install -r requirements.txt
python review_resources.py entrada.xlsx reporte.xlsx
```

El Excel debe contener una columna `URL` y opcionalmente `Autor`. La salida incluye pestañas `Revision`, `Duplicados` y `Resumen`. No sobrescribe sin `--overwrite`. Usar datos ficticios; no publicar hasta revisar los derechos.
