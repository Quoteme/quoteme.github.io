"""Generate initial-terminal.svg: the initial object 0 (the empty graph) and the
terminal object 1 (a single node with a single loop) of the topos of graphs.

Run: python3 initial-terminal.py > initial-terminal.svg
"""

FG = "#000"  # black and white only
MATH = "font-family=\"'Latin Modern Math','STIX Two Math','Cambria Math',serif\""

out = []
w = out.append
w('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 170" '
  'font-family="sans-serif" font-size="17">')
w('<rect x="0" y="0" width="420" height="170" fill="#fff"/>')
w("<defs>")
w('<marker id="it-arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
  'markerHeight="7" orient="auto-start-reverse">'
  f'<path d="M0,0 L10,5 L0,10 z" fill="{FG}"/></marker>')
w("</defs>")


def frame(x0, y0, x1, y1, label):
    w(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" rx="8" '
      f'fill="none" stroke="{FG}"/>')
    w(f'<text x="{(x0 + x1) / 2}" y="{y1 + 26}" fill="{FG}" '
      f'text-anchor="middle" {MATH}>{label}</text>')


# 0: the empty graph
frame(20, 20, 190, 130, "0")

# 1: a single node with a single loop
frame(230, 20, 400, 130, "1")
vx, vy = 290, 75
w(f'<path d="M{vx + 8},{vy - 6} C{vx + 70},{vy - 50} {vx + 70},{vy + 50} '
  f'{vx + 8},{vy + 6}" fill="none" stroke="{FG}" stroke-width="1.6" '
  f'marker-end="url(#it-arr)"/>')
w(f'<circle cx="{vx}" cy="{vy}" r="5" fill="{FG}"/>')
w(f'<text x="{vx - 14}" y="{vy + 5}" fill="{FG}" text-anchor="end" '
  f'font-style="italic" {MATH}>*</text>')
w(f'<text x="{vx + 64}" y="{vy + 5}" fill="{FG}" font-style="italic" '
  f'{MATH}>!</text>')

w("</svg>")
print("\n".join(out))
