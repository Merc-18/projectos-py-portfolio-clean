# Q-021 · Inspector independiente de propiedades de imágenes

**Demostración separada, redactada desde cero.** El desarrollo original está relacionado con otro proyecto cuyo código permanece reservado; por ese motivo **no se copia ni se reutiliza ese analizador**.

Este inspector lee formato, dimensiones, orientación y si hay metadatos GPS (sí/no), pero **nunca exporta coordenadas, números de cámara, fechas EXIF ni etiquetas privadas**.

```bash
pip install -r requirements.txt
python image_metadata.py imagenes_ficticias/ auditoria.csv
```

Operación local de solo lectura. No representa una migración del analizador empresarial. Publicación pendiente de autorización.
