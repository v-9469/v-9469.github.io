#!/usr/bin/env python3
"""
Generates the animated, monochrome 3D SVG assets used by README.md.

Everything is plain SVG + SMIL (no JavaScript), so it renders on GitHub.
Run:  python3 scripts/gen_assets.py
"""
import math
import os
import random
from xml.sax.saxutils import escape

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
os.makedirs(OUT, exist_ok=True)

MONO = "'SF Mono','JetBrains Mono','Menlo','Consolas','DejaVu Sans Mono',monospace"
SANS = "'Helvetica Neue',Helvetica,Arial,sans-serif"
BG = "#050505"
INK = "#f4f4f4"
MUTE = "#8a8a8a"
DIM = "#4a4a4a"
HAIR = "#2b2b2b"

S3 = math.sqrt(3) / 2


def write(name, svg):
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"  {name:28s} {os.path.getsize(path) / 1024:7.1f} KB")


# --------------------------------------------------------------------------
# 1. Rotating wireframe torus (true 3D: projected on every keyframe)
# --------------------------------------------------------------------------
def torus_paths(cx, cy, sc, rings=24, pts=48, frames=18, R=1.0, r=0.40,
                tilt=math.radians(58), dur=26):
    out = []
    for k in range(rings):
        th = 2 * math.pi * k / rings
        vals = []
        for f in range(frames + 1):
            a = math.pi * f / frames  # torus is symmetric after pi => seamless loop
            coords = []
            for j in range(pts):
                ph = 2 * math.pi * j / pts
                rad = R + r * math.cos(th)
                x = rad * math.cos(ph)
                y = rad * math.sin(ph)
                z = r * math.sin(th)
                x2 = x * math.cos(a) + z * math.sin(a)
                z2 = -x * math.sin(a) + z * math.cos(a)
                y3 = y * math.cos(tilt) - z2 * math.sin(tilt)
                z3 = y * math.sin(tilt) + z2 * math.cos(tilt)
                s = 1 / (1 - z3 / 6.0)
                coords.append((cx + x2 * s * sc, cy + y3 * s * sc))
            vals.append("M" + " L".join(f"{px:.1f},{py:.1f}" for px, py in coords) + "Z")
        op = 0.28 + 0.62 * (0.5 + 0.5 * math.cos(th))
        out.append(
            f'<path d="{vals[0]}" fill="none" stroke="{INK}" stroke-width="0.7" '
            f'stroke-opacity="{op:.2f}" stroke-linejoin="round">'
            f'<animate attributeName="d" dur="{dur}s" repeatCount="indefinite" '
            f'values="{";".join(vals)}"/></path>'
        )
    return "\n".join(out)


def burst(cx, cy, r0, r1, n=84, seed=7, dur=50):
    rnd = random.Random(seed)
    lines = []
    for i in range(n):
        a = 2 * math.pi * i / n
        rr = r0 + (r1 - r0) * (0.35 + 0.65 * rnd.random())
        lines.append(
            f'<line x1="{cx + r0 * math.cos(a):.1f}" y1="{cy + r0 * math.sin(a):.1f}" '
            f'x2="{cx + rr * math.cos(a):.1f}" y2="{cy + rr * math.sin(a):.1f}" '
            f'stroke="{INK}" stroke-width="0.8" stroke-opacity="{0.4 + 0.5 * rnd.random():.2f}"/>'
        )
    return (f'<g>{"".join(lines)}'
            f'<animateTransform attributeName="transform" type="rotate" '
            f'from="0 {cx} {cy}" to="360 {cx} {cy}" dur="{dur}s" repeatCount="indefinite"/></g>')


def rail_text(x, y, text, size=9, fill=MUTE, spacing=2):
    return (f'<text transform="translate({x} {y}) rotate(-90)" font-family="{MONO}" '
            f'font-size="{size}" letter-spacing="{spacing}" fill="{fill}">{escape(text)}</text>')


def role_cycle(x, y, roles, size=15, period=9):
    n = len(roles)
    out = []
    for i, role in enumerate(roles):
        t0, t1 = i / n, (i + 1) / n
        if i == 0:
            vals, keys = "1;0", f"0;{t1:.4f}"
        elif i == n - 1:
            vals, keys = "0;1", f"0;{t0:.4f}"
        else:
            vals, keys = "0;1;0", f"0;{t0:.4f};{t1:.4f}"
        init = "1" if i == 0 else "0"
        out.append(
            f'<text x="{x}" y="{y}" font-family="{MONO}" font-size="{size}" letter-spacing="3" '
            f'fill="{INK}" opacity="{init}">{escape(role)}'
            f'<animate attributeName="opacity" calcMode="discrete" dur="{period}s" '
            f'repeatCount="indefinite" values="{vals}" keyTimes="{keys}"/></text>'
        )
    return "\n".join(out)


def hero():
    W, H = 1200, 600
    rails_l = [(0, 56), (56, 112)]
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
             f'aria-label="Vishal S - Backend and Cloud Engineer. Animated 3D wireframe torus.">',
             f'<rect width="{W}" height="{H}" fill="{BG}"/>']

    # grid of panels ------------------------------------------------------
    vlines = [56, 112, 660, 1048, 1096, 1148]
    for x in vlines:
        parts.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{H}" stroke="{HAIR}" stroke-width="1"/>')
    parts.append(f'<line x1="660" y1="318" x2="1048" y2="318" stroke="{HAIR}"/>')
    parts.append(f'<line x1="860" y1="318" x2="860" y2="{H}" stroke="{HAIR}"/>')
    parts.append(f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" fill="none" stroke="{HAIR}"/>')

    # left rails
    parts.append(rail_text(34, H - 24, "VISHAL S  /  PORTFOLIO  /  2026"))
    parts.append(f'<text x="28" y="34" font-family="{MONO}" font-size="10" fill="{INK}" text-anchor="middle">01</text>')
    parts.append(rail_text(90, H - 24, "BENGALURU, KARNATAKA, IN"))
    parts.append(f'<text x="84" y="34" font-family="{MONO}" font-size="10" fill="{MUTE}" text-anchor="middle">02</text>')

    # torus ---------------------------------------------------------------
    parts.append(torus_paths(386, 306, 205))
    parts.append(f'<text x="136" y="40" font-family="{MONO}" font-size="10" letter-spacing="2" fill="{MUTE}">'
                 f'FIG.00  TORUS  /  REAL 3D PROJECTION, 26S LOOP</text>')
    parts.append(f'<text x="136" y="{H - 24}" font-family="{MONO}" font-size="10" letter-spacing="2" fill="{DIM}">'
                 f'24 PARALLELS  x  48 VERTICES  x  19 KEYFRAMES</text>')

    # headline panel ------------------------------------------------------
    parts.append(f'<text x="692" y="40" font-family="{MONO}" font-size="10" letter-spacing="3" fill="{MUTE}">HELLO, I AM</text>')
    parts.append(f'<text x="688" y="124" font-family="{SANS}" font-size="78" font-weight="700" letter-spacing="-2" fill="{INK}">Vishal S</text>')
    parts.append(f'<line x1="692" y1="148" x2="1016" y2="148" stroke="{INK}" stroke-width="1"/>')
    parts.append(role_cycle(692, 182, ["BACKEND ENGINEER", "CLOUD  /  AWS", "TEST-DRIVEN BUILDER"]))
    para = [
        "Java / Spring Boot and Python / FastAPI",
        "services, covered by automated tests and",
        "shipped to AWS through CI/CD.",
        "",
        "B.E. CSE (Data Science), BIT.  CGPA 9.07",
    ]
    for i, ln in enumerate(para):
        parts.append(f'<text x="692" y="{226 + i * 17}" font-family="{MONO}" font-size="11.5" fill="{MUTE if i < 3 else INK}">{escape(ln)}</text>')

    # burst panel ---------------------------------------------------------
    parts.append(burst(760, 438, 8, 62))
    parts.append(f'<text x="676" y="{H - 24}" font-family="{MONO}" font-size="9" letter-spacing="2" fill="{DIM}">SYS / 2026</text>')

    # stat panel ----------------------------------------------------------
    parts.append(f'<text x="880" y="392" font-family="{SANS}" font-size="46" font-weight="700" fill="{INK}">30K</text>')
    parts.append(f'<text x="880" y="414" font-family="{MONO}" font-size="9.5" letter-spacing="1.5" fill="{MUTE}">LIVE USERS, RVS APP</text>')
    parts.append(f'<line x1="880" y1="438" x2="1028" y2="438" stroke="{HAIR}"/>')
    parts.append(f'<text x="880" y="494" font-family="{SANS}" font-size="46" font-weight="700" fill="{INK}">2m</text>')
    parts.append(f'<text x="880" y="516" font-family="{MONO}" font-size="9.5" letter-spacing="1.5" fill="{MUTE}">DAILY REPORT, WAS 30m</text>')

    # right rails ---------------------------------------------------------
    parts.append(rail_text(1078, H - 24, "BACKEND  /  CLOUD  /  TESTING"))
    parts.append(f'<text x="1072" y="34" font-family="{MONO}" font-size="10" fill="{MUTE}" text-anchor="middle">03</text>')
    parts.append(rail_text(1126, H - 24, "SPRING BOOT  /  FASTAPI  /  AWS"))
    parts.append(f'<text x="1120" y="34" font-family="{MONO}" font-size="10" fill="{MUTE}" text-anchor="middle">04</text>')
    parts.append(rail_text(1180, H - 24, "OPEN THE REPO  >  SCROLL"))
    parts.append(f'<text x="1174" y="34" font-family="{MONO}" font-size="10" fill="{MUTE}" text-anchor="middle">05</text>')

    parts.append("</svg>")
    write("hero.svg", "\n".join(parts))


# --------------------------------------------------------------------------
# 2. Isometric architecture diagrams
# --------------------------------------------------------------------------
def P(x, y, z=0.0):
    """Isometric projection. +x -> up-right, +y -> down-right, +z -> up."""
    return ((x + y) * S3, (y - x) * 0.5 - z)


def poly(points, fill, stroke="#c9c9c9", sw=0.9):
    pts = " ".join(f"{px:.1f},{py:.1f}" for px, py in points)
    return f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"/>'


def iso_box(n):
    x, y, w, d, h = n["x"], n["y"], n["w"], n["d"], n["h"]
    hl = n.get("hl", False)
    top_f, left_f, right_f = ("#efefef", "#8c8c8c", "#c2c2c2") if hl else ("#1b1b1b", "#0b0b0b", "#272727")
    top = [P(x, y, h), P(x + w, y, h), P(x + w, y + d, h), P(x, y + d, h)]
    left = [P(x, y, 0), P(x, y + d, 0), P(x, y + d, h), P(x, y, h)]
    right = [P(x, y + d, 0), P(x + w, y + d, 0), P(x + w, y + d, h), P(x, y + d, h)]
    out = [poly(left, left_f), poly(right, right_f), poly(top, top_f)]
    # index number lying flat on the top face
    ox, oy = P(x, y, h)
    col = "#050505" if hl else INK
    fs = min(w, d) * 0.46
    out.append(
        f'<text transform="translate({ox:.1f} {oy:.1f}) matrix({S3:.4f} -0.5 {S3:.4f} 0.5 0 0)" '
        f'x="{w * 0.18:.1f}" y="{d * 0.72:.1f}" font-family="{MONO}" font-size="{fs:.1f}" '
        f'font-weight="700" fill="{col}" fill-opacity="0.9">{n["num"]}</text>'
    )
    # billboard label, anchored above the topmost vertex of the top face
    tx_, ty_ = P(x + w, y, h)
    out.append(f'<line x1="{tx_:.1f}" y1="{ty_ - 2:.1f}" x2="{tx_:.1f}" y2="{ty_ - 9:.1f}" stroke="{DIM}"/>')
    out.append(f'<text x="{tx_:.1f}" y="{ty_ - 31:.1f}" text-anchor="middle" font-family="{MONO}" font-size="12.5" font-weight="700" fill="{INK}">{escape(n["label"])}</text>')
    out.append(f'<text x="{tx_:.1f}" y="{ty_ - 15:.1f}" text-anchor="middle" font-family="{MONO}" font-size="10" fill="{MUTE}">{escape(n["sub"])}</text>')
    return "\n".join(out)


def node_center(n):
    return (n["x"] + n["w"] / 2, n["y"] + n["d"] / 2)


def diagram(fname, fig, title, nodes, edges, caption, box=92):
    for n in nodes.values():
        n.setdefault("w", box)
        n.setdefault("d", box)
        n.setdefault("h", 48)
    order = list(nodes.keys())
    for i, k in enumerate(order, 1):
        nodes[k]["num"] = f"{i:02d}"

    # ---- bounds in screen space
    xs, ys = [], []
    for n in nodes.values():
        x, y, w, d, h = n["x"], n["y"], n["w"], n["d"], n["h"]
        for px, py in [P(x, y, h), P(x + w, y, h), P(x + w, y + d, 0), P(x, y + d, 0), P(x, y, 0), P(x + w, y, 0)]:
            xs.append(px); ys.append(py)
        cx, cy = P(x + w, y, h)
        lw = max(len(n["label"]) * 7.6, len(n["sub"]) * 6.2) / 2
        xs += [cx - lw, cx + lw]
        ys.append(cy - 46)
    minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
    pad, head, foot = 70, 84, 74
    W = max(980, maxx - minx + 2 * pad)
    H = maxy - miny + 2 * pad * 0.55 + head + foot
    tx = (W - (maxx - minx)) / 2 - minx
    ty = head + pad * 0.55 - miny

    g = []
    # floor grid
    gx0 = min(n["x"] for n in nodes.values()) - 60
    gx1 = max(n["x"] + n["w"] for n in nodes.values()) + 60
    gy0 = min(n["y"] for n in nodes.values()) - 60
    gy1 = max(n["y"] + n["d"] for n in nodes.values()) + 60
    step = 46
    gl = []
    x = gx0
    while x <= gx1:
        a, b = P(x, gy0), P(x, gy1)
        gl.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}"/>')
        x += step
    y = gy0
    while y <= gy1:
        a, b = P(gx0, y), P(gx1, y)
        gl.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}"/>')
        y += step
    g.append(f'<g stroke="#161616" stroke-width="1">{"".join(gl)}</g>')

    # edges (floor level) + travelling packets
    packets = []
    for ei, e in enumerate(edges):
        a, b = nodes[e[0]], nodes[e[1]]
        via = e[2] if len(e) > 2 and e[2] else []
        pts = [node_center(a)] + via + [node_center(b)]
        sp = [P(px, py) for px, py in pts]
        d_attr = "M" + " L".join(f"{px:.1f},{py:.1f}" for px, py in sp)
        g.append(f'<path d="{d_attr}" fill="none" stroke="#d8d8d8" stroke-width="1.3" stroke-dasharray="4 6">'
                 f'<animate attributeName="stroke-dashoffset" from="0" to="-20" dur="1.2s" repeatCount="indefinite"/></path>')
        packets.append(
            f'<circle r="3.4" fill="{INK}"><animateMotion dur="3.2s" begin="{-(ei * 0.7):.1f}s" repeatCount="indefinite" path="{d_attr}"/></circle>'
        )
    g.extend(packets)

    # boxes, far to near
    for k in sorted(nodes, key=lambda k: (nodes[k]["y"] - nodes[k]["x"])):
        g.append(iso_box(nodes[k]))

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}" width="{W:.0f}" height="{H:.0f}" role="img" aria-label="{escape(title)}">',
           f'<rect width="{W:.0f}" height="{H:.0f}" fill="{BG}"/>',
           f'<rect x="0.5" y="0.5" width="{W - 1:.0f}" height="{H - 1:.0f}" fill="none" stroke="{HAIR}"/>',
           f'<line x1="0" y1="64" x2="{W:.0f}" y2="64" stroke="{HAIR}"/>',
           f'<text x="28" y="39" font-family="{MONO}" font-size="11" letter-spacing="3" fill="{MUTE}">{escape(fig)}</text>',
           f'<text x="132" y="40" font-family="{SANS}" font-size="20" font-weight="700" fill="{INK}">{escape(title)}</text>',
           f'<text x="{W - 28:.0f}" y="39" text-anchor="end" font-family="{MONO}" font-size="10" letter-spacing="3" fill="{DIM}">VISHAL S  /  2026</text>',
           f'<g transform="translate({tx:.1f} {ty:.1f})">', *g, '</g>',
           f'<line x1="0" y1="{H - 56:.0f}" x2="{W:.0f}" y2="{H - 56:.0f}" stroke="{HAIR}"/>']
    for i, ln in enumerate(caption):
        svg.append(f'<text x="28" y="{H - 34 + i * 16:.0f}" font-family="{MONO}" font-size="10.5" fill="{MUTE}">{escape(ln)}</text>')
    svg.append("</svg>")
    write(fname, "\n".join(svg))


def diagrams():
    # ---- FIG 01 : cloud / CI-CD -------------------------------------------
    n = {
        "git":   dict(x=0,   y=0,   label="git push",       sub="GitHub",                h=34),
        "ci":    dict(x=190, y=0,   label="GitHub Actions", sub="build / pytest / push", h=58, hl=True),
        "ecr":   dict(x=380, y=0,   label="Amazon ECR",     sub="Docker images",         h=44),
        "ec2":   dict(x=380, y=190, label="EC2 t3.medium",  sub="FastAPI + React tool",  h=72, hl=True),
        "rds":   dict(x=190, y=190, label="RDS PostgreSQL", sub="managed database",      h=50),
        "lam":   dict(x=0,   y=380, label="AWS Lambda",     sub="Python + ReportLab",    h=58, hl=True),
        "rep":   dict(x=190, y=380, label="Daily report",   sub="30 min -> 2 min",       h=30),
    }
    diagram("arch-cloud.svg", "FIG.03", "Ship it: CI/CD and automation on AWS", n,
            [("git", "ci"), ("ci", "ecr"), ("ecr", "ec2"), ("ec2", "rds"), ("lam", "rep")],
            ["UNext Learning, Jul 2026 - present.  Internal workflow tool deployed on EC2 with managed RDS;",
             "pytest suites gate every release in the pipeline.  Lambda automation cuts a daily report from 30 to 2 minutes."])

    # ---- FIG 02 : RVS membership backend -----------------------------------
    n = {
        "cli":   dict(x=0,   y=190, label="Members app",  sub="30K live users",           h=36),
        "api":   dict(x=190, y=190, label="FastAPI",      sub="REST APIs / Docker",       h=70, hl=True),
        "pg":    dict(x=380, y=0,   label="PostgreSQL",   sub="primary data",             h=52),
        "xls":   dict(x=380, y=-190, label="Legacy Excel", sub="migrated once",          h=26),
        "red":   dict(x=380, y=190, label="Redis",        sub="OTP keys, auto-expiring TTL", h=46, hl=True),
        "min":   dict(x=380, y=380, label="MinIO",        sub="secured file storage",     h=46),
    }
    diagram("arch-rvs.svg", "FIG.02", "RVS Membership App: backend for 700K+ users", n,
            [("cli", "api"),
             ("api", "pg", [(286, 238), (286, 46)]),
             ("api", "red"),
             ("api", "min", [(286, 238), (286, 426)]),
             ("xls", "pg")],
            ["Freelance backend, Jun 2025 - Mar 2026. Led a team of 4; designed for 700K+ users, live with 30K.",
             "Moving OTPs from PostgreSQL to Redis TTL keys cut primary-DB load and sped up lookups."])

    # ---- FIG 03 : AssetIQ --------------------------------------------------
    n = {
        "cli":   dict(x=0,   y=0,    label="REST client",     sub="consistent JSON errors", h=34),
        "api":   dict(x=190, y=0,    label="Spring Boot API", sub="multi-tenant platform",  h=72, hl=True),
        "mon":   dict(x=380, y=0,    label="MongoDB",         sub="asset data",             h=50),
        "tst":   dict(x=190, y=-190, label="JUnit + Jacoco",  sub="coverage via Gradle",    h=44, hl=True),
        "exc":   dict(x=0,   y=190,  label="Exception handler", sub="structured API errors", h=40),
        "dok":   dict(x=380, y=190,  label="Docker",          sub="consistent deployment",  h=44),
    }
    diagram("arch-assetiq.svg", "FIG.01", "AssetIQ: multi-tenant asset management", n,
            [("cli", "api"), ("api", "mon"), ("tst", "api"),
             ("api", "exc", [(238, 238)]), ("api", "dok", [(238, 238)])],
            ["In progress, Jul 2026 - present.  Java, Spring Boot, MongoDB, Gradle.",
             "Centralized exception handling, JUnit suites with Jacoco reports, containerized with Docker."])

    # ---- FIG 04 : VTU result scraper --------------------------------------
    n = {
        "web":   dict(x=0,   y=0,   label="Results portal", sub="VTU",                       h=34),
        "cap":   dict(x=190, y=0,   label="OpenCV + Tesseract", sub="CAPTCHA solve + auto-retry", h=60, hl=True),
        "eng":   dict(x=380, y=0,   label="Multithreaded engine", sub="Selenium, parallel fetch", h=70, hl=True),
        "sql":   dict(x=380, y=190, label="SQLite",         sub="structured results",        h=46),
        "cht":   dict(x=190, y=190, label="Chart.js",       sub="batch insight dashboards",  h=40),
        "fla":   dict(x=0,   y=190, label="Flask app",      sub="Python",                    h=36),
    }
    diagram("arch-vtu.svg", "FIG.04", "VTU Result Scraper: 3 min -> under 60 s", n,
            [("web", "cap"), ("cap", "eng"), ("eng", "sql"), ("sql", "cht"), ("cht", "fla")],
            ["Aug 2024 - Dec 2024.  Automated CAPTCHA recognition with retry logic, parallelised fetches,",
             "results stored in SQLite and turned into batch insights on Chart.js dashboards."])


# --------------------------------------------------------------------------
# 3. Floating isometric skill stack
# --------------------------------------------------------------------------
def skill_stack():
    slabs = [  # bottom -> top
        ("LANGUAGES",          ["Java  /  Python  /  C  /  JavaScript"]),
        ("DATA & LIBRARIES",   ["NumPy  /  Pandas  /  Matplotlib  /  OpenCV", "Tesseract OCR  /  Chart.js"]),
        ("DATABASES",          ["PostgreSQL  /  MongoDB  /  Redis  /  SQLite"]),
        ("BACKEND",            ["Spring Boot  /  FastAPI  /  Flask", "Node.js  /  REST APIs"]),
        ("FRONTEND",           ["React  /  HTML  /  CSS"]),
        ("TESTING",            ["pytest  /  JUnit  /  Jacoco  /  Selenium", "Test Driven Development"]),
        ("CLOUD & DEVOPS",     ["AWS (EC2, RDS, ECR, Lambda)  /  Docker", "GitHub Actions  /  Gradle  /  Git  /  Linux  /  MinIO"]),
    ]
    w, d, t, gap = 400, 74, 10, 86
    n = len(slabs)
    # screen bounds
    x_min = P(0, d, 0)[0] - 10
    x_max = P(w, 0, 0)[0] + P(0, d, 0)[0] + 10
    W = 560
    top_y = P(w, 0, (n - 1) * gap + t)[1]
    bot_y = P(0, d, 0)[1]
    H = (bot_y - top_y) + 150
    ox = (W - (P(w, d)[0])) / 2
    oy = -top_y + 96

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H:.0f}" width="{W}" height="{H:.0f}" role="img" aria-label="Skill stack">',
           f'<rect width="{W}" height="{H:.0f}" fill="{BG}"/>',
           f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1:.0f}" fill="none" stroke="{HAIR}"/>',
           f'<text x="24" y="36" font-family="{MONO}" font-size="11" letter-spacing="3" fill="{MUTE}">FIG.05</text>',
           f'<text x="96" y="37" font-family="{SANS}" font-size="19" font-weight="700" fill="{INK}">The stack, layer by layer</text>',
           f'<line x1="0" y1="56" x2="{W}" y2="56" stroke="{HAIR}"/>',
           f'<g transform="translate({ox:.1f} {oy:.1f})">']
    for i, (title, lines) in enumerate(slabs):
        z = i * gap
        top_hl = i == n - 1
        top_f, left_f, right_f = ("#efefef", "#8c8c8c", "#c2c2c2") if top_hl else (
            ("#202020", "#0c0c0c", "#2c2c2c") if i % 2 else ("#181818", "#090909", "#242424"))
        txt = "#050505" if top_hl else INK
        sub = "#3a3a3a" if top_hl else MUTE
        top = [P(0, 0, z + t), P(w, 0, z + t), P(w, d, z + t), P(0, d, z + t)]
        left = [P(0, 0, z), P(0, d, z), P(0, d, z + t), P(0, 0, z + t)]
        right = [P(0, d, z), P(w, d, z), P(w, d, z + t), P(0, d, z + t)]
        ax, ay = P(0, 0, z + t)
        body = [poly(left, left_f), poly(right, right_f), poly(top, top_f)]
        body.append(
            f'<g transform="translate({ax:.1f} {ay:.1f}) matrix({S3:.4f} -0.5 {S3:.4f} 0.5 0 0)">'
            f'<text x="16" y="20" font-family="{MONO}" font-size="9.5" letter-spacing="2.5" fill="{sub}">{i + 1:02d}  {escape(title)}</text>'
            + "".join(f'<text x="16" y="{40 + j * 16}" font-family="{MONO}" font-size="11.5" font-weight="700" fill="{txt}">{escape(ln)}</text>'
                      for j, ln in enumerate(lines))
            + "</g>"
        )
        svg.append(
            f'<g>{"".join(body)}'
            f'<animateTransform attributeName="transform" type="translate" values="0 0;0 -6;0 0" '
            f'dur="5.5s" begin="{-i * 0.8:.1f}s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/></g>'
        )
    svg.append("</g>")
    svg.append(f'<text x="24" y="{H - 22:.0f}" font-family="{MONO}" font-size="10" fill="{DIM}">Foundations at the bottom, delivery at the top.</text>')
    svg.append("</svg>")
    write("skill-stack.svg", "\n".join(svg))


# --------------------------------------------------------------------------
# 4. Metrics strip with wireframe cubes
# --------------------------------------------------------------------------
def cube_wire(cx, cy, s, dur=14):
    # wireframe cube rotating about the vertical axis, projected on each keyframe
    verts = [(x, y, z) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
    edges = [(a, b) for a in range(8) for b in range(a + 1, 8)
             if sum(abs(verts[a][i] - verts[b][i]) for i in range(3)) == 2]
    frames = 16
    tilt = math.radians(28)
    out = []
    for (a, b) in edges:
        vals = []
        for f in range(frames + 1):
            ang = 0.62 + (math.pi / 2) * f / frames  # symmetric every 90 degrees
            pts = []
            for vi in (a, b):
                x, y, z = verts[vi]
                x2 = x * math.cos(ang) + z * math.sin(ang)
                z2 = -x * math.sin(ang) + z * math.cos(ang)
                y2 = y * math.cos(tilt) - z2 * math.sin(tilt)
                pts.append((cx + x2 * s, cy + y2 * s))
            vals.append(f"M{pts[0][0]:.1f},{pts[0][1]:.1f} L{pts[1][0]:.1f},{pts[1][1]:.1f}")
        out.append(f'<path d="{vals[0]}" stroke="{INK}" stroke-width="1" fill="none" stroke-opacity="0.85">'
                   f'<animate attributeName="d" dur="{dur}s" repeatCount="indefinite" values="{";".join(vals)}"/></path>')
    return "".join(out)


def metrics():
    W, H = 1200, 250
    cells = [
        ("30 > 2", "MINUTES", "Daily stakeholder report, automated on AWS Lambda"),
        ("700K+", "USERS", "Designed-for scale of the RVS backend; live with 30K"),
        ("3m > 60s", "FETCH TIME", "VTU result scraper with Selenium + OpenCV"),
        ("9.07", "CGPA", "B.E. CSE (Data Science), Bangalore Institute of Technology"),
    ]
    cw = W / 4
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Key numbers">',
         f'<rect width="{W}" height="{H}" fill="{BG}"/>',
         f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" fill="none" stroke="{HAIR}"/>']
    for i, (big, unit, desc) in enumerate(cells):
        x0 = i * cw
        if i:
            s.append(f'<line x1="{x0}" y1="0" x2="{x0}" y2="{H}" stroke="{HAIR}"/>')
        s.append(cube_wire(x0 + cw - 52, 50, 16, dur=12 + i * 2))
        s.append(f'<text x="{x0 + 28}" y="40" font-family="{MONO}" font-size="10" letter-spacing="3" fill="{MUTE}">{i + 1:02d}  {unit}</text>')
        s.append(f'<text x="{x0 + 26}" y="132" font-family="{SANS}" font-size="56" font-weight="700" letter-spacing="-2" fill="{INK}">{escape(big)}</text>')
        s.append(f'<line x1="{x0 + 28}" y1="158" x2="{x0 + cw - 28}" y2="158" stroke="{HAIR}"/>')
        # wrap description at ~34 chars
        words, lines, cur = desc.split(), [], ""
        for wd in words:
            if len(cur) + len(wd) + 1 > 34:
                lines.append(cur); cur = wd
            else:
                cur = (cur + " " + wd).strip()
        lines.append(cur)
        for j, ln in enumerate(lines):
            s.append(f'<text x="{x0 + 28}" y="{184 + j * 16}" font-family="{MONO}" font-size="11" fill="{MUTE}">{escape(ln)}</text>')
    s.append("</svg>")
    write("metrics.svg", "\n".join(s))


if __name__ == "__main__":
    print("Generating assets ->", os.path.abspath(OUT))
    hero()
    diagrams()
    skill_stack()
    metrics()
    print("done")
