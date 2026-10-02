#!/usr/bin/env python3
"""Static site generator for yogamaty.com.

    python3 tools/build.py

Reads   src/site.json            site-wide config (domain, Stripe link, API base, noindex switch, ...)
        src/i18n/<lang>.json     chrome strings per language (nav, footer, forms, passport UI)
        src/pages/<lang>/*.html  one Jinja template per page; `{% set path = "shop/wholesale" %}` sets its URL
        src/templates/           base layout + macros
Writes  <lang>/<path>/index.html, sitemap.xml, robots.txt, 404.html, index.html (language redirect),
        passport/index.html, data/media.json (manifest of passport photos found on disk)

Adding Nepali later = add src/i18n/ne.json and src/pages/ne/, then add "ne" to LANGS in src/site.json.
"""
import json, pathlib, re, datetime, sys
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
site = json.loads((SRC / "site.json").read_text(encoding="utf-8"))
LANGS = site["languages"]
BASE = site["origin"].rstrip("/")

env = Environment(loader=FileSystemLoader(str(SRC / "templates")), autoescape=select_autoescape(["html"]),
                  trim_blocks=True, lstrip_blocks=True)

# ---------------------------------------------------------------- motifs
SPEEDS = {"bg": 0.3, "mid": 0.6, "accent": 1.2, "fast": 1.35, "content": 1.0}
_motif_cache = {}
SYMBOLS = {"peacock"}


def _svg(name):
    if name not in _motif_cache:
        raw = (ROOT / "assets" / "motifs" / f"{name}.svg").read_text(encoding="utf-8")
        vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', raw).group(1).split()]
        _motif_cache[name] = (raw, vb)
    return _motif_cache[name]


def motif(name, size="md", layer="mid", style="", cls="", rot=0, rise=0, inline=False, mobile=True, speed=None, progress=None, dx=0, scale=0, flip=False):
    """A decorative motif. Static ones load lazily as CSS masks after first paint; animated ones are inlined."""
    raw, vb = _svg(name)
    s = SPEEDS[layer] if speed is None else speed
    ar = f"{vb[2]:.0f}/{vb[3]:.0f}"
    attrs = f'data-speed="{s}"'
    if progress:
        attrs += f' data-progress="{progress}"'
    if dx:
        attrs += f' data-dx="{dx}"'
    if scale:
        attrs += f' data-scale="{scale}"'
    if flip:
        style += ";--flip:-1"
    if rot:
        attrs += f' data-rot="{rot}"'
    if rise:
        style += f";--rise:{rise}"
    klass = f"motif motif--{size} {cls}" + ("" if mobile else " motif--hide-sm")
    if inline and name in SYMBOLS:       # defined once per page (see add_symbols), referenced here
        return Markup(f'<div class="{klass}" style="--ar:{ar};{style}" {attrs}><svg viewBox="{vb[0]:g} {vb[1]:g} {vb[2]:g} {vb[3]:g}" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><use href="#sym-{name}"/></svg></div>')
    if inline:
        return Markup(f'<div class="{klass}" style="--ar:{ar};{style}" {attrs}>{raw}</div>')
    return Markup(f'<div class="{klass} motif--mask" style="--ar:{ar};{style}" {attrs} data-mask="/assets/motifs/{name}.svg"></div>')


def divider(name, tone="white", rot=360):
    """A single rotating motif used as a section divider instead of a rule."""
    raw, vb = _svg(name)
    return Markup(f'<div class="divider divider--{tone}" aria-hidden="true"><div class="motif motif--mask motif--divider" '
                  f'style="--ar:{vb[2]:.0f}/{vb[3]:.0f}" data-speed="1" data-rot="{rot}" data-mask="/assets/motifs/{name}.svg"></div></div>')


STITCH_ORDER = [1, 5, 2, 4, 3, 7, 6, 8]


def stitch_divider(n):
    raw, _ = _svg(f"stitch-{n}")
    return f'<div class="stitchdiv" aria-hidden="true" data-progress="self">{raw}</div>'


def add_symbols(html):
    """Inline motifs used several times per page are defined once as <symbol>s right after <body>."""
    defs = ""
    for name in sorted(SYMBOLS):
        if f'href="#sym-{name}"' in html:
            raw, vb = _svg(name)
            inner = re.sub(r"^<svg[^>]*>|</svg>$", "", raw)
            defs += f'<symbol id="sym-{name}" viewBox="{vb[0]:g} {vb[1]:g} {vb[2]:g} {vb[3]:g}">{inner}</symbol>'
    if not defs:
        return html
    i = html.find(">", html.find("<body")) + 1
    return html[:i] + f'<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><defs>{defs}</defs></svg>' + html[i:]


def add_dividers(html):
    """Stitched divider at the bottom of every section in <main> except the last (the footer has its own rule)."""
    a, b = html.find('<main id="main">'), html.find("</main>")
    if a < 0 or b < 0:
        return html
    main = html[a:b]
    parts = main.split("</section>")
    out = []
    for i, part in enumerate(parts[:-1]):
        div = "" if i == len(parts) - 2 else stitch_divider(STITCH_ORDER[i % len(STITCH_ORDER)])
        m = re.search(r'<section[^>]*data-divider="([^"]+)"', part)      # per-section override: a divider number, or "none"
        if m:
            div = "" if m.group(1) == "none" else stitch_divider(int(m.group(1)))
        out.append(part + div + "</section>")
    out.append(parts[-1])
    return html[:a] + "".join(out) + html[b:]


def flow(base):
    """The passport flow (A-E): a horizontal piece for wide screens and a vertical one for phones. Nodes link to the passport tiers."""
    out = ""
    for kind in ("h", "v"):
        raw, _ = _svg(f"flow-{kind}")
        for letter in "ABCDE":
            raw = raw.replace(f'href="__{letter}__"', f'href="{base}#chain-{letter.lower()}"')
        out += f'<div class="flow flow-{kind}" data-progress="self">{raw}</div>'
    return Markup(out)


def ph(text):
    """A placeholder that must be replaced before launch (listed by tools/check-placeholders.py)."""
    return Markup(f'<span class="ph">[{text}]</span>')


def sold_out():
    return bool(site.get("sold_out"))


env.globals.update(motif=motif, divider=divider, flow=flow, ph=ph, site=site, sold_out=sold_out, BASE=BASE)

# ---------------------------------------------------------------- media manifest (passport photos by tier)
MEDIA_DIR = ROOT / "assets" / "media" / "passport"
TIER_RE = re.compile(r"^([A-E]\d)-(.+?)(?:-(\d{2}))?\.(webp|jpg|jpeg|mp4|webm)$", re.I)


def build_media_manifest():
    manifest = {}
    if MEDIA_DIR.exists():
        for p in sorted(MEDIA_DIR.iterdir()):
            m = TIER_RE.match(p.name)
            if not m or p.name.startswith("poster"):
                continue
            tier = m.group(1).upper()
            alt_file = p.with_suffix(".txt")
            alt = alt_file.read_text(encoding="utf-8").strip() if alt_file.exists() else ""
            kind = "video" if p.suffix.lower() in (".mp4", ".webm") else "image"
            entry = {"src": f"/assets/media/passport/{p.name}", "kind": kind, "alt": alt}
            if kind == "video":
                poster = MEDIA_DIR / f"{p.stem}.poster.webp"
                if poster.exists():
                    entry["poster"] = f"/assets/media/passport/{poster.name}"
            manifest.setdefault(tier, []).append(entry)
    (ROOT / "data").mkdir(exist_ok=True)
    (ROOT / "data" / "media.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    return manifest


# ---------------------------------------------------------------- pages
def dig(d, key):
    cur = d
    for part in key.split("."):
        cur = cur[part]
    return cur


def build_lang(lang, pages_out):
    strings = json.loads((SRC / "i18n" / f"{lang}.json").read_text(encoding="utf-8"))

    def t(key, **kw):
        try:
            v = dig(strings, key)
        except (KeyError, TypeError):
            print(f"  ! missing i18n key [{lang}] {key}", file=sys.stderr)
            return key
        return v.format(**kw) if kw else v

    def url(path=""):
        path = path.strip("/")
        return f"/{lang}/" + (path + "/" if path else "")

    page_dir = SRC / "pages" / lang
    for f in sorted(page_dir.glob("*.html")):
        source = f.read_text(encoding="utf-8")
        tpl = env.from_string(source)
        m = re.search(r'{%\s*set\s+path\s*=\s*"([^"]*)"\s*%}', source)
        path = m.group(1) if m else f.stem
        indexable = not re.search(r'{%\s*set\s+indexable\s*=\s*false\s*%}', source)
        ctx = dict(t=t, url=url, lang=lang, i18n=strings, js_strings=strings.get("js", {}), year=datetime.date.today().year,
                   current=path, page_path=path)
        html = tpl.render(**ctx)
        if path == "":                    # decorative artwork (motifs, stitched dividers) lives on the Home page only
            html = add_dividers(html)
        html = add_symbols(html)
        out = ROOT / lang / path / "index.html" if path else ROOT / lang / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html, encoding="utf-8")
        pages_out.append((lang, path, indexable))
        print(f"  {lang}/{path or ''}")


def write_extras(pages):
    today = datetime.date.today().isoformat()
    urls = []
    for lang, path, indexable in pages:
        if not indexable:
            continue
        loc = f"{BASE}/{lang}/" + (path + "/" if path else "")
        alts = "".join(f'<xhtml:link rel="alternate" hreflang="{l}" href="{BASE}/{l}/{path + "/" if path else ""}"/>' for l in LANGS) if len(LANGS) > 1 else ""
        urls.append(f"<url><loc>{loc}</loc><lastmod>{today}</lastmod>{alts}</url>")
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + "\n".join(urls) + "\n</urlset>\n", encoding="utf-8")
    (ROOT / "robots.txt").write_text(
        # Crawling stays allowed even while the test build carries noindex, so search engines can see the noindex tag.
        f"User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n", encoding="utf-8")

    default = site["default_language"]
    (ROOT / "index.html").write_text(env.get_template("redirect.html").render(
        target=f"/{default}/", langs=LANGS, default=default, site=site, noindex=site["noindex"]), encoding="utf-8")
    (ROOT / "passport").mkdir(exist_ok=True)
    (ROOT / "passport" / "index.html").write_text(env.get_template("redirect.html").render(
        target=f"/{default}/supply-chain/", langs=[default], default=default, site=site, noindex=site["noindex"]), encoding="utf-8")


def main():
    build_media_manifest()
    pages = []
    for lang in LANGS:
        print(f"[{lang}]")
        build_lang(lang, pages)
    write_extras(pages)
    # 404.html (also resolves QR-code URLs of the form /passport/<batch>?mat=<serial>)
    strings = json.loads((SRC / "i18n" / f"{site['default_language']}.json").read_text(encoding="utf-8"))
    lang = site["default_language"]

    def t(key, **kw):
        v = dig(strings, key)
        return v.format(**kw) if kw else v
    (ROOT / "404.html").write_text(env.get_template("404.html").render(
        t=t, url=lambda p="": f"/{lang}/" + (p.strip("/") + "/" if p.strip("/") else ""), lang=lang, i18n=strings,
        js_strings=strings.get("js", {}), year=datetime.date.today().year, current="", page_path="404"), encoding="utf-8")
    print("done")


if __name__ == "__main__":
    main()
