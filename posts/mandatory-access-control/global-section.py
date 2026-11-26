"""Generate global-section.svg: the cwd/ graph on the x-z plane, with a stalk
Bool = {⊥, ⊤} above every node and a global section drawn across the stalks.

Run: python3 global-section.py > global-section.svg
"""

# floor positions (x, z) of the nodes: cwd/ furthest back, deeper
# directory levels further to the front
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
# the global section: value chosen at each node
SECTION = {
    "cwd/sub/": True,
    "cwd/sub/file2": False,
    "cwd/sub/par/": True,
    "cwd/": True,
    "cwd/file1": True,
}

# label offsets (dx, dy, text-anchor) where the default (9, 17, start) would
# collide with an edge
LABELS = {"cwd/": (10, -6, "start"), "cwd/sub/": (-9, -8, "end")}

BOT_Y, TOP_Y = 1.7, 2.7
FLOOR = (-0.6, 4.4, -0.8, 3.8)  # x0, x1, z0, z1

BLUE = RED = GREY = FG = "#000"  # black and white only


def proj(x, y, z):
    """Oblique projection: x to the right, y up, z into the screen."""
    return 120 + 130 * x + 30 * z, 430 - 85 * y - 45 * z


def pt(x, y, z):
    sx, sy = proj(x, y, z)
    return f"{sx:.1f},{sy:.1f}"


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
w('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 15 830 455" '
  'font-family="sans-serif" font-size="13">')
w('<rect x="0" y="15" width="830" height="455" fill="#fff"/>')
w("<defs>")
for name, col in (("floor", GREY), ("lift", BLUE)):
    w(f'<marker id="arr-{name}" viewBox="0 0 10 10" refX="9" refY="5" '
      f'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
      f'<path d="M0,0 L10,5 L0,10 z" fill="{col}"/></marker>')
w("</defs>")

# floor plane (the graph X lives here)
x0, x1, z0, z1 = FLOOR
w(f'<polygon points="{pt(x0,0,z0)} {pt(x1,0,z0)} {pt(x1,0,z1)} {pt(x0,0,z1)}" '
  f'fill="#fff" stroke="{GREY}"/>')
lx, ly = proj(x0, 0, z0)  # front corner: the stalks crowd the back one
w(f'<text x="{lx + 30:.1f}" y="{ly - 10:.1f}" text-anchor="start" fill="{FG}" '
  f'font-style="italic">X</text>')

# floor edges
for a, b, sym in EDGES:
    (ax_, az), (bx_, bz) = NODES[a], NODES[b]
    d = edge_d(proj(ax_, 0, az), proj(bx_, 0, bz), sym)
    dash = ' stroke-dasharray="5 4"' if sym else ""
    w(f'<path d="{d}" fill="none" stroke="{GREY}" stroke-width="1.5"{dash} '
      f'marker-end="url(#arr-floor)"/>')

# stalks
for name, (x, z) in NODES.items():
    fx, fy = proj(x, 0, z)
    tx, ty = proj(x, TOP_Y + 0.35, z)
    w(f'<line x1="{fx:.1f}" y1="{fy:.1f}" x2="{tx:.1f}" y2="{ty:.1f}" '
      f'stroke="{GREY}" stroke-dasharray="2 4"/>')

# lifted edges: the global section over each edge
for a, b, sym in EDGES:
    (ax_, az), (bx_, bz) = NODES[a], NODES[b]
    ya = TOP_Y if SECTION[a] else BOT_Y
    yb = TOP_Y if SECTION[b] else BOT_Y
    d = edge_d(proj(ax_, ya, az), proj(bx_, yb, bz), sym)
    dash = ' stroke-dasharray="5 4"' if sym else ""
    w(f'<path d="{d}" fill="none" stroke="{BLUE}" stroke-width="2"{dash} '
      f'marker-end="url(#arr-lift)"/>')

# nodes on the floor and the two points of each stalk
for name, (x, z) in NODES.items():
    fx, fy = proj(x, 0, z)
    w(f'<circle cx="{fx:.1f}" cy="{fy:.1f}" r="5" fill="{GREY}"/>')
    dx, dy, anchor = LABELS.get(name, (9, 17, "start"))
    w(f'<text x="{fx + dx:.1f}" y="{fy + dy:.1f}" fill="{FG}" '
      f'text-anchor="{anchor}" font-family="monospace">{name}</text>')
    for y, val, sym in ((BOT_Y, False, "⊥"), (TOP_Y, True, "⊤")):
        sx, sy = proj(x, y, z)
        chosen = SECTION[name] == val
        col = (BLUE if val else RED) if chosen else GREY
        fill = col if chosen else "none"
        w(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="7" fill="{fill}" '
          f'stroke="{col}" stroke-width="1.5"/>')
        w(f'<text x="{sx - 13:.1f}" y="{sy + 5:.1f}" text-anchor="end" '
          f'fill="{col}" font-size="15">{sym}</text>')

w("</svg>")
print("\n".join(out))
