"""Post-render step: two-click consent for YouTube embeds (GDPR/TDDDG).

Every rendered <iframe src="https://www.youtube.com/embed/..."> (from raw
HTML or Quarto's {{< video >}} shortcode) gets a `srcdoc` placeholder. The
browser shows the placeholder instead of contacting YouTube; only clicking
its link navigates the iframe to youtube-nocookie.com. No JavaScript needed,
and the iframe keeps its size and attributes.

Runs via `project.post-render` in _quarto.yml and is idempotent.
"""

import html
import os
import re
from pathlib import Path

SITE = Path(os.environ.get("QUARTO_PROJECT_OUTPUT_DIR", "_site"))

IFRAME = re.compile(r"<iframe\b[^>]*>", re.IGNORECASE)
YT_SRC = re.compile(
    r'\bsrc="https?://(?:www\.)?youtube(?:-nocookie)?\.com/embed/([^"]+)"',
    re.IGNORECASE,
)

TEXT = {
    "en": (
        "Load video from YouTube",
        "Clicking loads the video from YouTube (Google). Your IP address is "
        "then transmitted to Google.",
        "Privacy policy",
    ),
    "de": (
        "Video von YouTube laden",
        "Mit dem Klick wird das Video von YouTube (Google) geladen. Dabei wird "
        "Ihre IP-Adresse an Google übermittelt.",
        "Datenschutzerklärung",
    ),
}

STYLE = (
    "html,body{height:100%;margin:0}"
    "body{display:flex;align-items:center;justify-content:center;"
    "background:#15181c;color:#d5d8dc;font:15px/1.4 system-ui,sans-serif;"
    "text-align:center;padding:1em;box-sizing:border-box}"
    "a.play{display:inline-block;padding:.6em 1.1em;margin-bottom:.8em;"
    "background:#c00;color:#fff;border-radius:6px;text-decoration:none;"
    "font-weight:600}"
    "a.play:hover{background:#e00}"
    "p{margin:0;font-size:12px;max-width:34em;opacity:.8}"
    "p a{color:#9cc3ea}"
)


def placeholder(video: str, lang: str) -> str:
    play, note, policy = TEXT[lang]
    # `video` is the attribute value from the rendered HTML (entities kept).
    sep = "&amp;" if "?" in video else "?"
    url = f"https://www.youtube-nocookie.com/embed/{video}{sep}autoplay=1"
    doc = (
        f"<!DOCTYPE html><html lang=\"{lang}\"><head><meta charset=\"utf-8\">"
        f"<style>{STYLE}</style></head><body><div>"
        f"<a class=\"play\" href=\"{url}\">&#9654; {play}</a>"
        f"<p>{note} <a href=\"/datenschutz.html\" target=\"_top\">{policy}</a></p>"
        f"</div></body></html>"
    )
    return html.escape(doc, quote=True)


def gate(tag: str, lang: str) -> str:
    m = YT_SRC.search(tag)
    if not m or "srcdoc=" in tag:
        return tag
    attrs = f' srcdoc="{placeholder(m.group(1), lang)}"'
    return tag[:-1] + attrs + ">"


def main() -> None:
    changed = 0
    for path in SITE.rglob("*.html"):
        text = path.read_text(encoding="utf-8")
        if "youtube" not in text:
            continue
        m = re.search(r'<html[^>]*\blang="([a-z]{2})', text)
        lang = "de" if m and m.group(1) == "de" else "en"
        new = IFRAME.sub(lambda t: gate(t.group(0), lang), text)
        if new != text:
            path.write_text(new, encoding="utf-8")
            changed += 1
    print(f"youtube-consent: gated YouTube embeds in {changed} file(s)")


if __name__ == "__main__":
    main()
