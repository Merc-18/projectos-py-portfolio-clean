# Excel Column Matcher

Herramienta local que compara nombres en las columnas A y B de una hoja Excel, normalizando mayusculas, acentos y signos. Conserva todas las consultas de B y reporta coincidencias exactas, aproximadas y no encontradas.

## Demostracion local

```bash
python -m pip install -r requirements.txt
python generate_demo.py --output demo_entrada.xlsx
python matcher.py demo_entrada.xlsx resultado.xlsx --threshold 0.80
python -m unittest discover -s tests -v
```

El ejemplo crea datos totalmente ficticios; no requiere conexion a Internet ni servicios empresariales. No modifica el archivo de entrada y no sobrescribe una salida existente sin `--overwrite`. La hoja se puede escoger con `--sheet`.

**Limites:** compara solo las primeras dos columnas (A y B), no resuelve sinonimos ni asignaciones uno a uno, no interpreta formulas ni traduce idiomas. El puntaje es similitud de texto, no confianza estadistica. Las celdas que podrian ser formulas se exportan como texto.

Version nueva y autonoma creada para el portafolio; no incorpora codigo ni datos del repositorio fuente.
