#!/usr/bin/env python3
"""Make a relative-path copy of the built site (for hosts that serve it from a sub-path, e.g. an artifact preview).
    python3 tools/make_preview.py OUT_DIR
Production keeps root-absolute paths; this only post-processes a copy."""
import pathlib, re, shutil, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = pathlib.Path(sys.argv[1]); shutil.rmtree(OUT, ignore_errors=True)
for d in ("assets", "data"): shutil.copytree(ROOT / d, OUT / d, ignore=shutil.ignore_patterns("*.ttf"))
def rel(depth): return "../" * depth
pages = {}
for f in (ROOT / "en").rglob("index.html"):
    r = f.relative_to(ROOT)
    pages[r] = "index.html" if r == pathlib.Path("en/index.html") else str(r)
for src, dst in pages.items():
    html = (ROOT / src).read_text(encoding="utf-8")
    depth = dst.count("/"); pre = rel(depth)
    def fix(m):
        attr, path = m.group(1), m.group(2)
        if path.startswith("en/") and (path.endswith("/") ): path += "index.html"
        elif re.match(r"en/[^#?]*/(#|\?)", path): path = re.sub(r"/(#|\?)", r"/index.html\1", path, 1)
        if path in ("en/index.html", "en/"): path = "index.html"
        return f'{attr}="{pre}{path}"'
    html = re.sub(r'(href|src|poster|data-mask)="/(?!/)([^"]*)"', lambda m: fix(m) if True else m.group(0), html)
    html = html.replace('href="' + pre + 'en/index.html"', 'href="' + pre + 'index.html"')
    html = html.replace("window.YM={", f'window.YM={{root:"{pre}",idx:"index.html",', 1)
    html = re.sub(r'<meta http-equiv="refresh"[^>]*>', "", html)
    out = OUT / dst; out.parent.mkdir(parents=True, exist_ok=True); out.write_text(html, encoding="utf-8")
css = OUT / "assets/css/site.css"; css.write_text(css.read_text().replace("url(/assets/", "url(../"), encoding="utf-8")
# the root-absolute "/en/…" links that JS-free pages use for home resolve to index.html above
print("pages:", len(pages), "->", OUT)
