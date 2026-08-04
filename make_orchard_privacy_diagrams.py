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
    width = 1780
    height = 900
    elements = []

    # Additional styling local to this diagram.
    elements.append("""
  <defs>
    <filter id="node-shadow"
            x="-20%" y="-25%" width="140%" height="160%">
      <feDropShadow dx="0"
                    dy="4"
                    stdDeviation="5"
                    flood-color="#172033"
                    flood-opacity="0.10"/>
    </filter>

    <filter id="panel-shadow"
            x="-10%" y="-15%" width="120%" height="140%">
      <feDropShadow dx="0"
                    dy="3"
                    stdDeviation="6"
                    flood-color="#172033"
                    flood-opacity="0.06"/>
    </filter>

    <style>
      .node,
      .cloud {
          filter: url(#node-shadow);
      }

      .tee {
          filter: url(#panel-shadow);
      }

      .continuation-dot {
          fill: #8793a8;
      }
    </style>
  </defs>
""")

    elements.append(
        text(
            width / 2,
            52,
            "Zero-indexer transaction publication",
            "title",
            anchor="middle",
        )
    )

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    wallet_x = 150
    shim_x = 650
    indexer_x = 930

    organization_x = 430
    organization_width = 680
    organization_height = 275

    tee_x = 470
    tee_width = 340
    tee_height = 180

    organizations = [
        {
            "number": 1,
            "boundary_y": 90,
            "tee_y": 130,
            "wallet_ys": (170, 270),
            "shim_y": 220,
            # The upper indexer sends its direct connection through
            # the dedicated lane above the hub.
            "indexer_y": 150,
        },
        {
            "number": 2,
            "boundary_y": 405,
            "tee_y": 450,
            "wallet_ys": (490, 590),
            "shim_y": 540,
            # The lower indexer sends its direct connection through
            # the dedicated lane below the hub.
            "indexer_y": 610,
        },
    ]

    hub_x = 1330
    hub_y = 420
    hub_tee_x = 1180
    hub_tee_y = 270
    hub_tee_width = 300
    hub_tee_height = 300

    mempool_x = 1540
    mempool_y = 320
    mempool_width = 210
    mempool_height = 210

    # ------------------------------------------------------------------
    # Background boundaries
    # ------------------------------------------------------------------

    for organization in organizations:
        elements.append(
            organization_boundary(
                organization_x,
                organization["boundary_y"],
                organization_width,
                organization_height,
                f'organisation {organization["number"]}',
            )
        )

        elements.append(
            tee_boundary(
                tee_x,
                organization["tee_y"],
                tee_width,
                tee_height,
            )
        )

    # The shared hub is also enclosed in a locked TEE.
    elements.append(
        tee_boundary(
            hub_tee_x,
            hub_tee_y,
            hub_tee_width,
            hub_tee_height,
        )
    )

    # ------------------------------------------------------------------
    # Wallet-to-shim TLS connections
    # ------------------------------------------------------------------

    for organization in organizations:
        shim_y = organization["shim_y"]
        wallet_ys = organization["wallet_ys"]
        shim_target_ys = (shim_y - 15, shim_y + 15)

        for wallet_y, target_y in zip(
            wallet_ys,
            shim_target_ys,
        ):
            elements.append(
                edge(
                    f"M 245,{wallet_y} "
                    f"C 335,{wallet_y} "
                    f"405,{target_y} "
                    f"522,{target_y}"
                )
            )

            badge_y = wallet_y + 0.47 * (target_y - wallet_y)
            elements.append(
                tls_badge(
                    365,
                    round(badge_y, 1),
                )
            )

    # ------------------------------------------------------------------
    # Shim-to-local-indexer connections
    # ------------------------------------------------------------------

    # Organization 1: indexer is above and to the right of its shim.
    elements.append(
        edge(
            "M 770,198 "
            "C 795,188 807,166 829,158",
            css_class="edge-local",
            marker="arrow-local",
        )
    )

    # Organization 2: indexer is below and to the right of its shim.
    elements.append(
        edge(
            "M 770,562 "
            "C 795,573 807,599 829,607",
            css_class="edge-local",
            marker="arrow-local",
        )
    )

    # ------------------------------------------------------------------
    # Shim-to-hub connections
    #
    # These approach separate points on the left side of the hub.
    # ------------------------------------------------------------------

    elements.append(
        edge(
            "M 780,220 "
            "C 935,220 1060,255 1145,342 "
            "C 1170,368 1192,387 1218,395",
            css_class="edge-publication",
            marker="arrow-publication",
        )
    )

    elements.append(
        edge(
            "M 780,540 "
            "C 935,540 1060,515 1145,483 "
            "C 1172,473 1193,453 1218,445",
            css_class="edge-publication",
            marker="arrow-publication",
        )
    )

    # ------------------------------------------------------------------
    # Direct indexer-to-mempool connections
    #
    # The first uses an upper routing lane. The second uses a lower
    # routing lane. Both remain outside the hub TEE.
    # ------------------------------------------------------------------

    elements.append(
        edge(
            "M 1035,150 "
            "C 1100,150 1120,82 1210,82 "
            "H 1445 "
            "C 1510,82 1542,275 1609,381",
            css_class="edge",
            marker="arrow",
        )
    )

    elements.append(
        edge(
            "M 1035,610 "
            "C 1100,610 1120,830 1210,830 "
            "H 1445 "
            "C 1510,830 1542,585 1592,490",
            css_class="edge",
            marker="arrow",
        )
    )

    # Hub-to-mempool publication.
    elements.append(
        edge(
            "M 1445,420 "
            "C 1490,420 1525,428 1563,433",
            css_class="edge-publication",
            marker="arrow-publication",
        )
    )

    # ------------------------------------------------------------------
    # Foreground nodes
    # ------------------------------------------------------------------

    for organization in organizations:
        for wallet_y in organization["wallet_ys"]:
            elements.append(
                ellipse_node(
                    wallet_x,
                    wallet_y,
                    95,
                    36,
                    "wallet",
                    "wallet",
                )
            )

        elements.append(
            ellipse_node(
                shim_x,
                organization["shim_y"],
                130,
                44,
                "zero-indexer-shim",
                "shim",
            )
        )

        elements.append(
            ellipse_node(
                indexer_x,
                organization["indexer_y"],
                105,
                40,
                "indexer",
                "indexer",
            )
        )

    elements.append(
        ellipse_node(
            hub_x,
            hub_y,
            115,
            48,
            "zero-indexer-hub",
            "hub",
        )
    )

    elements.append(
        cloud(
            mempool_x,
            mempool_y,
            mempool_width,
            mempool_height,
        )
    )

    # ------------------------------------------------------------------
    # Continuation marks
    #
    # The left column indicates more wallets. The right column indicates
    # more organization/indexer instances without drawing another group.
    # ------------------------------------------------------------------

    for continuation_x in (wallet_x, indexer_x):
        elements.append(
            f"""  <g aria-label="more">
    <circle class="continuation-dot"
            cx="{continuation_x}" cy="735" r="4.5"/>
    <circle class="continuation-dot"
            cx="{continuation_x}" cy="757" r="4.5"/>
    <circle class="continuation-dot"
            cx="{continuation_x}" cy="779" r="4.5"/>
  </g>"""
        )

    # Independent and intentionally disconnected auditor.
    elements.append(
        auditor_eyes(
            1325,
            700,
        )
    )

    return svg_document(
        width,
        height,
        "Zero-indexer transaction publication",
        "Wallet TLS connections terminate at zero-indexer shims inside "
        "trusted execution environments. Shims connect to a shared hub "
        "inside another trusted execution environment. Indexers retain "
        "their direct connections to the mempool.",
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
