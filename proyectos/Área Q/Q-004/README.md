# Q-004 · Conservación selectiva de PDF (versión segura)

Adaptación del flujo de selección y aplanamiento de PDF del desarrollo original. **El original podía borrar otros archivos; esta versión nunca elimina entradas ni directorios.**

```bash
python preserve_pdfs.py carpeta_origen carpeta_destino --keyword APROBADO
python preserve_pdfs.py carpeta_origen carpeta_destino --keyword APROBADO --execute
```

Sin `--execute` solamente muestra el plan. Con él copia los PDF coincidentes a carpetas de primer nivel, usa sufijos para evitar nombres duplicados y no sobrescribe resultados. No procesa enlaces simbólicos. El ejemplo se prueba con archivos ficticios. Mantener privado hasta revisión de derechos y seguridad.
