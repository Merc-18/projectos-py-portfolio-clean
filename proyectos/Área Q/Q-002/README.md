# Q-002 - Consolidacion de indicadores Excel

Basada en la logica del proyecto original: varias hojas de indicadores por
periodo, `outer merge` sobre claves comunes y concatenacion de periodos.
Se reemplazaron etiquetas, nombres de informes y rutas organizativas.

Entrada esperada: ZIP con carpetas por periodo, cada una con
`serie_a.xlsx` (hoja `SERIE_A`), `serie_b.xlsx` (hoja `SERIE_B`), y
`serie_c.xlsx` (hoja `SERIE_C`), con columnas clave `ID` y `PERIODO`.

```bash
python -m pip install -r requirements.txt
python consolidar_indicadores.py datos_ficticios.zip resumen.xlsx
```

No descarga ni extrae ficheros del ZIP a disco. No sobreescribe salida.
Los nombres e indicadores son puramente ficticios; adapte las hojas para
sus propias fuentes. No contiene codigo ni valores empresariales originales.
