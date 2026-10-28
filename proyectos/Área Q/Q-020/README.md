# Q-020 · Inspección anonimizada de soluciones XML

**Demostración técnica alternativa**, no copia de la solución propietaria del origen. Inspecciona un XML local con estructura de componentes, cuenta elementos y omite intencionadamente nombres de empresa, editores, usuarios, identificadores internos y endpoints.

```bash
python inspect_solution.py ejemplo_sintetico.xml resumen.json
```

No exporta ni recrea procesos originales, no llama a sistemas externos y bloquea DTD/entidades XML. La solución original, sus flujos y metadatos **no se han incorporado**. Solo mostrar el código de este inspector genérico está sujeto a revisión y autorización de publicación.
