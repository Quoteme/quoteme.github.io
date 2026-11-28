"""Generate fhs-httpd.svg, fhs-mysqld.svg and fhs-both.svg: a small part of the FHS as a
flat graph, with the subgraph that the Apache (httpd_t) resp. MariaDB
(mysqld_t) process, or both of them, have access to drawn in black and the
rest in grey.

Run: python3 fhs-subgraphs.py   (writes all three SVG files next to this script)
"""

from pathlib import Path

# floor positions (x, z) of the nodes
NODES = {
    "/": (2.8, 3.4),
    "/var/": (1.5, 2.4),
    "/etc/": (2.8, 2.4),
    "/data/": (4.1, 2.4),
    "/var/www/": (1.5, 1.4),
    "/var/www/html/": (1.5, 0.4),
    "/var/www/html/index.html": (1.5, -0.6),
    "/data/mysql/": (4.1, 1.4),
    "/data/mysql/ibdata1": (4.1, 0.4),
}
# nodes whose label is placed to the left of the node
LEFT_LABELS = {"/var/", "/var/www/", "/var/www/html/", "/var/www/html/index.html"}
# edges child -> parent
EDGES = [
    ("/var/", "/"),
    ("/etc/", "/"),
    ("/data/", "/"),
    ("/var/www/", "/var/"),
    ("/var/www/html/", "/var/www/"),
    ("/var/www/html/index.html", "/var/www/html/"),
    ("/data/mysql/", "/data/"),
    ("/data/mysql/ibdata1", "/data/mysql/"),
]
# nodes each process has access to
SUBGRAPHS = {
    "fhs-httpd.svg": ("httpd_t", {
        "/", "/var/", "/var/www/", "/var/www/html/", "/var/www/html/index.html",
    }),
    "fhs-mysqld.svg": ("mysqld_t", {
        "/", "/data/", "/data/mysql/", "/data/mysql/ibdata1",
    }),
    # the intersection of both subgraphs
    "fhs-both.svg": ("httpd_t and mysqld_t", {"/"}),
}

INK = "#000"
GREY = "#bbb"
SX, SY = 110, 80  # screen units per floor unit


def proj(x, z):
    """Flat layout: x to the right, z up."""
    return 30 + SX * x, 30 + SY * (3.4 - z)


def shorten(a, b, d):
    """Shorten the screen segment a->b by d pixels at both ends."""
    (ax, ay), (bx, by) = a, b
    lx, ly = bx - ax, by - ay
    n = (lx * lx + ly * ly) ** 0.5
    ux, uy = lx / n, ly / n
    return (ax + ux * d, ay + uy * d), (bx - ux * d, by - uy * d)


def render(keep):
    """The FHS as a flat graph: nodes and arcs of the subgraph in black, the
    rest in grey."""
    out = []
    w = out.append
    xs = [proj(x, z)[0] for x, z in NODES.values()]
    ys = [proj(x, z)[1] for x, z in NODES.values()]
    x0, x1 = min(xs) - 200, max(xs) + 160
    y0, y1 = min(ys) - 25, max(ys) + 25
    w(f'<svg xmlns="http://www.w3.org/2000/svg" '
      f'viewBox="{x0:.0f} {y0:.0f} {x1 - x0:.0f} {y1 - y0:.0f}" '
      'font-family="sans-serif" font-size="13">')
    w(f'<rect x="{x0:.0f}" y="{y0:.0f}" width="{x1 - x0:.0f}" '
      f'height="{y1 - y0:.0f}" fill="#fff"/>')
    w("<defs>")
    for mid, col in (("fhs-arr", INK), ("fhs-arr-grey", GREY)):
        w(f'<marker id="{mid}" viewBox="0 0 10 10" refX="9" refY="5" '
          'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
          f'<path d="M0,0 L10,5 L0,10 z" fill="{col}"/></marker>')
    w("</defs>")
    for a, b in EDGES:
        inside = a in keep and b in keep
        col, mid = (INK, "fhs-arr") if inside else (GREY, "fhs-arr-grey")
        dash = "" if inside else ' stroke-dasharray="5 4"'
        p, q = shorten(proj(*NODES[a]), proj(*NODES[b]), 8)
        w(f'<line x1="{p[0]:.1f}" y1="{p[1]:.1f}" x2="{q[0]:.1f}" '
          f'y2="{q[1]:.1f}" stroke="{col}" stroke-width="1.5"{dash} '
          f'marker-end="url(#{mid})"/>')
    for name, (x, z) in NODES.items():
        col = INK if name in keep else GREY
        sx, sy = proj(x, z)
        w(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="4.5" fill="{col}"/>')
        left = name in LEFT_LABELS
        tx = sx - 9 if left else sx + 9
        anchor = ' text-anchor="end"' if left else ""
        ty = sy - 10 if name == "/" else sy + 4
        if name == "/":
            tx, anchor = sx, ' text-anchor="middle"'
        w(f'<text x="{tx:.1f}" y="{ty:.1f}" fill="{col}"{anchor} '
          f'font-family="monospace" font-size="12">{name}</text>')
    w("</svg>")
    return "\n".join(out) + "\n"


here = Path(__file__).parent
for filename, (label, keep) in SUBGRAPHS.items():
    (here / filename).write_text(render(keep))
