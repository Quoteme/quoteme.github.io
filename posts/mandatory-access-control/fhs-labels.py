"""Generate fhs-labels.svg: the FHS graph of the Apache/MariaDB example, where
every node carries the bits that serialize the characteristic maps of httpd_t
and mysqld_t: one "include" bit per process, and for every entry of a
directory one "out" bit per process.

Run: python3 fhs-labels.py > fhs-labels.svg
"""

from html import escape

# node -> (column, entry name) ; parent given by EDGES
COLUMN = {
    "/": 1,
    "/var/": 0, "/var/www/": 0, "/var/www/html/": 0,
    "/var/www/html/index.html": 0,
    "/etc/": 1,
    "/data/": 2, "/data/mysql/": 2, "/data/mysql/ibdata1": 2,
}
# edges child -> parent, in display order
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
ACCESS = {
    "httpd": {"/", "/var/", "/var/www/", "/var/www/html/",
              "/var/www/html/index.html"},
    "mysqld": {"/", "/data/", "/data/mysql/", "/data/mysql/ibdata1"},
}


def entry(path):
    """The name of a file or directory inside its parent, e.g. 'www'."""
    return path.rstrip("/").rsplit("/", 1)[-1]


def lines(node):
    out = [f"{p}_include: {str(node in nodes).lower()}"
           for p, nodes in ACCESS.items()]
    children = [c for c, parent in EDGES if parent == node]
    for p, nodes in ACCESS.items():
        for c in children:
            # an arc is visible iff both of its endpoints are
            visible = c in nodes and node in nodes
            out.append(f"{p}_out_{entry(c)}: {str(visible).lower()}")
    return out


LINE_H, PAD, CHAR_W = 16, 8, 7.3
COL_X = [20, 300, 580]
BOX_W = 260
GAP = 46

# layout: root on top of the middle column, then the columns below it
boxes = {}
root_lines = lines("/")
root_h = PAD * 2 + LINE_H * (len(root_lines) + 1)
boxes["/"] = (COL_X[1], 10, root_h)
cursor = [10 + root_h + GAP] * 3
for child, _ in EDGES:
    col = COLUMN[child]
    h = PAD * 2 + LINE_H * (len(lines(child)) + 1)
    boxes[child] = (COL_X[col], cursor[col], h)
    cursor[col] += h + GAP

W = COL_X[2] + BOX_W + 20
H = max(cursor) - GAP + 10

out = []
w = out.append
w(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
  'font-family="monospace" font-size="12.5">')
w(f'<rect width="{W}" height="{H}" fill="#fff"/>')
w('<defs><marker id="lab-arr" viewBox="0 0 10 10" refX="9" refY="5" '
  'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
  '<path d="M0,0 L10,5 L0,10 z" fill="#000"/></marker></defs>')

# arcs child -> parent: from the top of the child to the bottom of the parent
for child, parent in EDGES:
    cx, cy, _ = boxes[child]
    px, py, ph = boxes[parent]
    x1, y1 = cx + BOX_W / 2, cy
    x2, y2 = px + BOX_W / 2, py + ph
    if parent == "/":
        x2 += {0: -70, 1: 0, 2: 70}[COLUMN[child]]
    w(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2 + 2}" stroke="#000" '
      'stroke-width="1.4" marker-end="url(#lab-arr)"/>')

for node, (x, y, h) in boxes.items():
    w(f'<rect x="{x}" y="{y}" width="{BOX_W}" height="{h}" fill="#fff" '
      'stroke="#000"/>')
    w(f'<text x="{x + PAD}" y="{y + PAD + 12}" font-weight="bold">'
      f'{escape(node)}</text>')
    for i, line in enumerate(lines(node), start=1):
        w(f'<text x="{x + PAD}" y="{y + PAD + 12 + i * LINE_H}">'
          f'{escape(line)}</text>')

w("</svg>")
print("\n".join(out))
