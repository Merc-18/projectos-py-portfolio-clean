# A-004 — Automatización local de formularios web

**Alternativa demostrativa segura.** No contiene ni usa credenciales, URLs, nombres de empresas, flujos empresariales ni automatizaciones sobre sitios reales.

Automatiza un formulario HTML sintético con Playwright, comprueba que sus tres valores fueron escritos y guarda una captura PNG. El HTML está integrado en el código, no tiene acción de envío y toda solicitud de red se bloquea. No automatiza formularios reales ni representa una migración fiel del bot original.

```bash
pip install -r requirements.txt
python offline_form_bot.py ejemplo.json captura.png --chromium /usr/bin/chromium
```

Ejemplo ficticio de `ejemplo.json`: `{"codigo":"DEMO-001","fecha":"2026-01-01","asunto":"Prueba local"}`. Requiere Chromium instalado (en algunos entornos se puede utilizar el navegador de Playwright si está disponible). La captura no se sobrescribe.

El código del proyecto original **no** se publica. El repositorio es privado y no está autorizado para difusión pública.
