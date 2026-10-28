# Folder Inventory Report

Generates an XLSX inventory of leaf directories, listing relative directory paths, total files and PDF counts. Ignores desktop metadata files and does not traverse symbolic links.

```bash
python -m pip install -r requirements.txt
python generate_demo.py --root demo_tree
python inventory.py demo_tree inventory.xlsx
python -m unittest discover -s tests -v
```

**Privacy and behavior:** Operates offline, reporting only paths relative to the selected root. Does not move/delete files or follow directory links. Output is not overwritten unless `--overwrite` is supplied. Maximum 10,000 leaf folders. Names inside a real directory could still contain private information: use synthetic trees for demonstrations and review reports before sharing.

Clean standalone reimplementation; no company-specific paths or folders.
