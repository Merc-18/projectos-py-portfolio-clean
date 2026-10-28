# PDF Certificate Auditor (Read-Only)

Inspects file **names** to flag likely certificate PDFs for manual review, including accent-insensitive variants. Produces a CSV with classifications: `CERTIFICATE_CANDIDATE` or `MANUAL_REVIEW`.

```bash
python -m pip install -r requirements.txt
python generate_demo.py --root demo_documents
python audit.py demo_documents audit.csv
python -m unittest discover -s tests -v
```

**Safety:** Never deletes, moves or edits source files, and cannot output a report inside the scanned tree. Does not follow directory symlinks and does not overwrite the report without `--overwrite`. Classification uses filenames only and is *not* document authenticity verification. All unmatched files are for review, **not deletion**. Maximum 10,000 scanned files.

This is a deliberately non-destructive redesign of a generic file-audit workflow.
