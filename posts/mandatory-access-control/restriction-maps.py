"""Generate restriction-maps-id.svg and restriction-maps-twist.svg: the graph
a -> b <- c on the x-z plane, with a stalk Bool = {⊥, ⊤} above every node and
the restriction maps Y(b) -> Y(a) and Y(b) -> Y(c) drawn between the stalks.

Run: python3 restriction-maps.py id > restriction-maps-id.svg
     python3 restriction-maps.py twist > restriction-maps-twist.svg
"""

import sys

# floor positions (x, z): the parent b sits behind its two children
NODES = {"a": (0.0, 0.0), "b": (1.3, 1.6), "c": (2.6, 0.0)}
# edges child -> parent
EDGES = [("a", "b"), ("c", "b")]

BOT_Y, TOP_Y = 1.5, 2.5
FLOOR = (-0.5, 3.1, -0.6, 2.1)  # x0, x1, z0, z1

FG = "#000"  # black and white only


def proj(x, y, z):
    """Oblique projection: x to the right, y up, z into the screen."""
    return 40 + 90 * x + 30 * z, 330 - 80 * y - 45 * z


def pt(x, y, z):
    sx, sy = proj(x, y, z)
    return f"{sx:.1f},{sy:.1f}"


def shorten(a, b, d):
    """Shorten the screen segment a->b by d pixels at both ends."""
    (ax, ay), (bx, by) = a, b
    lx, ly = bx - ax, by - ay
    n = (lx * lx + ly * ly) ** 0.5
    ux, uy = lx / n, ly / n
    return (ax + ux * d, ay + uy * d), (bx - ux * d, by - uy * d)


def restriction(child, value, twist):
    """Y(p)(value) for the edge p : child -> b."""
    return (not value) if (twist and child == "a") else value


twist = len(sys.argv) > 1 and sys.argv[1] == "twist"

out = []
w = out.append
# viewBox: the floor's corners and the stalk tops, plus a margin
x0, x1, z0, z1 = FLOOR
xs, ys = zip(*[proj(x, 0, z) for x in (x0, x1) for z in (z0, z1)]
             + [proj(x, TOP_Y + 0.35, z) for x, z in NODES.values()])
vx, vy = min(xs) - 25, min(ys) - 10
vw, vh = max(xs) - vx + 10, max(ys) - vy + 10
w(f'<svg xmlns="http://www.w3.org/2000/svg" '
  f'viewBox="{vx:.0f} {vy:.0f} {vw:.0f} {vh:.0f}" '
  f'font-family="sans-serif" font-size="13">')
w(f'<rect x="{vx:.0f}" y="{vy:.0f}" width="{vw:.0f}" height="{vh:.0f}" '
  f'fill="#fff"/>')
w("<defs>")
w(f'<marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" '
  f'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
  f'<path d="M0,0 L10,5 L0,10 z" fill="{FG}"/></marker>')
w("</defs>")

# floor plane (the graph X lives here)
w(f'<polygon points="{pt(x0,0,z0)} {pt(x1,0,z0)} {pt(x1,0,z1)} {pt(x0,0,z1)}" '
  f'fill="#fff" stroke="{FG}"/>')
lx, ly = proj(x0, 0, z1)  # back-left corner, away from the edges
w(f'<text x="{lx + 12:.1f}" y="{ly + 18:.1f}" text-anchor="start" fill="{FG}" '
  f'font-style="italic">X</text>')

# floor edges
for a, b in EDGES:
    (ax, az), (bx, bz) = NODES[a], NODES[b]
    (sx, sy), (ex, ey) = shorten(proj(ax, 0, az), proj(bx, 0, bz), 9)
    w(f'<line x1="{sx:.1f}" y1="{sy:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" '
      f'stroke="{FG}" stroke-width="1.5" marker-end="url(#arr)"/>')

# stalks
for name, (x, z) in NODES.items():
    fx, fy = proj(x, 0, z)
    tx, ty = proj(x, TOP_Y + 0.35, z)
    w(f'<line x1="{fx:.1f}" y1="{fy:.1f}" x2="{tx:.1f}" y2="{ty:.1f}" '
      f'stroke="{FG}" stroke-dasharray="2 4"/>')

# restriction maps Y(b) -> Y(child), from the parent's stalk to the child's
for child, _ in EDGES:
    (cx, cz), (bx, bz) = NODES[child], NODES["b"]
    for val in (False, True):
        img = restriction(child, val, twist)
        yb = TOP_Y if val else BOT_Y
        yc = TOP_Y if img else BOT_Y
        (sx, sy), (ex, ey) = shorten(proj(bx, yb, bz), proj(cx, yc, cz), 10)
        w(f'<line x1="{sx:.1f}" y1="{sy:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" '
          f'stroke="{FG}" stroke-width="1.5" marker-end="url(#arr)"/>')

# nodes on the floor and the two points of each stalk
for name, (x, z) in NODES.items():
    fx, fy = proj(x, 0, z)
    w(f'<circle cx="{fx:.1f}" cy="{fy:.1f}" r="5" fill="{FG}"/>')
    dx, dy = (10, -8) if name == "b" else (9, 17)
    w(f'<text x="{fx + dx:.1f}" y="{fy + dy:.1f}" fill="{FG}" '
      f'font-style="italic" font-size="15">{name}</text>')
    for y, sym in ((BOT_Y, "⊥"), (TOP_Y, "⊤")):
        sx, sy = proj(x, y, z)
        w(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="7" fill="#fff" '
          f'stroke="{FG}" stroke-width="1.5"/>')
        w(f'<text x="{sx - 13:.1f}" y="{sy + 5:.1f}" text-anchor="end" '
          f'fill="{FG}" font-size="15">{sym}</text>')

w("</svg>")
print("\n".join(out))
