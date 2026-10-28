# Control de migración de código — 34 tickets

**No es un informe de pruebas de los 105 elementos:** distingue el estado de código únicamente de los 34 proyectos por ticket.

| Estado | Tickets |
|---|---:|
| Código funcional saneado o alternativa segura (privado) | **16** |
| Pendiente de saneamiento y revisión | **12** |
| Solo descripción, sin código por instrucción expresa | **6** |
| **Total** | **34** |

En los dieciséis proyectos con código, se trabajó a partir de su funcionalidad original conservando algoritmos relevantes, se eliminaron dependencias de entornos internos y se realizaron **61 pruebas locales acumuladas (18 anteriores, 14 del lote 03, 19 del lote 04 y 10 del lote 05) con datos ficticios**. No se presume equivalencia exacta con los originales, ni autorización para difusión pública.

## Estado individual

| Ticket | Estado | Motivo o alcance |
|---|---|---|
| Q-001 | CODIGO_SEGURO_PRIVADO | Conciliación tabular por clave; adaptación offline o alternativa no destructiva, sin autorización pública. |
| Q-002 | CODIGO_ADAPTADO_PRIVADO | Código genérico adaptado y pruebas sintéticas, sin autorización pública |
| Q-003 | CODIGO_ADAPTADO_PRIVADO | Código genérico adaptado y pruebas sintéticas, sin autorización pública |
| Q-004 | CODIGO_SEGURO_PRIVADO | Conservación selectiva de PDF; adaptación offline o alternativa no destructiva, sin autorización pública. |
| Q-005 | CODIGO_SEGURO_PRIVADO | Conciliación con fechas; adaptación offline o alternativa no destructiva, sin autorización pública. |
| Q-006 | CODIGO_SEGURO_PRIVADO | Conciliación multiclave; adaptación offline o alternativa no destructiva, sin autorización pública. |
| Q-007 | CODIGO_ADAPTADO_PRIVADO | Código genérico adaptado y pruebas sintéticas, sin autorización pública |
| Q-008 | SOLO_DESCRIPCION | Restricción expresa: no incorporar fuentes |
| Q-009 | SOLO_DESCRIPCION | Restricción expresa: no incorporar fuentes |
| Q-010 | SOLO_DESCRIPCION | Restricción expresa: no incorporar fuentes |
| Q-011 | CODIGO_SEGURO_PRIVADO | Conciliación con maestro detectado; adaptación offline o alternativa no destructiva, sin autorización pública. |
| Q-012 | CODIGO_SEGURO_PRIVADO | Organización documental desde Excel; adaptación offline o alternativa no destructiva, sin autorización pública. |
| Q-013 | CODIGO_ADAPTADO_PRIVADO | Word a Excel: extracción de casos; código revisado, 14 pruebas nuevas compartidas del lote, sin publicación autorizada. |
| Q-014 | SOLO_DESCRIPCION | Restricción expresa: no incorporar fuentes |
| Q-015 | CODIGO_ADAPTADO_PRIVADO | Similitud visual de PDF mediante pHash; código revisado, 14 pruebas nuevas compartidas del lote, sin publicación autorizada. |
| Q-016 | PENDIENTE_REVISION | Implementación extensa de documentos: revisión de dependencias y datos. |
| Q-017 | PENDIENTE_REVISION | Rutas y estructura documental interna: requiere parametrización. |
| Q-018 | PENDIENTE_REVISION | Integración con servicio autenticado: eliminar endpoints y credenciales. |
| Q-019 | SOLO_DESCRIPCION | Restricción expresa: no incorporar fuentes |
| Q-020 | PENDIENTE_REVISION | Contiene metadatos de solución de plataforma externa; revisión de derechos. |
| Q-021 | PENDIENTE_REVISION | Relación técnica con código de proyecto reservado: revisión reforzada. |
| D-001 | PENDIENTE_REVISION | Automatización de portal externo y condiciones de servicio por revisar. |
| D-002 | CODIGO_SEGURO_PRIVADO | Revisión offline de enlaces; adaptación offline o alternativa no destructiva, sin autorización pública. |
| D-003 | CODIGO_SEGURO_PRIVADO | Documentos de demostración PDF; adaptación offline o alternativa no destructiva, sin autorización pública. |
| D-004 | CODIGO_ADAPTADO_PRIVADO | Código genérico adaptado y pruebas sintéticas, sin autorización pública |
| D-005 | PENDIENTE_REVISION | Modificación de leyendas y fechas en documentos: requiere reformulación para uso legítimo. |
| D-006 | SOLO_DESCRIPCION | Restricción expresa: no incorporar fuentes |
| D-007 | CODIGO_ADAPTADO_PRIVADO | Código genérico adaptado y pruebas sintéticas, sin autorización pública |
| A-001 | PENDIENTE_REVISION | Flujo de firmas y documentos: reemplazar muestras y referencias identificables. |
| A-002 | PENDIENTE_REVISION | Flujo de firmas y documentos: eliminar referencias de origen. |
| A-003 | PENDIENTE_REVISION | Uso de imagen de firma: no publicar imágenes/personas ni formatos internos. |
| A-004 | PENDIENTE_REVISION | Bot autenticado: requiere entorno de simulación independiente. |
| A-005 | CODIGO_SEGURO_PRIVADO | Auditoría de carpetas; adaptación offline o alternativa no destructiva, sin autorización pública. |
| G-001 | PENDIENTE_REVISION | Interfaz dependiente de plantilla y entorno de escritorio; marcas y datos por revisar. |

## Protección de datos y código

No incluir datos reales, nombres de empresas, marcas internas, rutas de puestos de trabajo ni credenciales. Para los seis tickets reservados queda prohibido incorporar fuentes. Los 23 pendientes no deben copiarse literalmente: pueden contener infraestructura, identificadores o funciones que requieren una reformulación.

Los 71 trabajos antiguos (69 fichas visibles y 2 reservadas) conservan su propio proceso de clasificación; las seis demos genéricas no se contabilizan como proyectos adicionales.

**Toda la copia seguirá privada. El paso a pública requiere auditoría integral y aprobación expresa.**

## Lote 03 — Q-013 y Q-015

Se incorporaron los algoritmos saneados de extracción de casos en Word a Excel y comparación perceptual de PDF. Se ejecutaron **14 tests nuevos** con documentos creados para pruebas y se verificaron las salidas XLSX, CSV, PNG y DOCX. No se utilizaron archivos reales. La similitud perceptual no autentica firmas ni garantiza identidad documental.

## Lotes 04 y 05

Nueve tickets adicionales cuentan con implementaciones ejecutables: cinco herramientas offline y cuatro variantes de conciliación que comparten motor, para evitar duplicar código y pruebas. Se ejecutaron **29 pruebas nuevas** (19 + 10). Los módulos de archivos operan en modo simulación o copia segura; el documento D-003 está marcado SIN VALIDEZ OFICIAL. No se presume equivalencia integral con los desarrollos originales.
