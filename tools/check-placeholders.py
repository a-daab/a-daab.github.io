#!/usr/bin/env python3
"""List every [PLACEHOLDER] still on the site. Exit code 1 if any remain (use before launch).
    python3 tools/check-placeholders.py
Scans the built pages (en/**), data/*.json and src/site.json."""
import pathlib, re, json, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
found = {}
for f in sorted(ROOT.glob("en/**/index.html")):
    for m in re.finditer(r'<span class="ph">\[([^\]]+)\]</span>', f.read_text(encoding="utf-8")):
        found.setdefault(m.group(1), set()).add(str(f.relative_to(ROOT)))
batch_nulls = 0
for f in ROOT.glob("data/batches/*.json"):
    def walk(o):
        global batch_nulls
        if isinstance(o, dict):
            for k, v in o.items():
                if not k.startswith("_"): walk(v)
        elif o is None: batch_nulls += 1
    walk(json.loads(f.read_text(encoding="utf-8")))
site = json.loads((ROOT / "src/site.json").read_text(encoding="utf-8"))
todo = [k for k in ("api_base", "turnstile_site_key", "stripe_payment_link", "whitepaper_url") if not site.get(k)]
if site.get("noindex"): todo.append("noindex is still ON (python3 tools/set-indexing.py index)")
print(f"{len(found)} distinct placeholders on built pages:")
for k, pages in sorted(found.items()): print(f"  [{k}]  ({len(pages)} page{'s' if len(pages) > 1 else ''})")
print(f"\n{batch_nulls} unfilled values in data/batches/*.json (render as [ADD ...] on the passport)")
print("site.json settings still empty/on:", ", ".join(todo) or "none")
sys.exit(1 if found or batch_nulls or todo else 0)
