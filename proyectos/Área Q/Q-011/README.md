# Q-011 · Conciliación con detección de maestro

Adaptación del **procesamiento y cruce tabular** observado en el proyecto histórico. Se conservan los identificadores neutrales y se sustituyeron esquemas de datos reales por tres columnas sintéticas: `Codigo`, `Grupo` y `Inicio`/`Fin` cuando corresponda.

## Ejecución

```bash
python run.py --master-folder referencias --reports reportes --out resultados
```

La entrada maestra tiene `Codigo` y `Grupo`; cada reporte tiene `Codigo` y otras columnas opcionales. La salida es un Excel nuevo con `Grupo asignado` y `Estado` (ASIGNADO, SIN_MAPEO, AMBIGUO), sin sobrescribir archivos existentes. Este ticket utiliza modo **AUTODETECTAR** para conservar la diferencia funcional respecto a los demás tickets, reutilizando un único motor en `proyectos/portfolio_core/enrichment.py`.

No es una copia literal ni reproduce columnas internas. Los ensayos usan identificadores inventados. **Publicación pendiente de autorización.**
