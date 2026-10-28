# Control de migración de código — 34 tickets

**No es un informe de pruebas de los 105 elementos:** distingue el estado de código únicamente de los 34 proyectos por ticket.

| Estado | Tickets |
|---|---:|
| Código adaptado o alternativa ejecutable (privado) | **28** |
| Pendiente de una implementación privada | **0** |
| Solo descripción, sin código por instrucción expresa | **6** |
| **Total** | **34** |

Los 28 proyectos no reservados incluyen adaptaciones genéricas y **alternativas demostrativas**. Las segundas sustituyen funcionalidades sensibles (firmas, modificación de documentos oficiales, accesos corporativos o plantillas) por demostraciones ficticias. Las pruebas acumuladas de estas entregas son **93**: 18 anteriores y 75 de los lotes 03–07. Ninguna prueba acredita equivalencia exacta ni derecho de publicación pública.

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
| Q-016 | CODIGO_ADAPTADO_PRIVADO | Detección de duplicados PDF mediante hash; adaptación general del flujo técnico, sin publicación autorizada. |
| Q-017 | CODIGO_ADAPTADO_PRIVADO | Consolidación genérica de reportes Excel; adaptación general del flujo técnico, sin publicación autorizada. |
| Q-018 | ALTERNATIVA_DEMO_PRIVADA | Descarga HTTPS con consentimiento y simulación; solución alternativa funcional con datos ficticios, NO equivalente al desarrollo original, sin publicación autorizada. |
| Q-019 | SOLO_DESCRIPCION | Restricción expresa: no incorporar fuentes |
| Q-020 | ALTERNATIVA_DEMO_PRIVADA | Inspección anónima de estructura XML; solución alternativa funcional con datos ficticios, NO equivalente al desarrollo original, sin publicación autorizada. |
| Q-021 | ALTERNATIVA_DEMO_PRIVADA | Metadatos no sensibles de fotografías; solución alternativa funcional con datos ficticios, NO equivalente al desarrollo original, sin publicación autorizada. |
| D-001 | ALTERNATIVA_DEMO_PRIVADA | Extracción de recursos desde HTML local; solución alternativa funcional con datos ficticios, NO equivalente al desarrollo original, sin publicación autorizada. |
| D-002 | CODIGO_SEGURO_PRIVADO | Revisión offline de enlaces; adaptación offline o alternativa no destructiva, sin autorización pública. |
| D-003 | CODIGO_SEGURO_PRIVADO | Documentos de demostración PDF; adaptación offline o alternativa no destructiva, sin autorización pública. |
| D-004 | CODIGO_ADAPTADO_PRIVADO | Código genérico adaptado y pruebas sintéticas, sin autorización pública |
| D-005 | ALTERNATIVA_DEMO_PRIVADA | Auditoría no destructiva de fechas y leyendas PDF; solución alternativa funcional con datos ficticios, NO equivalente al desarrollo original, sin publicación autorizada. |
| D-006 | SOLO_DESCRIPCION | Restricción expresa: no incorporar fuentes |
| D-007 | CODIGO_ADAPTADO_PRIVADO | Código genérico adaptado y pruebas sintéticas, sin autorización pública |
| A-001 | ALTERNATIVA_DEMO_PRIVADA | Marcado ficticio PDF (alternativa sin firma); solución alternativa funcional con datos ficticios, NO equivalente al desarrollo original, sin publicación autorizada. |
| A-002 | ALTERNATIVA_DEMO_PRIVADA | Marcado ficticio PDF (variante sin firma); solución alternativa funcional con datos ficticios, NO equivalente al desarrollo original, sin publicación autorizada. |
| A-003 | ALTERNATIVA_DEMO_PRIVADA | Marcado ficticio PDF (otra disposición); solución alternativa funcional con datos ficticios, NO equivalente al desarrollo original, sin publicación autorizada. |
| A-004 | ALTERNATIVA_DEMO_PRIVADA | Automatización local de formularios de prueba; solución alternativa funcional con datos ficticios, NO equivalente al desarrollo original, sin publicación autorizada. |
| A-005 | CODIGO_SEGURO_PRIVADO | Auditoría de carpetas; adaptación offline o alternativa no destructiva, sin autorización pública. |
| G-001 | ALTERNATIVA_DEMO_PRIVADA | Formulario Streamlit para PDF ficticio; solución alternativa funcional con datos ficticios, NO equivalente al desarrollo original, sin publicación autorizada. |

## Protección de datos y código

No incluir datos reales, nombres de empresas, marcas internas, rutas de puestos de trabajo ni credenciales. Para los seis tickets reservados queda prohibido incorporar fuentes. Los flujos empresariales sensibles no se han copiado literalmente: se reemplazaron por alternativas locales y demostrativas que no dependen de datos o sistemas reales.

Los 71 trabajos antiguos (69 fichas visibles y 2 reservadas) conservan su propio proceso de clasificación; las seis demos genéricas no se contabilizan como proyectos adicionales.

**Toda la copia seguirá privada. El paso a pública requiere auditoría integral y aprobación expresa.**

## Lote 03 — Q-013 y Q-015

Se incorporaron los algoritmos saneados de extracción de casos en Word a Excel y comparación perceptual de PDF. Se ejecutaron **14 tests nuevos** con documentos creados para pruebas y se verificaron las salidas XLSX, CSV, PNG y DOCX. No se utilizaron archivos reales. La similitud perceptual no autentica firmas ni garantiza identidad documental.

## Lotes 04 y 05

Nueve tickets adicionales cuentan con implementaciones ejecutables: cinco herramientas offline y cuatro variantes de conciliación que comparten motor, para evitar duplicar código y pruebas. Se ejecutaron **29 pruebas nuevas** (19 + 10). Los módulos de archivos operan en modo simulación o copia segura; el documento D-003 está marcado SIN VALIDEZ OFICIAL. No se presume equivalencia integral con los desarrollos originales.

## Lotes 06 y 07 — cierre de los 28 tickets no reservados

Q-016, Q-017, Q-018 y D-001: **13 pruebas nuevas** de hash visual, reportes, HTTPS controlado y HTML local. A-001, A-002 y A-003 presentan **marcas ficticias**, nunca firmas reales. A-004 trabaja solo en una página local con solicitudes de red bloqueadas; D-005 audita PDF sin cambiar leyendas ni fechas; Q-020 resume XML sin exportar identidades; Q-021 no utiliza ningún código del proyecto reservado Q-019; G-001 genera PDF inequívocamente ficticios. Estos ocho últimos suman **19 pruebas nuevas**. Se mantiene la distinción documental entre adaptación y alternativa.

**Estado técnico:** 28 tickets con código ejecutable privado, 6 tickets de solo descripción, 0 sin implementación privada. **Estado de publicación:** todos pendientes de auditoría de derechos/licencias, privacidad y seguridad antes de cualquier cambio de visibilidad.
