"""Generate global-element.svg: a global element x : 1 -> X of a graph X,
where 1 is the terminal graph (a node * with a loop !) and
X = a -p-> b -q-> c with a loop l : b -> b.
x sends * to b and ! to the loop l, shown as dotted arrows.

Run: python3 global-element.py > global-element.svg
"""

FG = "#000"  # black and white only
MATH = "font-family=\"'Latin Modern Math','STIX Two Math','Cambria Math',serif\" font-style=\"italic\""

STAR = (300, 75)
X_NODES = {"a": (90, 250), "b": (300, 250), "c": (480, 250)}
X_ARCS = [("p", "a", "b"), ("q", "b", "c")]


def shorten(a, b, d):
    """Shorten the screen segment a->b by d pixels at both ends."""
    (ax, ay), (bx, by) = a, b
    lx, ly = bx - ax, by - ay
    n = (lx * lx + ly * ly) ** 0.5
    ux, uy = lx / n, ly / n
    return (ax + ux * d, ay + uy * d), (bx - ux * d, by - uy * d)


out = []
w = out.append
w('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 540 360" '
  'font-family="sans-serif" font-size="17">')
w('<rect x="0" y="0" width="540" height="360" fill="#fff"/>')
w("<defs>")
w('<marker id="ge-arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
  'markerHeight="7" orient="auto-start-reverse">'
  f'<path d="M0,0 L10,5 L0,10 z" fill="{FG}"/></marker>')
w("</defs>")


def frame(x0, y0, x1, y1, label):
    w(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" rx="8" '
      f'fill="none" stroke="{FG}"/>')
    w(f'<text x="{x0 + 10}" y="{y0 + 22}" fill="{FG}" {MATH}>{label}</text>')


def node(name, pos, dx=0, dy=-12, anchor="middle"):
    x, y = pos
    w(f'<circle cx="{x}" cy="{y}" r="5" fill="{FG}"/>')
    w(f'<text x="{x + dx}" y="{y + dy}" fill="{FG}" text-anchor="{anchor}" '
      f'{MATH}>{name}</text>')


def loop_left(pos):
    """A loop to the left of the node at pos; returns its apex."""
    x, y = pos
    w(f'<path d="M{x - 8},{y + 6} C{x - 70},{y + 50} {x - 70},{y - 50} '
      f'{x - 8},{y - 6}" fill="none" stroke="{FG}" stroke-width="1.6" '
      f'marker-end="url(#ge-arr)"/>')
    return x - 54, y


def loop_below(pos):
    """A loop below the node at pos; returns its apex."""
    x, y = pos
    w(f'<path d="M{x + 6},{y + 8} C{x + 50},{y + 70} {x - 50},{y + 70} '
      f'{x - 6},{y + 8}" fill="none" stroke="{FG}" stroke-width="1.6" '
      f'marker-end="url(#ge-arr)"/>')
    return x, y + 54


frame(30, 20, 510, 130, "1")
frame(30, 190, 510, 340, "X")

# the terminal graph 1
bang = loop_left(STAR)
w(f'<text x="{bang[0] - 8}" y="{bang[1] + 5}" fill="{FG}" text-anchor="end" '
  f'{MATH}>!</text>')
node("*", STAR, dx=12, dy=5, anchor="start")

# the graph X
for name, s, t in X_ARCS:
    p, q = shorten(X_NODES[s], X_NODES[t], 10)
    w(f'<line x1="{p[0]:.1f}" y1="{p[1]:.1f}" x2="{q[0]:.1f}" y2="{q[1]:.1f}" '
      f'stroke="{FG}" stroke-width="1.6" marker-end="url(#ge-arr)"/>')
    mx = (X_NODES[s][0] + X_NODES[t][0]) / 2
    if name == "p":  # keep the label clear of the dotted arrow from !
        mx -= 45
    w(f'<text x="{mx:.1f}" y="{X_NODES[s][1] - 10}" fill="{FG}" '
      f'text-anchor="middle" {MATH}>{name}</text>')
ell = loop_below(X_NODES["b"])
w(f'<text x="{ell[0] + 30}" y="{ell[1] + 4}" fill="{FG}" {MATH}>ℓ</text>')
for name, pos in X_NODES.items():
    if name == "b":  # keep the label clear of the dotted arrow from *
        node(name, pos, dx=10, dy=-12, anchor="start")
    else:
        node(name, pos)

# the global element x, as dotted arrows: * to b, and ! around to ℓ
p, q = shorten(STAR, X_NODES["b"], 12)
w(f'<line x1="{p[0]:.1f}" y1="{p[1]:.1f}" x2="{q[0]:.1f}" y2="{q[1]:.1f}" '
  f'stroke="{FG}" stroke-dasharray="2 4" marker-end="url(#ge-arr)"/>')
w(f'<text x="{STAR[0] + 8}" y="165" fill="{FG}" {MATH}>x</text>')
sx, sy = bang[0] - 6, bang[1] + 10
ex, ey = ell[0] - 8, ell[1] + 4
w(f'<path d="M{sx},{sy} C{sx - 80},{sy + 120} {ex - 110},{ey + 10} {ex},{ey}" '
  f'fill="none" stroke="{FG}" stroke-dasharray="2 4" '
  f'marker-end="url(#ge-arr)"/>')

w("</svg>")
print("\n".join(out))
