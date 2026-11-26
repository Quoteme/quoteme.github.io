"""Generate subgraph.svg: the cwd/ graph X on a bottom plane, the subgraph Y
without cwd/sub/file2 on a top plane, and dotted arrows from every node of Y
down to the node of X it corresponds to.

With the argument "edge", generate subgraph-edge.svg instead: Y keeps every
node, but drops the symlink edge from cwd/ into cwd/sub/par/.

Run: python3 subgraph.py > subgraph.svg
     python3 subgraph.py edge > subgraph-edge.svg
"""
import sys

# floor positions (x, z) of the nodes: cwd/ furthest back, deeper
# directory levels further to the front, as in global-section.py
NODES = {
    "cwd/": (2.4, 3.2),
    "cwd/sub/": (1.4, 1.6),
    "cwd/file1": (3.6, 1.6),
    "cwd/sub/file2": (0.4, 0.0),
    "cwd/sub/par/": (2.2, 0.0),
}
# edges child -> parent; True marks the symlink edge
EDGES = [
    ("cwd/sub/file2", "cwd/sub/", False),
    ("cwd/sub/par/", "cwd/sub/", False),
    ("cwd/", "cwd/sub/par/", True),
    ("cwd/sub/", "cwd/", False),
    ("cwd/file1", "cwd/", False),
]
if sys.argv[1:] == ["edge"]:
    HIDDEN = set()  # nodes of X that are not in Y
    HIDDEN_EDGES = {("cwd/", "cwd/sub/par/")}  # edges of X that are not in Y
    ID = "sge"  # marker id prefix, unique per figure
else:
    HIDDEN = {"cwd/sub/file2"}
    HIDDEN_EDGES = set()
    ID = "sg"
# label offsets (dx, dy, text-anchor) where the default (9, 17, start) would
# collide with an edge
LABELS = {"cwd/": (10, -6, "start"), "cwd/sub/": (-9, -8, "end")}

BOTTOM_Y, TOP_Y = 0.0, 2.6
PLANE = (-0.6, 4.4, -0.8, 3.8)  # x0, x1, z0, z1

BLUE = GREY = FG = "#000"  # black and white only


def proj(x, y, z):
    """Oblique projection: x to the right, y up, z into the screen."""
    return 120 + 130 * x + 30 * z, 600 - 85 * y - 45 * z


def edge_d(a, b, sym, d=9, bend=0.3):
    """SVG path data for the screen edge a->b, shortened by d pixels at both
    ends; the symlink edge (sym) is drawn as an arc bulging to its right."""
    (ax, ay), (bx, by) = a, b
    lx, ly = bx - ax, by - ay
    n = (lx * lx + ly * ly) ** 0.5
    ux, uy = lx / n, ly / n
    if not sym:
        return (f"M{ax + ux * d:.1f},{ay + uy * d:.1f} "
                f"L{bx - ux * d:.1f},{by - uy * d:.1f}")
    # quadratic Bezier with its control point off the chord's midpoint
    cx, cy = (ax + bx) / 2 - uy * bend * n, (ay + by) / 2 + ux * bend * n

    def towards(px, py, qx, qy):
        vx, vy = qx - px, qy - py
        m = (vx * vx + vy * vy) ** 0.5
        return px + vx / m * d, py + vy / m * d

    sx, sy = towards(ax, ay, cx, cy)
    ex, ey = towards(bx, by, cx, cy)
    return f"M{sx:.1f},{sy:.1f} Q{cx:.1f},{cy:.1f} {ex:.1f},{ey:.1f}"


def shorten(a, b, d):
    """Shorten the screen segment a->b by d pixels at both ends."""
    (ax, ay), (bx, by) = a, b
    lx, ly = bx - ax, by - ay
    n = (lx * lx + ly * ly) ** 0.5
    ux, uy = lx / n, ly / n
    return (ax + ux * d, ay + uy * d), (bx - ux * d, by - uy * d)


out = []
w = out.append
w('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 185 830 465" '
  'font-family="sans-serif" font-size="13">')
w('<rect x="0" y="185" width="830" height="465" fill="#fff"/>')
w("<defs>")
for name, col in (("grey", GREY), ("blue", BLUE)):
    w(f'<marker id="{ID}-arr-{name}" viewBox="0 0 10 10" refX="9" refY="5" '
      f'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
      f'<path d="M0,0 L10,5 L0,10 z" fill="{col}"/></marker>')
w("</defs>")


def plane(y, col, label):
    x0, x1, z0, z1 = PLANE
    pts = " ".join(f"{sx:.1f},{sy:.1f}" for sx, sy in (
        proj(x0, y, z0), proj(x1, y, z0), proj(x1, y, z1), proj(x0, y, z1)))
    w(f'<polygon points="{pts}" fill="#fff" '
      f'stroke="{col}"/>')
    lx, ly = proj(x0, y, z1)
    w(f'<text x="{lx + 8:.1f}" y="{ly + 18:.1f}" fill="{col}" '
      f'font-style="italic">{label}</text>')


def graph(y, col, marker, skip, skip_edges=frozenset()):
    for a, b, sym in EDGES:
        if a in skip or b in skip or (a, b) in skip_edges:
            continue
        (ax_, az), (bx_, bz) = NODES[a], NODES[b]
        d = edge_d(proj(ax_, y, az), proj(bx_, y, bz), sym)
        dash = ' stroke-dasharray="5 4"' if sym else ""
        w(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="1.6"'
          f'{dash} marker-end="url(#{ID}-arr-{marker})"/>')
    for name, (x, z) in NODES.items():
        if name in skip:
            continue
        sx, sy = proj(x, y, z)
        w(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="5" fill="{col}"/>')
        dx, dy, anchor = LABELS.get(name, (9, 17, "start"))
        w(f'<text x="{sx + dx:.1f}" y="{sy + dy:.1f}" fill="{col}" '
          f'text-anchor="{anchor}" font-family="monospace">{name}</text>')


# bottom: the whole graph X
plane(BOTTOM_Y, GREY, "X")
graph(BOTTOM_Y, GREY, "grey", set())

# top plane (opaque, so drawn before the dotted arrows)
plane(TOP_Y, BLUE, "Y")

# the inclusion Y >-> X: dotted arrows from each node of Y down to X
for name, (x, z) in NODES.items():
    if name in HIDDEN:
        continue
    p, q = shorten(proj(x, TOP_Y, z), proj(x, BOTTOM_Y, z), 9)
    w(f'<line x1="{p[0]:.1f}" y1="{p[1]:.1f}" x2="{q[0]:.1f}" y2="{q[1]:.1f}" '
      f'stroke="{FG}" stroke-dasharray="2 4" marker-end="url(#{ID}-arr-grey)"/>')

# top: the subgraph Y
graph(TOP_Y, BLUE, "blue", HIDDEN, HIDDEN_EDGES)

w("</svg>")
print("\n".join(out))
