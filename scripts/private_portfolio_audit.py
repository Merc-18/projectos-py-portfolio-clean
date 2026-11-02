"""Private, read-only repository audit. No values of potential secrets are logged."""
from __future__ import annotations
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True, stderr=subprocess.PIPE).strip()

PATTERNS = {
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----", re.I),
    "aws_access_key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "github_token": re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}"),
    "openai_key": re.compile(r"sk-(?:proj-)?[A-Za-z0-9_-]{24,}"),
    "password_assignment": re.compile(r"(?i)(?:password|passwd|api[_-]?key|secret)\s*[:=]\s*['\"][^'\"]{8,}['\"]"),
}
RESTRICTED = re.compile(r"\b(?:" + "|".join(a+b for a,b in (("PRONA","TEL"),("DA","PA"),("GI","LAT"),("N","OC"))) + r")\b", re.I)
LIMIT = 2_000_000
def main():
    refs = git("for-each-ref", "--format=%(refname)").splitlines()
    objects = git("rev-list", "--objects", "--all").splitlines()
    scan = {"refs": len(refs), "objects": len(objects), "blobs": 0,
            "oversize_blobs": 0, "secret_pattern_hits": 0,
            "restricted_terms_hits": 0, "excluded_binary": 0}
    for entry in objects:
        # Scanner versions carry detection signatures and must not self-trigger.
        if entry.endswith(" scripts/private_portfolio_audit.py"): continue
        oid=entry.split(" ", 1)[0]
        if git("cat-file", "-t", oid) != "blob": continue
        scan["blobs"] += 1
        size=int(git("cat-file", "-s", oid))
        if size > LIMIT:
            scan["oversize_blobs"] += 1
            continue
        content=subprocess.check_output(["git", "cat-file", "blob", oid], cwd=ROOT)
        if b"\0" in content:
            scan["excluded_binary"] += 1
            continue
        value=content.decode("utf-8", errors="replace")
        if any(p.search(value) for p in PATTERNS.values()):
            scan["secret_pattern_hits"] += 1
        if RESTRICTED.search(value):
            scan["restricted_terms_hits"] += 1
    manifest=json.loads((ROOT/"proyectos/historicos/historical_manifest.json").read_text(encoding="utf-8"))
    records=manifest["records"]
    scan["records"]=len(records)
    scan["missing_wrappers"] = sum(1 for r in records if r["status"]=="OFFLINE_RECONSTRUCTION" and not (ROOT/r["code"]).is_file())
    scan["public_approved_records"]=sum(bool(r.get("public_approved")) for r in records)
    scan["top_level_license_present"]=any((ROOT/name).exists() for name in ("LICENSE", "LICENSE.md", "COPYING"))
    scan["rights_verified"]=False
    report=ROOT/"docs"/"AUDITORIA_AUTOMATIZADA_RESULTADOS.json"
    report.write_text(json.dumps(scan, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    print(json.dumps(scan, ensure_ascii=False))
    if scan["secret_pattern_hits"] or scan["restricted_terms_hits"] or scan["oversize_blobs"] or scan["missing_wrappers"] or scan["public_approved_records"]:
        raise SystemExit("REVIEW REQUIRED: security/inventory audit findings (details deliberately withheld)")
if __name__=="__main__": main()
