#!/usr/bin/env pypy3
"""
Generate two SVG diagrams of Zcash transaction publication:

1. Current wallet -> indexer -> mempool publication.
2. Zero-indexer variant with TEE-enclosed shims, a common hub,
   and an auditor represented by watchful eyes.

No third-party packages are required.
"""

from argparse import ArgumentParser
from html import escape
from pathlib import Path


CSS = """
.canvas {
    fill: #fbfcfe;
}

.title {
    fill: #172033;
    font-family: Inter, ui-sans-serif, system-ui, -apple-system,
                 BlinkMacSystemFont, "Segoe UI", sans-serif;
    font-size: 30px;
    font-weight: 700;
}

.node-label {
    fill: #172033;
    font-family: Inter, ui-sans-serif, system-ui, -apple-system,
                 BlinkMacSystemFont, "Segoe UI", sans-serif;
    font-size: 16px;
    font-weight: 650;
    text-anchor: middle;
    dominant-baseline: middle;
}

.small-label {
    fill: #516078;
    font-family: Inter, ui-sans-serif, system-ui, -apple-system,
                 BlinkMacSystemFont, "Segoe UI", sans-serif;
    font-size: 14px;
    font-weight: 600;
}

.boundary-label {
    fill: #667085;
    font-family: Inter, ui-sans-serif, system-ui, -apple-system,
                 BlinkMacSystemFont, "Segoe UI", sans-serif;
    font-size: 14px;
    font-weight: 650;
}

.node {
    stroke-width: 2.2;
    vector-effect: non-scaling-stroke;
}

.wallet {
    fill: #f3efff;
    stroke: #7456c7;
}

.indexer {
    fill: #eaf2ff;
    stroke: #4775bd;
}

.shim {
    fill: #fff1d7;
    stroke: #d88121;
}

.hub {
    fill: #dcf7ec;
    stroke: #218c69;
}

.cloud {
    fill: #eaf4fa;
    stroke: #4c7892;
    stroke-width: 2.4;
    vector-effect: non-scaling-stroke;
}

.edge {
    fill: none;
    stroke: #68758a;
    stroke-width: 2.2;
    stroke-linecap: round;
    stroke-linejoin: round;
    vector-effect: non-scaling-stroke;
}

.edge-local {
    fill: none;
    stroke: #8a94a6;
    stroke-width: 2;
    stroke-linecap: round;
    stroke-linejoin: round;
    vector-effect: non-scaling-stroke;
}

.edge-publication {
    fill: none;
    stroke: #218c69;
    stroke-width: 3;
    stroke-linecap: round;
    stroke-linejoin: round;
    vector-effect: non-scaling-stroke;
}

.organization {
    fill: #f7f9fc;
    fill-opacity: 0.72;
    stroke: #a9b2c2;
    stroke-width: 1.8;
    stroke-dasharray: 8 6;
    vector-effect: non-scaling-stroke;
}

.tee {
    fill: #ebfaf4;
    fill-opacity: 0.9;
    stroke: #218c69;
    stroke-width: 2.5;
    vector-effect: non-scaling-stroke;
}

.tls-badge {
    fill: #ffffff;
    stroke: #7456c7;
    stroke-width: 1.5;
    vector-effect: non-scaling-stroke;
}

.tls-text {
    fill: #5e43aa;
    font-family: Inter, ui-sans-serif, system-ui, -apple-system,
                 BlinkMacSystemFont, "Segoe UI", sans-serif;
    font-size: 12px;
    font-weight: 750;
    text-anchor: middle;
    dominant-baseline: middle;
}

.lock {
    fill: none;
    stroke: #218c69;
    stroke-width: 2;
    stroke-linecap: round;
    stroke-linejoin: round;
    vector-effect: non-scaling-stroke;
}

.auditor-label {
    fill: #5f4b13;
    font-family: Inter, ui-sans-serif, system-ui, -apple-system,
                 BlinkMacSystemFont, "Segoe UI", sans-serif;
    font-size: 16px;
    font-weight: 700;
    text-anchor: middle;
}

.eye {
    fill: #ffffff;
    stroke: #b38a25;
    stroke-width: 2.2;
    vector-effect: non-scaling-stroke;
}

.pupil {
    fill: #29303d;
}

.highlight {
    fill: #ffffff;
}
"""


def svg_document(width, height, title, description, elements):
    """Return a complete SVG document."""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     width="{width}"
     height="{height}"
     viewBox="0 0 {width} {height}"
     role="img"
     aria-labelledby="svg-title svg-desc">
  <title id="svg-title">{escape(title)}</title>
  <desc id="svg-desc">{escape(description)}</desc>

  <defs>
    <style>
{CSS}
    </style>

    <marker id="arrow"
            viewBox="0 0 10 10"
            refX="9"
            refY="5"
            markerWidth="7"
            markerHeight="7"
            orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#68758a"/>
    </marker>

    <marker id="arrow-local"
            viewBox="0 0 10 10"
            refX="9"
            refY="5"
            markerWidth="7"
            markerHeight="7"
            orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#8a94a6"/>
    </marker>

    <marker id="arrow-publication"
            viewBox="0 0 10 10"
            refX="9"
            refY="5"
            markerWidth="7"
            markerHeight="7"
            orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#218c69"/>
    </marker>
  </defs>

  <rect class="canvas" x="0" y="0" width="{width}" height="{height}"/>

{chr(10).join(elements)}
</svg>
"""


def text(x, y, value, css_class, anchor=None):
    anchor_attr = f' text-anchor="{anchor}"' if anchor else ""
    return (
        f'  <text x="{x}" y="{y}" class="{css_class}"'
        f'{anchor_attr}>{escape(value)}</text>'
    )


def ellipse_node(cx, cy, rx, ry, label, node_class):
    return f"""  <g>
    <ellipse class="node {node_class}"
             cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}"/>
    <text class="node-label" x="{cx}" y="{cy}">{escape(label)}</text>
  </g>"""


def cloud_path(x, y, width, height):
    """Create a rounded cloud path inside the supplied bounding box."""
    p = lambda fx, fy: (x + width * fx, y + height * fy)

    points = {
        "start": p(0.25, 0.82),
        "a1": p(0.07, 0.82),
        "a2": p(0.02, 0.68),
        "a3": p(0.11, 0.54),
        "b1": p(0.04, 0.37),
        "b2": p(0.18, 0.23),
        "b3": p(0.33, 0.29),
        "c1": p(0.39, 0.08),
        "c2": p(0.64, 0.07),
        "c3": p(0.72, 0.28),
        "d1": p(0.90, 0.24),
        "d2": p(0.98, 0.40),
        "d3": p(0.91, 0.55),
        "e1": p(1.02, 0.69),
        "e2": p(0.89, 0.83),
        "e3": p(0.75, 0.81),
    }

    def xy(name):
        px, py = points[name]
        return f"{px:.1f},{py:.1f}"

    return (
        f"M {xy('start')} "
        f"C {xy('a1')} {xy('a2')} {xy('a3')} "
        f"C {xy('b1')} {xy('b2')} {xy('b3')} "
        f"C {xy('c1')} {xy('c2')} {xy('c3')} "
        f"C {xy('d1')} {xy('d2')} {xy('d3')} "
        f"C {xy('e1')} {xy('e2')} {xy('e3')} "
        f"L {xy('start')} Z"
    )


def cloud(x, y, width, height, label="mempool"):
    label_x = x + width * 0.52
    label_y = y + height * 0.56
    return f"""  <g>
    <path class="cloud" d="{cloud_path(x, y, width, height)}"/>
    <text class="node-label"
          x="{label_x:.1f}" y="{label_y:.1f}">{escape(label)}</text>
  </g>"""


def edge(path_d, css_class="edge", marker="arrow"):
    return (
        f'  <path class="{css_class}" d="{path_d}" '
        f'marker-end="url(#{marker})"/>'
    )


def tls_badge(cx, cy):
    """Draw a compact lock-and-TLS badge."""
    return f"""  <g transform="translate({cx} {cy})">
    <rect class="tls-badge" x="-34" y="-13" width="68" height="26" rx="13"/>
    <path d="M -21,-2 V -6
             C -21,-12 -11,-12 -11,-6
             V -2"
          fill="none"
          stroke="#7456c7"
          stroke-width="1.5"
          stroke-linecap="round"/>
    <rect x="-22.5" y="-3"
          width="13" height="10"
          rx="2"
          fill="#7456c7"/>
    <text class="tls-text" x="11" y="1">TLS</text>
  </g>"""


def organization_boundary(x, y, width, height, label):
    return f"""  <g>
    <rect class="organization"
          x="{x}" y="{y}" width="{width}" height="{height}" rx="22"/>
    <text class="boundary-label"
          x="{x + 18}" y="{y + 25}">{escape(label)}</text>
  </g>"""


def tee_boundary(x, y, width, height):
    """Draw a TEE boundary with a small lock symbol."""
    return f"""  <g>
    <rect class="tee"
          x="{x}" y="{y}" width="{width}" height="{height}" rx="18"/>

    <path class="lock"
          d="M {x + 20},{y + 28}
             V {y + 21}
             C {x + 20},{y + 10}
               {x + 36},{y + 10}
               {x + 36},{y + 21}
             V {y + 28}"/>

    <rect x="{x + 17}" y="{y + 27}"
          width="22" height="17" rx="3"
          fill="#218c69"/>

    <circle cx="{x + 28}" cy="{y + 35}"
            r="2.3" fill="#ffffff"/>

    <text class="small-label"
          x="{x + 49}" y="{y + 34}">TEE</text>
  </g>"""


def auditor_eyes(cx, cy):
    """Draw a vector version of the conventional watching-eyes symbol."""
    return f"""  <g>
    <ellipse class="eye"
             cx="{cx - 29}" cy="{cy}"
             rx="26" ry="38"
             transform="rotate(-5 {cx - 29} {cy})"/>

    <ellipse class="eye"
             cx="{cx + 29}" cy="{cy}"
             rx="26" ry="38"
             transform="rotate(5 {cx + 29} {cy})"/>

    <circle class="pupil" cx="{cx - 21}" cy="{cy + 3}" r="10"/>
    <circle class="pupil" cx="{cx + 37}" cy="{cy + 3}" r="10"/>

    <circle class="highlight" cx="{cx - 17}" cy="{cy - 1}" r="3"/>
    <circle class="highlight" cx="{cx + 41}" cy="{cy - 1}" r="3"/>

    <text class="auditor-label"
          x="{cx}" y="{cy + 67}">zero-indexer-auditor</text>
  </g>"""


def make_current_diagram():
    width = 1400
    height = 820
    elements = []

    elements.append(
        text(
            width / 2,
            52,
            "Current Zcash transaction publication",
            "title",
            anchor="middle",
        )
    )

    indexer_rows = [210, 410, 610]
    wallet_x = 170
    indexer_x = 700

    # Wallet-to-indexer TLS connections.
    for index, indexer_y in enumerate(indexer_rows, start=1):
        wallet_ys = [indexer_y - 45, indexer_y + 45]
        target_ys = [indexer_y - 13, indexer_y + 13]

        for wallet_y, target_y in zip(wallet_ys, target_ys):
            path = (
                f"M 260,{wallet_y} "
                f"C 385,{wallet_y} 470,{target_y} 580,{target_y}"
            )
            elements.append(edge(path))

            badge_x = 410
            badge_y = wallet_y + (target_y - wallet_y) * 0.55
            elements.append(tls_badge(badge_x, round(badge_y, 1)))

    # Indexer-to-mempool publication connections.
    cloud_targets = [(1128, 347), (1115, 411), (1128, 477)]

    for indexer_y, (target_x, target_y) in zip(
        indexer_rows, cloud_targets
    ):
        path = (
            f"M 810,{indexer_y} "
            f"C 930,{indexer_y} 1010,{target_y} "
            f"{target_x},{target_y}"
        )
        elements.append(edge(path))

    # Nodes are drawn above the connections.
    for index, indexer_y in enumerate(indexer_rows, start=1):
        wallet_ys = [indexer_y - 45, indexer_y + 45]

        for wallet_y in wallet_ys:
            elements.append(
                ellipse_node(
                    wallet_x,
                    wallet_y,
                    90,
                    35,
                    "wallet",
                    "wallet",
                )
            )

        elements.append(
            ellipse_node(
                indexer_x,
                indexer_y,
                110,
                43,
                f"indexer {index}",
                "indexer",
            )
        )

    elements.append(cloud(1100, 280, 260, 260))

    return svg_document(
        width,
        height,
        "Current Zcash transaction publication",
        "Multiple wallets connect over TLS to three indexers, "
        "which publish transactions to the mempool.",
        elements,
    )


def make_zero_indexer_diagram():
    width = 1760
    height = 980
    elements = []

    elements.append(
        text(
            width / 2,
            52,
            "Zero-indexer transaction publication",
            "title",
            anchor="middle",
        )
    )

    rows = [180, 450, 720]

    wallet_x = 160
    shim_x = 620
    indexer_x = 920

    organization_x = 350
    organization_width = 760
    organization_height = 240

    shim_tee_x = 450
    shim_tee_width = 320
    shim_tee_height = 156

    hub_x = 1355
    hub_y = 450

    hub_tee_x = 1200
    hub_tee_y = 350
    hub_tee_width = 300
    hub_tee_height = 200

    # Organizational boundaries and shim TEE enclaves.
    for number, row_y in enumerate(rows, start=1):
        elements.append(
            organization_boundary(
                organization_x,
                row_y - 120,
                organization_width,
                organization_height,
                f"organization {number}",
            )
        )

        elements.append(
            tee_boundary(
                shim_tee_x,
                row_y - shim_tee_height / 2,
                shim_tee_width,
                shim_tee_height,
            )
        )

    # Locked TEE enclave containing the shared hub.
    elements.append(
        tee_boundary(
            hub_tee_x,
            hub_tee_y,
            hub_tee_width,
            hub_tee_height,
        )
    )

    # Wallet-to-shim TLS connections. Each TLS endpoint is inside a TEE.
    for row_y in rows:
        wallet_ys = [row_y - 45, row_y + 45]
        target_ys = [row_y - 11, row_y + 11]

        for wallet_y, target_y in zip(wallet_ys, target_ys):
            path = (
                f"M 248,{wallet_y} "
                f"C 335,{wallet_y} 405,{target_y} 492,{target_y}"
            )
            elements.append(edge(path))

            badge_x = 350
            badge_y = wallet_y + (target_y - wallet_y) * 0.58
            elements.append(tls_badge(badge_x, round(badge_y, 1)))

    # Shim-to-local-indexer connections.
    for row_y in rows:
        path = (
            f"M 742,{row_y + 12} "
            f"C 790,{row_y + 15} "
            f"805,{row_y + 46} "
            f"806,{row_y + 51}"
        )
        elements.append(
            edge(
                path,
                css_class="edge-local",
                marker="arrow-local",
            )
        )

    # Preserve the direct indexer-to-mempool publication paths.
    # These are routed around the hub's TEE boundary.
    direct_indexer_paths = [
        (
            "M 1025,235 "
            "C 1190,235 1380,285 1510,330 "
            "L 1572,404"
        ),
        (
            "M 1025,505 "
            "C 1100,505 1125,610 1200,625 "
            "H 1440 "
            "C 1500,625 1515,520 1548,465"
        ),
        (
            "M 1025,775 "
            "C 1220,775 1410,665 1510,570 "
            "L 1550,512"
        ),
    ]

    for path in direct_indexer_paths:
        elements.append(
            edge(
                path,
                css_class="edge",
                marker="arrow",
            )
        )

    # Every shim also connects to the single hub inside its TEE.
    shim_to_hub_paths = [
        (
            f"M 742,{rows[0] - 10} "
            f"H 1080 "
            f"C 1165,{rows[0] - 10} 1175,405 1236,425"
        ),
        (
            f"M 742,{rows[1] - 10} "
            f"H 1080 "
            f"C 1150,{rows[1] - 10} 1190,450 1235,450"
        ),
        (
            f"M 742,{rows[2] - 10} "
            f"H 1080 "
            f"C 1165,{rows[2] - 10} 1175,495 1236,475"
        ),
    ]

    for path in shim_to_hub_paths:
        elements.append(
            edge(
                path,
                css_class="edge-publication",
                marker="arrow-publication",
            )
        )

    # Hub-to-mempool publication path exits the hub's TEE.
    elements.append(
        edge(
            "M 1465,450 C 1500,450 1518,450 1542,450",
            css_class="edge-publication",
            marker="arrow-publication",
        )
    )

    # Wallets, shims, and local indexers.
    for row_y in rows:
        for wallet_y in (row_y - 45, row_y + 45):
            elements.append(
                ellipse_node(
                    wallet_x,
                    wallet_y,
                    88,
                    34,
                    "wallet",
                    "wallet",
                )
            )

        elements.append(
            ellipse_node(
                shim_x,
                row_y,
                125,
                42,
                "zero-indexer-shim",
                "shim",
            )
        )

        elements.append(
            ellipse_node(
                indexer_x,
                row_y + 55,
                105,
                40,
                "indexer",
                "indexer",
            )
        )

    # Shared hub, enclosed by the hub TEE drawn earlier.
    elements.append(
        ellipse_node(
            hub_x,
            hub_y,
            110,
            48,
            "zero-indexer-hub",
            "hub",
        )
    )

    elements.append(cloud(1530, 350, 205, 200))

    # Independent, disconnected auditor.
    elements.append(auditor_eyes(1355, 755))

    return svg_document(
        width,
        height,
        "Zero-indexer transaction publication",
        "Wallet TLS connections terminate at zero-indexer shims inside "
        "trusted execution environments. The shims connect to a hub in "
        "another trusted execution environment. Both the hub and the "
        "indexers publish to the mempool.",
        elements,
    )


def main():
    parser = ArgumentParser(
        description="Generate Zcash transaction-publication SVG diagrams."
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=Path("."),
        help="Directory in which to write the SVG files.",
    )
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    current_path = args.output_dir / "zcash_current_publication.svg"
    zero_indexer_path = (
        args.output_dir / "zcash_zero_indexer_publication.svg"
    )

    current_path.write_text(
        make_current_diagram(),
        encoding="utf-8",
    )
    zero_indexer_path.write_text(
        make_zero_indexer_diagram(),
        encoding="utf-8",
    )

    print(f"Wrote {current_path}")
    print(f"Wrote {zero_indexer_path}")


if __name__ == "__main__":
    main()
