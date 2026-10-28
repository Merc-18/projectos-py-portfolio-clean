# Q-018 · Descarga genérica controlada por manifiesto

**Adaptación independiente** de la descarga de documentos autenticados. No incluye endpoints, tenants, sesiones ni credenciales del origen. El mecanismo usa un manifiesto `Filename,URL`, una lista blanca de dominio HTTPS y un token de entorno cuando se activa.

```bash
pip install -r requirements.txt
python secure_downloader.py manifest.csv destino --domain ejemplo.org
# Solo sobre servicios propios o autorizados:
PORTFOLIO_TOKEN=... python secure_downloader.py manifest.csv destino --domain ejemplo.org --execute
```

- Por defecto **no solicita ni descarga ningún archivo**. Con `--execute` utiliza `PORTFOLIO_TOKEN` sin registrarlo ni guardarlo.
- Limita archivos a 20 MiB, bloquea redirecciones, rutas de salida inseguras y sobrescrituras.
- Las pruebas utilizan un cliente HTTP simulado, nunca el sistema de la empresa.
- No equivale al control de sesiones ni a los mecanismos específicos de plataformas de almacenamiento empresarial. Falta validación de integración con servicios propios y permisos antes de uso público.
