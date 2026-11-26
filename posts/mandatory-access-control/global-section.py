"""Generate global-section.svg: the cwd/ graph on the x-z plane, with a stalk
Bool = {⊥, ⊤} above every node and a global section drawn across the stalks.

Run: python3 global-section.py > global-section.svg
"""

# floor positions (x, z) of the nodes
NODES = {
    "cwd/sub/": (1.6, 3.2),
    "cwd/sub/file2": (0.0, 2.4),
    "cwd/sub/par/": (1.6, 1.8),
    "cwd/": (3.0, 1.2),
    "cwd/file1": (3.0, -0.2),
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

BOT_Y, TOP_Y = 1.0, 2.0
FLOOR = (-0.6, 4.4, -0.8, 3.8)  # x0, x1, z0, z1

BLUE = RED = GREY = FG = "#000"  # black and white only


def proj(x, y, z):
    """Oblique projection: x to the right, y up, z into the screen."""
    return 120 + 130 * x + 30 * z, 430 - 85 * y - 45 * z


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


out = []
w = out.append
w('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 30 830 440" '
  'font-family="sans-serif" font-size="13">')
w('<rect x="0" y="30" width="830" height="440" fill="#fff"/>')
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
lx, ly = proj(x0, 0, z1)
w(f'<text x="{lx + 8:.1f}" y="{ly + 18:.1f}" text-anchor="start" fill="{FG}" '
  f'font-style="italic">X</text>')

# floor edges
for a, b, sym in EDGES:
    (ax_, az), (bx_, bz) = NODES[a], NODES[b]
    p, q = shorten(proj(ax_, 0, az), proj(bx_, 0, bz), 9)
    dash = ' stroke-dasharray="5 4"' if sym else ""
    w(f'<line x1="{p[0]:.1f}" y1="{p[1]:.1f}" x2="{q[0]:.1f}" y2="{q[1]:.1f}" '
      f'stroke="{GREY}" stroke-width="1.5"{dash} marker-end="url(#arr-floor)"/>')

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
    p, q = shorten(proj(ax_, ya, az), proj(bx_, yb, bz), 9)
    dash = ' stroke-dasharray="5 4"' if sym else ""
    w(f'<line x1="{p[0]:.1f}" y1="{p[1]:.1f}" x2="{q[0]:.1f}" y2="{q[1]:.1f}" '
      f'stroke="{BLUE}" stroke-width="2"{dash} marker-end="url(#arr-lift)"/>')

# nodes on the floor and the two points of each stalk
for name, (x, z) in NODES.items():
    fx, fy = proj(x, 0, z)
    w(f'<circle cx="{fx:.1f}" cy="{fy:.1f}" r="5" fill="{GREY}"/>')
    w(f'<text x="{fx + 9:.1f}" y="{fy + 17:.1f}" fill="{FG}" '
      f'font-family="monospace">{name}</text>')
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
