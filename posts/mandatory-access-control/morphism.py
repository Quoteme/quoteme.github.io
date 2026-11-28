"""Generate morphism.svg: a graph homomorphism f : G -> H, where
G = a -p-> b -q-> c and H = u -r-> v with a loop ℓ : v -> v.
f sends a to u, b and c to v, p to r and q to the loop ℓ.

Run: python3 morphism.py > morphism.svg
"""

# screen positions of the nodes
G_NODES = {"a": (80, 70), "b": (260, 70), "c": (440, 70)}
H_NODES = {"u": (80, 250), "v": (350, 250)}
G_ARCS = [("p", "a", "b"), ("q", "b", "c")]
H_ARCS = [("r", "u", "v")]
F_N = {"a": "u", "b": "v", "c": "v"}

FG = "#000"  # black and white only
MATH = "font-family=\"'Latin Modern Math','STIX Two Math','Cambria Math',serif\" font-style=\"italic\""


def shorten(a, b, d):
    """Shorten the screen segment a->b by d pixels at both ends."""
    (ax, ay), (bx, by) = a, b
    lx, ly = bx - ax, by - ay
    n = (lx * lx + ly * ly) ** 0.5
    ux, uy = lx / n, ly / n
    return (ax + ux * d, ay + uy * d), (bx - ux * d, by - uy * d)


out = []
w = out.append
w('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 540 330" '
  'font-family="sans-serif" font-size="17">')
w('<rect x="0" y="0" width="540" height="330" fill="#fff"/>')
w("<defs>")
w('<marker id="mo-arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
  'markerHeight="7" orient="auto-start-reverse">'
  f'<path d="M0,0 L10,5 L0,10 z" fill="{FG}"/></marker>')
w("</defs>")


def frame(x0, y0, x1, y1, label):
    w(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" rx="8" '
      f'fill="none" stroke="{FG}"/>')
    w(f'<text x="{x0 + 10}" y="{y0 + 22}" fill="{FG}" {MATH}>{label}</text>')


def arc(name, a, b, dy=-10):
    p, q = shorten(a, b, 10)
    w(f'<line x1="{p[0]:.1f}" y1="{p[1]:.1f}" x2="{q[0]:.1f}" y2="{q[1]:.1f}" '
      f'stroke="{FG}" stroke-width="1.6" marker-end="url(#mo-arr)"/>')
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    w(f'<text x="{mx:.1f}" y="{my + dy:.1f}" fill="{FG}" text-anchor="middle" '
      f'{MATH}>{name}</text>')


def node(name, pos, dy=-12):
    x, y = pos
    w(f'<circle cx="{x}" cy="{y}" r="5" fill="{FG}"/>')
    w(f'<text x="{x}" y="{y + dy}" fill="{FG}" text-anchor="middle" '
      f'{MATH}>{name}</text>')


frame(30, 20, 510, 110, "G")
frame(30, 200, 510, 310, "H")

# the node part f_N of the morphism, as dotted arrows from G down to H
for g, h in F_N.items():
    p, q = shorten(G_NODES[g], H_NODES[h], 10)
    w(f'<line x1="{p[0]:.1f}" y1="{p[1]:.1f}" x2="{q[0]:.1f}" y2="{q[1]:.1f}" '
      f'stroke="{FG}" stroke-dasharray="2 4" marker-end="url(#mo-arr)"/>')
w(f'<text x="35" y="160" fill="{FG}" {MATH}>f</text>')

for name, a, b in G_ARCS:
    arc(name, G_NODES[a], G_NODES[b])
for name, a, b in H_ARCS:
    arc(name, H_NODES[a], H_NODES[b])

# the loop ℓ : v -> v, to the right of v
vx, vy = H_NODES["v"]
w(f'<path d="M{vx + 8},{vy - 6} C{vx + 70},{vy - 50} {vx + 70},{vy + 50} '
  f'{vx + 8},{vy + 6}" fill="none" stroke="{FG}" stroke-width="1.6" '
  f'marker-end="url(#mo-arr)"/>')
w(f'<text x="{vx + 64}" y="{vy + 5}" fill="{FG}" {MATH}>ℓ</text>')

for name, pos in G_NODES.items():
    node(name, pos)
for name, pos in H_NODES.items():
    node(name, pos, dy=24)

w("</svg>")
print("\n".join(out))
