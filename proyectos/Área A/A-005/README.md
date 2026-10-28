# A-005 · Auditoría y selección de carpetas

El programa original seleccionaba carpetas de una región y eliminaba categorías de documentos en la copia. Esta adaptación usa grupos ficticios y **no borra archivos ni carpetas**, ni siquiera en el destino.

```bash
pip install -r requirements.txt
python folder_audit.py origen mapa.xlsx destino informe.xlsx --group DEMO
python folder_audit.py origen mapa.xlsx destino informe.xlsx --group DEMO --execute
```

La planilla contiene las columnas `Grupo` y `Codigo`. Sin `--execute` prepara un informe y un plan sin copiar. Con `--execute` solo copia archivos; el destino no puede estar dentro del origen. Se impide sobrescribir archivos existentes. No se incluye ningún nombre de empresa ni estructura real de clientes.
