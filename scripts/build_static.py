"""Build the hand-crafted animated SVGs in assets/.

Run:  python scripts/build_static.py
Everything is self-contained (no external fonts/images), so GitHub renders it
reliably. Animations use SMIL + CSS, which work inside <img>-embedded SVGs.
"""
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"
ASSETS.mkdir(exist_ok=True)

BG = "#0D1117"
GREEN = "#00E5A0"
BLUE = "#58A6FF"
TEXT = "#E6EDF3"
MUTED = "#8B949E"
YELLOW = "#FFD166"
SANS = "-apple-system,'Segoe UI','Hiragino Sans','Noto Sans JP',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"


# --------------------------------------------------------------------------- #
# 1. Header: animated tracking demo on a pitch + name and rotating taglines
# --------------------------------------------------------------------------- #
def header() -> str:
    W, H = 1000, 320
    # Pitch area
    px, py, pw, ph = 520, 34, 446, 252

    # Ball route between attackers (ball positions), with holds at each player.
    pts = [(600, 210), (690, 112), (800, 196), (900, 98)]
    seq = [pts[0], pts[0], pts[1], pts[1], pts[2], pts[2], pts[3], pts[3], pts[0]]
    kt = "0;0.12;0.25;0.37;0.5;0.62;0.75;0.87;1"
    trans = ";".join(f"{x} {y}" for x, y in seq)
    dur = "10s"

    owner = [
        "1;1;0;0;0;0;0;0;1",
        "0;0;1;1;0;0;0;0;0",
        "0;0;0;0;1;1;0;0;0",
        "0;0;0;0;0;0;1;1;0",
    ]
    numbers = ["#7", "#10", "#8", "#9"]

    attackers = ""
    for i, ((x, y), op, num) in enumerate(zip(pts, owner, numbers)):
        cx, cy = x - 13, y - 6
        attackers += f"""
    <g>
      <circle cx="{cx}" cy="{cy}" r="16" fill="none" stroke="{GREEN}" stroke-width="1.5" opacity="0">
        <animate attributeName="opacity" values="{op}" keyTimes="{kt}" dur="{dur}" repeatCount="indefinite"/>
        <animate attributeName="r" values="14;19;14" dur="1.2s" repeatCount="indefinite"/>
      </circle>
      <circle cx="{cx}" cy="{cy}" r="7" fill="{GREEN}"/>
      <text x="{cx}" y="{cy - 13}" fill="{GREEN}" font-family="{MONO}" font-size="10" text-anchor="middle" opacity="0.85">{num}</text>
    </g>"""

    # Defenders drifting around
    defenders = ""
    dpos = [(650, 150, "8 -6"), (745, 160, "-10 8"), (850, 140, "6 10"), (870, 230, "-8 -6"), (720, 240, "10 -4"), (940, 170, "-6 6")]
    for i, (x, y, d) in enumerate(dpos):
        defenders += f"""
    <circle cx="{x}" cy="{y}" r="6.5" fill="{BLUE}" opacity="0.9">
      <animateTransform attributeName="transform" type="translate" values="0 0;{d};0 0" dur="{3 + i * 0.6:.1f}s" repeatCount="indefinite"/>
    </circle>"""

    # HUD readout: who has the ball
    hud = ""
    for op, num in zip(owner, numbers):
        hud += f"""
      <text x="{px + 14}" y="{py + ph - 14}" fill="{GREEN}" font-family="{MONO}" font-size="12" opacity="0">ON-BALL: GREEN {num}
        <animate attributeName="opacity" values="{op}" keyTimes="{kt}" dur="{dur}" repeatCount="indefinite"/>
      </text>"""

    taglines = [
        "Computer Vision × Sports Analytics",
        "Finding a 22cm ball on a 105m pitch.",
        "Who has the ball? I teach models to answer.",
        "Research by day. Shipping products by night.",
    ]
    n = len(taglines)
    cycle = 3.2 * n
    tag_css = ""
    tag_svg = ""
    for i, t in enumerate(taglines):
        start = i / n * 100
        end = (i + 1) / n * 100
        tag_css += f"""
    @keyframes tag{i} {{
      0%, {max(start - 0.01, 0):.2f}% {{ opacity: 0; transform: translateY(8px); }}
      {start + 3:.2f}%, {end - 4:.2f}% {{ opacity: 1; transform: translateY(0); }}
      {end:.2f}%, 100% {{ opacity: 0; transform: translateY(-8px); }}
    }}
    .tag{i} {{ animation: tag{i} {cycle:.1f}s ease-in-out infinite; opacity: 0; }}"""
        tag_svg += f'\n    <text class="tag{i}" x="48" y="214" fill="{GREEN}" font-family="{MONO}" font-size="17">&gt; {t}</text>'

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Nao Ebata — Computer Vision × Sports Analytics">
  <title>Nao Ebata — Computer Vision × Sports Analytics</title>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{BG}"/>
      <stop offset="1" stop-color="#0A2A20"/>
    </linearGradient>
    <linearGradient id="scan" x1="0" x2="1">
      <stop offset="0" stop-color="{GREEN}" stop-opacity="0"/>
      <stop offset="1" stop-color="{GREEN}" stop-opacity="0.22"/>
    </linearGradient>
    <linearGradient id="grass" x1="0" x2="1">
      <stop offset="0" stop-color="#0E3B2C"/>
      <stop offset="1" stop-color="#0B2F23"/>
    </linearGradient>
    <clipPath id="pitch"><rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="6"/></clipPath>
  </defs>
  <style>
    .fade {{ animation: fade 1.2s ease-out both; }}
    .fade2 {{ animation: fade 1.2s ease-out 0.35s both; }}
    .fade3 {{ animation: fade 1.2s ease-out 0.7s both; }}
    @keyframes fade {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
    .line {{ stroke-dasharray: 1400; stroke-dashoffset: 1400; animation: draw 2.4s ease-out 0.2s forwards; }}
    @keyframes draw {{ to {{ stroke-dashoffset: 0; }} }}
    .scan {{ animation: scan 4s linear infinite; }}
    @keyframes scan {{ from {{ transform: translateX(0); }} to {{ transform: translateX({pw + 60}px); }} }}
    .cursor {{ animation: blink 1s steps(1) infinite; }}
    @keyframes blink {{ 50% {{ opacity: 0; }} }}
    .rec {{ animation: blink 1.4s steps(1) infinite; }}{tag_css}
  </style>

  <rect width="{W}" height="{H}" rx="14" fill="url(#bg)"/>
  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="14" fill="none" stroke="#21262D"/>

  <!-- Left: identity -->
  <g class="fade">
    <text x="48" y="74" fill="{MUTED}" font-family="{MONO}" font-size="14" letter-spacing="2">HELLO, WORLD — I'M</text>
  </g>
  <g class="fade2">
    <text x="46" y="136" fill="{TEXT}" font-family="{SANS}" font-size="58" font-weight="800" letter-spacing="-1">Nao Ebata</text>
    <text x="48" y="170" fill="{MUTED}" font-family="{SANS}" font-size="17">江畑 尚 · CV Researcher &amp; Full-stack Engineer</text>
  </g>
  <g>{tag_svg}
  </g>
  <g class="fade3">
    <rect x="48" y="246" width="190" height="30" rx="15" fill="none" stroke="{GREEN}" stroke-opacity="0.6"/>
    <circle cx="66" cy="261" r="4" fill="{GREEN}" class="rec"/>
    <text x="78" y="266" fill="{TEXT}" font-family="{MONO}" font-size="13">Kansai Univ. · M2</text>
    <rect x="250" y="246" width="150" height="30" rx="15" fill="none" stroke="#30363D"/>
    <text x="268" y="266" fill="{MUTED}" font-family="{MONO}" font-size="13">Osaka, Japan</text>
  </g>

  <!-- Right: live tracking demo -->
  <g clip-path="url(#pitch)">
    <rect x="{px}" y="{py}" width="{pw}" height="{ph}" fill="url(#grass)"/>
    {''.join(f'<rect x="{px + i * pw / 8:.1f}" y="{py}" width="{pw / 16:.1f}" height="{ph}" fill="#ffffff" opacity="0.025"/>' for i in range(8))}
    <g fill="none" stroke="#3FB98A" stroke-opacity="0.45" stroke-width="1.5">
      <rect class="line" x="{px + 8}" y="{py + 8}" width="{pw - 16}" height="{ph - 16}"/>
      <line class="line" x1="{px + pw / 2}" y1="{py + 8}" x2="{px + pw / 2}" y2="{py + ph - 8}"/>
      <circle class="line" cx="{px + pw / 2}" cy="{py + ph / 2}" r="34"/>
      <rect class="line" x="{px + 8}" y="{py + ph / 2 - 60}" width="62" height="120"/>
      <rect class="line" x="{px + pw - 70}" y="{py + ph / 2 - 60}" width="62" height="120"/>
    </g>
    <rect class="scan" x="{px - 60}" y="{py}" width="60" height="{ph}" fill="url(#scan)"/>
    {defenders}
    {attackers}

    <!-- Ball + detection box -->
    <g>
      <animateTransform attributeName="transform" type="translate" values="{trans}" keyTimes="{kt}" dur="{dur}" calcMode="spline"
        keySplines="0 0 1 1;.45 0 .25 1;0 0 1 1;.45 0 .25 1;0 0 1 1;.45 0 .25 1;0 0 1 1;.4 0 .2 1" repeatCount="indefinite"/>
      <circle r="4.5" fill="#ffffff"/>
      <rect x="-10" y="-10" width="20" height="20" fill="none" stroke="{YELLOW}" stroke-width="1.6"/>
      <rect x="10" y="10" width="64" height="14" fill="{YELLOW}"/>
      <text x="14" y="20.5" fill="{BG}" font-family="{MONO}" font-size="10" font-weight="700">ball 0.97</text>
    </g>

    <!-- HUD -->
    <rect x="{px}" y="{py}" width="{pw}" height="26" fill="#000" opacity="0.35"/>
    <circle cx="{px + 16}" cy="{py + 13}" r="4" fill="#FF4D4F" class="rec"/>
    <text x="{px + 28}" y="{py + 17}" fill="{TEXT}" font-family="{MONO}" font-size="11">LIVE · ball-detector + possession-estimator</text>
    {hud}
  </g>
  <rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="6" fill="none" stroke="#30363D"/>
</svg>
"""


# --------------------------------------------------------------------------- #
# 2. whoami: terminal with typing animation
# --------------------------------------------------------------------------- #
def whoami() -> str:
    W = 1000
    CH = 8.4  # approx advance width of a 14px monospace glyph
    lines = [
        ("prompt", "$ cat ./nao_ebata.yaml"),
        ("key", "name:", "江畑 尚 (Nao Ebata)"),
        ("key", "role:", "Graduate researcher · Full-stack engineer"),
        ("key", "lab:", "Kansai University, Graduate School of Informatics (M2)"),
        ("key", "research:", "[ball_detection, possession_estimation, tactical_change_points]"),
        ("key", "ships:", "[web_apps, ios_flutter_apps, reservation_payment, llm_tools]"),
        ("key", "awards:", "[JPHacks 三菱重工賞 & SecureCycle賞, RSS Hackathon 審査員特別賞]"),
        ("key", "philosophy:", "\"AI does what it's good at. Humans do the rest.\""),
        ("prompt", "$ ./say_hi --to you"),
        ("out", "Show me a match video. I'll tell you where the ball is — and who's got it. ⚽"),
    ]
    top, lh = 68, 26
    H = top + lh * len(lines) + 36
    body = ""
    t = 0.4
    for i, ln in enumerate(lines):
        y = top + i * lh
        if ln[0] == "prompt":
            text = ln[1]
            content = f'<tspan fill="{GREEN}">$</tspan><tspan fill="{TEXT}">{text[1:]}</tspan>'
            n = len(text)
            speed = 0.03
        elif ln[0] == "key":
            k, v = ln[1], ln[2]
            content = f'<tspan fill="{BLUE}">  {k}</tspan><tspan fill="{TEXT}"> {v.replace("&", "&amp;")}</tspan>'
            n = len(k) + len(v) + 3
            speed = 0.008
        else:
            text = ln[1]
            content = f'<tspan fill="{YELLOW}">  {text}</tspan>'
            n = len(text) + 2
            speed = 0.015
        raw = "".join(x for x in ln[1:])
        cells = sum(2 if ord(c) > 0x2E80 else 1 for c in raw) + 4
        width = cells * CH + 40  # CJK glyphs take two cells
        d = min(max(n * speed, 0.25), 0.9)
        steps = min(n, 60)
        vals = ";".join(f"{width * k / steps:.1f}" for k in range(steps + 1))
        body += f"""
  <clipPath id="c{i}"><rect x="28" y="{y - 18}" height="{lh}" width="0">
    <animate attributeName="width" values="{vals}" dur="{d:.2f}s" begin="{t:.2f}s" fill="freeze" calcMode="discrete"/>
  </rect></clipPath>
  <text x="32" y="{y}" font-family="{MONO}" font-size="14" clip-path="url(#c{i})" xml:space="preserve">{content}</text>"""
        t += d + (0.25 if ln[0] == "prompt" else 0.04)
    cy = top + lh * len(lines)
    body += f"""
  <rect x="32" y="{cy - 14}" width="9" height="17" fill="{GREEN}" opacity="0">
    <set attributeName="opacity" to="1" begin="{t:.2f}s"/>
    <animate attributeName="opacity" values="1;0;1" dur="1s" begin="{t:.2f}s" repeatCount="indefinite" calcMode="discrete"/>
  </rect>"""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="whoami terminal">
  <title>whoami</title>
  <rect width="{W}" height="{H}" rx="12" fill="{BG}"/>
  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12" fill="none" stroke="#30363D"/>
  <rect width="{W}" height="36" rx="12" fill="#161B22"/>
  <rect y="24" width="{W}" height="12" fill="#161B22"/>
  <circle cx="22" cy="18" r="6" fill="#FF5F56"/><circle cx="42" cy="18" r="6" fill="#FFBD2E"/><circle cx="62" cy="18" r="6" fill="#27C93F"/>
  <text x="{W / 2}" y="23" fill="{MUTED}" font-family="{MONO}" font-size="12" text-anchor="middle">ebaoacho@kansai-u: ~/profile — zsh</text>
{body}
</svg>
"""


# --------------------------------------------------------------------------- #
# 3. Tech stack: chips that pop in group by group
# --------------------------------------------------------------------------- #
def stack() -> str:
    groups = [
        ("VISION / ML", [("Python", "#3572A5"), ("PyTorch", "#EE4C2C"), ("OpenCV", "#5C3EE8"), ("YOLO", "#00FFFF"),
                         ("KPConv", "#7EE787"), ("LangChain", "#1C9C7C"), ("Gemini API", "#8E75B2")]),
        ("WEB / APP", [("TypeScript", "#3178C6"), ("Next.js", "#E6EDF3"), ("React", "#61DAFB"), ("Tailwind", "#38BDF8"),
                       ("Flutter", "#02569B"), ("Swift", "#F05138"), ("Django", "#44B78B"), ("PHP", "#777BB4"), ("WordPress", "#21759B")]),
        ("DATA / INFRA", [("Supabase", "#3ECF8E"), ("PostgreSQL", "#4169E1"), ("MySQL", "#4479A1"), ("Prisma", "#A0AEC0"),
                          ("Docker", "#2496ED"), ("Nginx", "#009639"), ("Vercel", "#E6EDF3"), ("Stripe", "#635BFF")]),
    ]
    W = 1000
    y = 30
    out = ""
    delay = 0.2
    for title, items in groups:
        out += f'<text x="32" y="{y + 20}" fill="{MUTED}" font-family="{MONO}" font-size="12" letter-spacing="2">{title}</text>'
        x = 170
        for name, color in items:
            w = len(name) * 7.3 + 32
            if x + w > W - 24:
                x = 170
                y += 42
            out += f"""
  <g class="chip" style="animation-delay:{delay:.2f}s">
    <rect x="{x}" y="{y}" width="{w:.0f}" height="30" rx="15" fill="#161B22" stroke="#30363D"/>
    <circle cx="{x + 15}" cy="{y + 15}" r="4.5" fill="{color}"/>
    <text x="{x + 26}" y="{y + 19.5}" fill="{TEXT}" font-family="{SANS}" font-size="12.5" font-weight="600">{name}</text>
  </g>"""
            x += w + 8
            delay += 0.06
        y += 54
    H = y + 6
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Tech stack">
  <title>Tech stack</title>
  <style>
    .chip {{ opacity: 0; animation: pop .5s cubic-bezier(.2,.9,.3,1.3) forwards; transform-box: fill-box; transform-origin: center; }}
    @keyframes pop {{ from {{ opacity: 0; transform: translateY(10px) scale(.9); }} to {{ opacity: 1; transform: none; }} }}
  </style>
  <rect width="{W}" height="{H}" rx="12" fill="{BG}"/>
  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12" fill="none" stroke="#21262D"/>
  {out}
</svg>
"""


# --------------------------------------------------------------------------- #
# 4. Section divider + footer wave
# --------------------------------------------------------------------------- #
def footer() -> str:
    W, H = 1000, 110
    def wave(a, ph):
        pts = " ".join(f"{x},{H / 2 + a * __import__('math').sin((x / W) * 6.283 * 2 + ph):.1f}" for x in range(0, W + 1, 20))
        return f"M0,{H} L{pts.replace(' ', ' L')} L{W},{H} Z"
    w1a, w1b = wave(14, 0), wave(14, 3.14)
    w2a, w2b = wave(10, 1.5), wave(10, 4.6)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <path fill="{GREEN}" opacity="0.18" d="{w1a}"><animate attributeName="d" values="{w1a};{w1b};{w1a}" dur="7s" repeatCount="indefinite"/></path>
  <path fill="#0B3D2E" opacity="0.9" d="{w2a}"><animate attributeName="d" values="{w2a};{w2b};{w2a}" dur="5s" repeatCount="indefinite"/></path>
  <text x="{W / 2}" y="{H - 22}" fill="{TEXT}" font-family="{MONO}" font-size="13" text-anchor="middle" opacity="0.85">Detection is the easy part. Understanding the game is the goal.</text>
</svg>
"""


if __name__ == "__main__":
    for name, fn in [("header", header), ("whoami", whoami), ("stack", stack), ("footer", footer)]:
        (ASSETS / f"{name}.svg").write_text(fn(), encoding="utf-8")
        print("wrote", ASSETS / f"{name}.svg")
