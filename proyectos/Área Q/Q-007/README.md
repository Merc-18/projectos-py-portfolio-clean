# Q-007 - Copia selectiva de PDF por periodos

Retiene los componentes del algoritmo original de copia (busqueda de
subcarpetas, reconocimiento de mes, dos tipos de PDF y sufijos para evitar
colisiones). Sustituye todas las carpetas, patrones y rutas internos por
etiquetas ficticias `TIPO_A`, `TIPO_B` y `DOCUMENTOS`.

Organice un ejemplo propio como `entrada/ENERO/DOCUMENTOS/doc_TIPO_A.pdf` y
`entrada/FEBRERO/DOCUMENTOS/doc_TIPO_B.pdf`.

```bash
python copiar_documentos.py entrada/ resultados/
python copiar_documentos.py entrada/ resultados/ --execute
```

El modo por defecto solo muestra el plan, **sin copiar**. El modo execute
crea nuevas copias y no altera originales; se rechazan directorios solapados.
Solo usa Python estandar y no necesita datos personales ni red.
