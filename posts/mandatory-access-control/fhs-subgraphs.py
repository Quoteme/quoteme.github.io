"""Generate fhs-httpd.svg and fhs-mysqld.svg: a small part of the FHS as the
graph X on a bottom plane, and on a top plane the subgraph that the Apache
(httpd_t) resp. MariaDB (mysqld_t) process has access to, with dotted arrows
from every node of the subgraph down to the node of X it corresponds to.

Run: python3 fhs-subgraphs.py   (writes both SVG files next to this script)
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
}

BOTTOM_Y, TOP_Y = 0.0, 2.8
PLANE = (-0.6, 5.6, -1.2, 4.0)  # x0, x1, z0, z1
INK = "#000"  # black and white only


def proj(x, y, z):
    """Oblique projection: x to the right, y up, z into the screen."""
    return 110 + 95 * x + 28 * z, 560 - 80 * y - 40 * z


def shorten(a, b, d):
    """Shorten the screen segment a->b by d pixels at both ends."""
    (ax, ay), (bx, by) = a, b
    lx, ly = bx - ax, by - ay
    n = (lx * lx + ly * ly) ** 0.5
    ux, uy = lx / n, ly / n
    return (ax + ux * d, ay + uy * d), (bx - ux * d, by - uy * d)


def render(label, keep):
    out = []
    w = out.append
    w('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 160 770 460" '
      'font-family="sans-serif" font-size="13">')
    w('<rect x="0" y="160" width="770" height="460" fill="#fff"/>')
    w('<defs><marker id="fhs-arr" viewBox="0 0 10 10" refX="9" refY="5" '
      'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
      f'<path d="M0,0 L10,5 L0,10 z" fill="{INK}"/></marker></defs>')

    def plane(y, name):
        x0, x1, z0, z1 = PLANE
        pts = " ".join(f"{sx:.1f},{sy:.1f}" for sx, sy in (
            proj(x0, y, z0), proj(x1, y, z0), proj(x1, y, z1), proj(x0, y, z1)))
        w(f'<polygon points="{pts}" fill="#fff" stroke="{INK}"/>')
        lx, ly = proj(x0, y, z1)
        w(f'<text x="{lx + 8:.1f}" y="{ly + 18:.1f}" fill="{INK}" '
          f'font-style="italic">{name}</text>')

    def graph(y, nodes):
        for a, b in EDGES:
            if a not in nodes or b not in nodes:
                continue
            (ax, az), (bx, bz) = NODES[a], NODES[b]
            p, q = shorten(proj(ax, y, az), proj(bx, y, bz), 8)
            w(f'<line x1="{p[0]:.1f}" y1="{p[1]:.1f}" x2="{q[0]:.1f}" '
              f'y2="{q[1]:.1f}" stroke="{INK}" stroke-width="1.5" '
              f'marker-end="url(#fhs-arr)"/>')
        for name in nodes:
            x, z = NODES[name]
            sx, sy = proj(x, y, z)
            w(f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="4.5" fill="{INK}"/>')
            left = name in LEFT_LABELS
            tx = sx - 8 if left else sx + 8
            anchor = ' text-anchor="end"' if left else ""
            ty = sy - 9 if name == "/" else sy + 4 if left else sy + 15
            w(f'<text x="{tx:.1f}" y="{ty:.1f}" fill="{INK}"{anchor} '
              f'font-family="monospace" font-size="12">{name}</text>')

    plane(BOTTOM_Y, "FHS")
    graph(BOTTOM_Y, list(NODES))
    plane(TOP_Y, label)
    for name in keep:
        x, z = NODES[name]
        p, q = shorten(proj(x, TOP_Y, z), proj(x, BOTTOM_Y, z), 8)
        w(f'<line x1="{p[0]:.1f}" y1="{p[1]:.1f}" x2="{q[0]:.1f}" '
          f'y2="{q[1]:.1f}" stroke="{INK}" stroke-dasharray="2 4" '
          f'marker-end="url(#fhs-arr)"/>')
    graph(TOP_Y, [n for n in NODES if n in keep])
    w("</svg>")
    return "\n".join(out) + "\n"


here = Path(__file__).parent
for filename, (label, keep) in SUBGRAPHS.items():
    (here / filename).write_text(render(f"Y<tspan font-size='10' dy='4'>{label}</tspan>", keep))
