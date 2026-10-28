# Excel Workbook Consolidator

Consolidates the first row of each non-empty sheet as a header and joins rows across several XLSX files. It retains source file/sheet provenance and builds the union of column names.

```bash
python -m pip install -r requirements.txt
python generate_demo.py --dir demo_input
python consolidate.py demo_input consolidated.xlsx
python -m unittest discover -s tests -v
```

**Privacy and behavior:** Works offline. Demo data is synthetic. Does not change input files, does not overwrite output without `--overwrite`, and converts formula-like text to literal strings in the report. Maximum 100 files and 30,000 non-empty data rows. Rejects repeated header labels, and reads calculated Excel values when available. It does not evaluate Excel formulas or infer semantic column matches.

Clean standalone reimplementation; no company-specific code, names or workbooks.
