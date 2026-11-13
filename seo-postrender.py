"""Post-render SEO/GEO fixes for the rendered site (runs after every render).

For every page in the output directory:
- alias redirect pages: `noindex` + canonical to the redirect target
- draft posts (draft-mode: unlinked still publishes them): `noindex`
- missing <link rel="canonical">: added, using clean directory URLs
- missing meta description: derived from the subtitle or first paragraph;
  the generic site-wide og:/twitter:description is replaced with it
- blog posts: BlogPosting JSON-LD linked to the Person entity on the home page
sitemap.xml: `.../index.html` URLs rewritten to `.../` to match canonicals.

Idempotent; only touches pages that lack the respective element.
"""

import html
import json
import os
import posixpath
import re
from pathlib import Path

SITE_URL = "https://happel.ai/"
OUT = Path(os.environ.get("QUARTO_PROJECT_OUTPUT_DIR", "_site"))
SRC = Path(".")
PERSON = {"@id": SITE_URL + "#luca", "@type": "Person",
          "name": "Luca Leon Happel", "url": SITE_URL}
GENERIC_DESC = "Luca Happel builds, audits and hacks high-security systems"


def clean_url(rel: str) -> str:
    rel = rel.replace(os.sep, "/")
    if rel == "index.html":
        return SITE_URL
    if rel.endswith("/index.html"):
        return SITE_URL + rel[: -len("index.html")]
    return SITE_URL + rel


SUP = str.maketrans("0123456789+-nx", "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻ⁿˣ")
TEX = {r"\\ell": "ℓ", r"\\pi": "π", r"\\infty": "∞", r"\\times": "×", r"\\to": "→",
       r"\\cdot": "·", r"\\alpha": "α", r"\\beta": "β", r"\\exp": "exp"}
BB = {"R": "ℝ", "Z": "ℤ", "N": "ℕ", "Q": "ℚ", "C": "ℂ"}


def tex_to_text(tex: str) -> str:
    """Rough plain-text rendering of inline TeX for meta descriptions."""
    tex = tex.strip().strip("$").strip()
    tex = re.sub(r"^\\[\(\[]|\\[\)\]]$", "", tex).strip()
    tex = re.sub(r"\\mathbb\{?([A-Z])\}?", lambda m: BB.get(m.group(1), m.group(1)), tex)
    for k, v in TEX.items():
        tex = re.sub(k + r"(?![A-Za-z])", v, tex)
    tex = re.sub(r"\^(?:\{([0-9+\-nx]+)\}|([0-9nx]))",
                 lambda m: (m.group(1) or m.group(2)).translate(SUP), tex)
    tex = re.sub(r"\\[A-Za-z]+", "", tex)
    return re.sub(r"[{}_]", "", tex).strip()


def text_of(fragment: str) -> str:
    fragment = re.sub(r"<(script|style|svg)\b.*?</\1>", " ", fragment, flags=re.S)
    fragment = re.sub(r'<span class="math[^"]*">(.*?)</span>',
                      lambda m: " " + tex_to_text(html.unescape(m.group(1))) + " ",
                      fragment, flags=re.S)
    t = html.unescape(re.sub(r"<[^>]+>", " ", fragment))
    t = re.sub(r"\$\$.*?\$\$", " ", t, flags=re.S)
    t = re.sub(r"\$([^$]*)\$", lambda m: tex_to_text(m.group(1)), t)
    t = re.sub(r"\s+", " ", t).strip()
    return re.sub(r"\s+([,.;:!?)])", r"\1", t)


def shorten(t: str, limit: int = 155) -> str:
    if len(t) <= limit:
        return t
    cut = t[:limit].rsplit(" ", 1)[0].rstrip(",;:–-")
    return cut + "…"


def derive_description(page: str) -> str:
    m = re.search(r'<p class="subtitle[^"]*">(.*?)</p>', page, re.S)
    if m and len(text_of(m.group(1))) > 30:
        return shorten(text_of(m.group(1)))
    m = re.search(r'<div class="abstract">.*?<p>(.*?)</p>', page, re.S)
    if m and len(text_of(m.group(1))) > 30:
        return shorten(text_of(m.group(1)))
    main = re.search(r'<main\b.*?</main>', page, re.S)
    body = main.group(0) if main else page
    body = re.sub(r'<header\b.*?</header>', " ", body, flags=re.S)
    for p in re.findall(r"<p\b[^>]*>(.*?)</p>", body, re.S):
        t = text_of(p)
        if len(t) >= 60:
            return shorten(t)
    return ""


def is_draft(rel: str) -> bool:
    if not rel.endswith("index.html"):
        return False
    src = SRC / rel.replace("index.html", "index.qmd")
    if not src.exists():
        return False
    head = src.read_text(encoding="utf-8").split("\n---", 1)[0]
    return re.search(r"^draft:\s*true\s*$", head, re.M) is not None


def add_head(page: str, snippet: str) -> str:
    return page.replace("</head>", snippet + "\n</head>", 1)


def set_meta(page: str, attr: str, name: str, value: str) -> str:
    v = html.escape(value, quote=True)
    pat = re.compile(rf'<meta {attr}="{re.escape(name)}" content="[^"]*">')
    tag = f'<meta {attr}="{name}" content="{v}">'
    if pat.search(page):
        return pat.sub(lambda _: tag, page, count=1)
    return add_head(page, tag)


def blog_posting(page: str, rel: str, desc: str) -> str:
    title = re.search(r'<h1 class="title">(.*?)</h1>', page, re.S)
    if not title:
        return ""
    date = re.search(r'<meta name="dcterms.date" content="([^"]+)"', page)
    image = re.search(r'<meta property="og:image" content="([^"]+)"', page)
    lang = re.search(r'<html[^>]*\blang="([^"]+)"', page)
    cats = [text_of(c) for c in re.findall(r'<div class="quarto-category">(.*?)</div>', page, re.S)]
    cats = [c for c in cats if c.lower() not in ("english", "deutsch", "german")]
    data = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": text_of(title.group(1))[:110],
        "url": clean_url(rel),
        "mainEntityOfPage": clean_url(rel),
        "author": PERSON,
        "publisher": PERSON,
        "inLanguage": lang.group(1) if lang else "en",
        "isPartOf": {"@type": "Blog", "@id": SITE_URL + "blog.html#blog",
                     "name": "happel.ai Blog", "url": SITE_URL + "blog.html"},
    }
    if desc:
        data["description"] = desc
    if date:
        data["datePublished"] = date.group(1)
    if image:
        data["image"] = image.group(1)
    if cats:
        data["keywords"] = cats
        data["about"] = [{"@type": "Thing", "name": c} for c in cats]
    return ('<script type="application/ld+json">'
            + json.dumps(data, ensure_ascii=False) + "</script>")


def process(path: Path) -> bool:
    rel = path.relative_to(OUT).as_posix()
    page = path.read_text(encoding="utf-8")
    orig = page

    if "<title>Redirect</title>" in page:
        if 'name="robots"' not in page:
            target = re.search(r'var redirects = \{"":"([^"]+)"', page)
            snippet = '<meta name="robots" content="noindex, follow">'
            if target:
                dest = target.group(1)
                if not dest.startswith("/"):  # relative to the redirect page
                    dest = posixpath.join(posixpath.dirname(rel), dest)
                url = clean_url(posixpath.normpath(dest).lstrip("/"))
                snippet += f'\n<link rel="canonical" href="{url}">'
            page = add_head(page, snippet)
    else:
        if is_draft(rel) and 'name="robots"' not in page:
            page = add_head(page, '<meta name="robots" content="noindex, follow">')

        if 'rel="canonical"' not in page:
            page = add_head(page, f'<link rel="canonical" href="{clean_url(rel)}">')

        desc_m = re.search(r'<meta name="description" content="([^"]*)"', page)
        desc = html.unescape(desc_m.group(1)) if desc_m else ""
        if not desc:
            desc = derive_description(page)
            if desc:
                page = set_meta(page, "name", "description", desc)
        elif len(desc) > 160 or "$" in desc or "\\" in desc:
            desc = re.sub(r"\\[A-Za-z]+(?:\{[^}]*\})?(?:\^(?:\{[0-9+\-nx]+\}|[0-9nx]))?",
                          lambda m: tex_to_text(m.group(0)), desc)
            desc = shorten(text_of(html.escape(desc)))
            page = set_meta(page, "name", "description", desc)
        if desc:
            for attr, name in (("property", "og:description"), ("name", "twitter:description")):
                cur = re.search(rf'<meta {attr}="{name}" content="([^"]*)"', page)
                if not cur or cur.group(1).startswith(GENERIC_DESC):
                    page = set_meta(page, attr, name, desc)

        if rel.startswith("posts/") and '"BlogPosting"' not in page:
            ld = blog_posting(page, rel, desc)
            if ld:
                page = add_head(page, ld)

    if page != orig:
        path.write_text(page, encoding="utf-8")
        return True
    return False


def fix_sitemap() -> None:
    sm = OUT / "sitemap.xml"
    if not sm.exists():
        return
    t = sm.read_text(encoding="utf-8")
    new = re.sub(r"<loc>(https://[^<]*?/)index\.html</loc>", r"<loc>\1</loc>", t)
    if new != t:
        sm.write_text(new, encoding="utf-8")


def main() -> None:
    changed = sum(process(p) for p in OUT.rglob("*.html")
                  if not p.relative_to(OUT).as_posix().startswith("site_libs/"))
    fix_sitemap()
    print(f"seo-postrender: updated {changed} page(s)")


if __name__ == "__main__":
    main()
