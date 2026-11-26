"""Generate subgraph.svg: the cwd/ graph X on a bottom plane, the subgraph Y
without cwd/sub/file2 on a top plane, and dotted arrows from every node of Y
down to the node of X it corresponds to.

Run: python3 subgraph.py > subgraph.svg
"""

# floor positions (x, z) of the nodes, as in global-section.py
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
HIDDEN = {"cwd/sub/file2"}  # nodes of X that are not in Y
LEFT_LABELS = {"cwd/sub/par/"}  # labels placed left of their node

BOTTOM_Y, TOP_Y = 0.0, 2.6
PLANE = (-0.6, 4.4, -0.8, 3.8)  # x0, x1, z0, z1

BLUE = GREY = FG = "#000"  # black and white only


def proj(x, y, z):
    """Oblique projection: x to the right, y up, z into the screen."""
    return 120 + 130 * x + 30 * z, 600 - 85 * y - 45 * z


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
    w(f'<marker id="sg-arr-{name}" viewBox="0 0 10 10" refX="9" refY="5" '
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


def graph(y, col, marker, skip):
    for a, b, sym in EDGES:
        if a in skip or b in skip:
            continue
        (ax_, az), (bx_, bz) = NODES[a], NODES[b]
        p, q = shorten(proj(ax_, y, az), proj(bx_, y, bz), 9)
        dash = ' stroke-dasharray="5 4"' if sym else ""
        w(f'<line x1="{p[0]:.1f}" y1="{p[1]:.1f}" x2="{q[0]:.1f}" '
          f'y2="{q[1]:.1f}" stroke="{col}" stroke-width="1.6"{dash} '
          f'marker-end="url(#sg-arr-{marker})"/>')
    for name, (x, z) in NODES.items():
        if name in skip:
            continue
        sx, sy = proj(x, y, z)
        w(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="5" fill="{col}"/>')
        left = name in LEFT_LABELS
        tx = sx - 9 if left else sx + 9
        anchor = ' text-anchor="end"' if left else ""
        w(f'<text x="{tx:.1f}" y="{sy + 17:.1f}" fill="{col}"{anchor} '
          f'font-family="monospace">{name}</text>')


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
      f'stroke="{FG}" stroke-dasharray="2 4" marker-end="url(#sg-arr-grey)"/>')

# top: the subgraph Y
graph(TOP_Y, BLUE, "blue", HIDDEN)

w("</svg>")
print("\n".join(out))
