# Lote 01 - Herramientas autonomas

Estado: dos reimplementaciones limpias, en fase de revision privada; no aptas todavia para publicacion automatica.

| Proyecto nuevo | Objetivo | Fuente de ejemplo | Salida | Red |
|---|---|---|---|---|
| `excel-column-matcher` | Coincidencias A vs B en un Excel | XLSX ficticio generado localmente | XLSX | No |
| `pdf-field-extractor` | Extraccion de cuatro campos genericos | PDF ficticio generado localmente | CSV | No |

## Criterios de migracion

- No se copia codigo empresarial ni historial Git del repositorio original.
- No hay rutas locales de empleados, clientes, documentos reales ni secretos.
- Las salidas se guardan en rutas elegidas por quien ejecuta el programa.
- No se sobrescriben archivos existentes sin opcion explicita.
- Los ejemplos se generan bajo demanda, sin incluir binarios.
- Las pruebas funcionan sin red.
- Validacion funcional limitada a caracteristicas genericas y ejemplos sinteticos; no implica equivalencia con codigo anterior.

Las 105 unidades siguen en el inventario. Este lote no cambia la cifra de proyectos independientes confirmados y aun no resuelve la correspondencia privada Pxxx entre archivos fuente y demos.
