# Estado de codigo de los trabajos historicos

**Cobertura documentada:** 69 entradas visibles; **71 unidades** en el inventario con dos reservadas, que no se incluyen aqui.

| Estado | Cantidad | Alcance |
|---|---:|---|
| Reconstruccion segura offline | 51 | Codigo ejecutable propio y limitado, sin copiar fuente empresarial |
| Demo previamente verificada | 6 | Enlace a un ejemplo saneado existente, sin duplicarlo |
| Variante/componente relacionado | 8 | Enlace a la implementacion principal o de referencia |
| Duplicado exacto | 2 | Enlace a su canonico, sin repetir codigo |
| Restringido | 2 | Solo ficha y motivo de reserva, sin ejecutable |
| **Total** | **69** | |

Los **51 wrappers** se ejecutaron con documentos y archivos ficticios en pruebas automatizadas; la suite de **7 pruebas unittest** finalizo correctamente, incluida proteccion de salida, no sobrescritura y copia PDF simulada. No se han probado sistemas externos, datos reales ni equivalencia completa con los programas originales.

**Condicion vigente: privado.** Falta autorizacion de derechos, auditoria integral de todas las versiones Git y revision de dependencias antes de cualquier publicacion.

Consulta [el inventario](../proyectos/historicos/README.md), [las pruebas](../proyectos/historicos/tests/test_historicos.py) y [la auditoria preliminar](../AUDITORIA_PREPUBLICACION.md).
