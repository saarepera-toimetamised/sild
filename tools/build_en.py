"""Generate en/index.html from index.html.

index.html is the source of truth (Estonian static text, English in data-en).
After editing index.html, run:  python3 tools/build_en.py
"""
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
s = (ROOT / "index.html").read_text(encoding="utf-8")


def rep(old, new):
    global s
    assert s.count(old) == 1, f"not found exactly once: {old[:60]}"
    s = s.replace(old, new)


# Body text: swap each element's content for its data-en value.
open_re = re.compile(r'<([a-zA-Z0-9]+)\b[^>]*\sdata-en="([^"]*)"[^>]*>')
out, pos = [], 0
for m in open_re.finditer(s):
    if m.start() < pos:
        continue
    tag, en = m.group(1), m.group(2)
    tok = re.compile(r"<(/?)%s\b[^>]*>" % tag)
    depth, i = 1, m.end()
    while depth:
        t = tok.search(s, i)
        depth += -1 if t.group(1) else 1
        i = t.end()
    inner = s[m.end():t.start()]
    if inner.strip():
        lead = re.match(r"\s*", inner).group(0)
        trail = re.search(r"\s*$", inner).group(0)
        inner = lead + html.unescape(en) + trail
    out += [s[pos:m.end()], inner]
    pos = t.start()
out.append(s[pos:])
s = "".join(out)

# Head: English metadata.
rep('<html lang="et">', '<html lang="en">')
s = re.sub(r"<title>.*?</title>",
           "<title>Realbon translation — Estonian ⇄ English translator</title>", s)
s = re.sub(r'<meta name="description" content="[^"]*">',
           '<meta name="description" content="Science, medicine, technology and culture '
           'translation between Estonian and English by a Tallinn-based translator. '
           'Quotes within one working day.">', s)
rep('<link rel="canonical" href="https://tolked.realbon.eu/">',
    '<link rel="canonical" href="https://tolked.realbon.eu/en/">')
rep('<meta property="og:url" content="https://tolked.realbon.eu/">',
    '<meta property="og:url" content="https://tolked.realbon.eu/en/">')
s = re.sub(r'<meta property="og:title" content="[^"]*">',
           '<meta property="og:title" content="Realbon translation — your personal translation bureau">', s)
s = re.sub(r'<meta property="og:description" content="[^"]*">',
           '<meta property="og:description" content="Science, medicine, technology and culture '
           'translation, Estonian ⇄ English. Quotes within one working day.">', s)
rep('<meta property="og:locale" content="et_EE">', '<meta property="og:locale" content="en_GB">')
s = re.sub(r'<meta property="og:image:alt" content="[^"]*">',
           '<meta property="og:image:alt" content="Realbon translation — Estonian ⇄ English">', s)
rep('aria-pressed="false" onclick="setLang(\'en\')"', 'aria-pressed="true" onclick="setLang(\'en\')"')
rep('aria-pressed="true" onclick="setLang(\'et\')"', 'aria-pressed="false" onclick="setLang(\'et\')"')
rep("?subject=Hinnap%C3%A4ring", "?subject=Translation%20quote%20request")

(ROOT / "en").mkdir(exist_ok=True)
(ROOT / "en" / "index.html").write_text(s, encoding="utf-8")
print("wrote en/index.html")
