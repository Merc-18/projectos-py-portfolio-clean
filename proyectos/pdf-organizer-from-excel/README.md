# PDF Organizer from Excel

Reads a mapping sheet (`Group ID`, `PDF 1`, `PDF 2`) and prepares copies of local PDF files into per-group folders.

```bash
python -m pip install -r requirements.txt
python generate_demo.py --root demo_mappings
python organize.py demo_mappings/mapping.xlsx demo_mappings/pdf_input organized
# The command above is preview-only. To actually copy the files:
python organize.py demo_mappings/mapping.xlsx demo_mappings/pdf_input organized --execute
python -m unittest discover -s tests -v
```

**Safety:** Default is dry-run: **no files copied**. `--execute` performs copies only after validating all mappings. Rejects `../`, absolute paths, group IDs containing directory separators, symlink escapes, missing files and source/output overlap. Automatically creates suffixes for duplicate target filenames and uses exclusive file creation to avoid overwrites. Processes up to 1,000 mapping rows and 100 MiB per PDF. No deletion or move operation is implemented.

The original workflow had unsafe filename collisions and group-path handling. This independent replacement addresses those cases without importing private source code.
