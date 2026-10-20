"""Generate assets/generated/stats.svg from live GitHub data.

Runs inside GitHub Actions (see .github/workflows/profile.yml).
Needs env GITHUB_TOKEN (the default Actions token works for public data;
set a PAT secret named METRICS_TOKEN to include private contributions).
Standard library only — no pip install needed.
"""
import datetime as dt
import json
import os
import sys
import urllib.request
from pathlib import Path

USER = os.environ.get("GH_USER", "ebaoacho")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
OUT = Path(__file__).resolve().parent.parent / "assets" / "generated" / "stats.svg"

BG, GREEN, BLUE, TEXT, MUTED = "#0D1117", "#00E5A0", "#58A6FF", "#E6EDF3", "#8B949E"
SANS = "-apple-system,'Segoe UI','Hiragino Sans','Noto Sans JP',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"

QUERY = """
query($login: String!) {
  user(login: $login) {
    createdAt
    followers { totalCount }
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      restrictedContributionsCount
      contributionCalendar {
        totalContributions
        weeks { contributionDays { contributionCount date } }
      }
    }
    repositories(ownerAffiliations: OWNER, isFork: false, first: 100, privacy: PUBLIC) {
      totalCount
      nodes {
        stargazerCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
  }
}
"""


def fetch():
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
        headers={"Authorization": f"bearer {TOKEN}", "User-Agent": "profile-stats"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if "errors" in data:
        sys.exit(f"GraphQL error: {data['errors']}")
    return data["data"]["user"]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def streaks(days):
    cur = best = run = 0
    for d in days:
        run = run + 1 if d["contributionCount"] > 0 else 0
        best = max(best, run)
    # current streak: count back from today (today may still be 0)
    for i, d in enumerate(reversed(days)):
        if d["contributionCount"] > 0:
            cur += 1
        elif i == 0:
            continue
        else:
            break
    return cur, best


def render(u):
    cc = u["contributionsCollection"]
    cal = cc["contributionCalendar"]
    days = [d for w in cal["weeks"] for d in w["contributionDays"]]
    cur, best = streaks(days)
    stars = sum(n["stargazerCount"] for n in u["repositories"]["nodes"])

    langs = {}
    for n in u["repositories"]["nodes"]:
        for e in n["languages"]["edges"]:
            k = e["node"]["name"]
            if k in ("HTML", "CSS", "Dockerfile", "Shell", "Batchfile", "Procfile"):
                continue
            c = e["node"]["color"] or MUTED
            langs.setdefault(k, [0, c])[0] += e["size"]
    total = sum(v[0] for v in langs.values()) or 1
    top = sorted(langs.items(), key=lambda kv: -kv[1][0])[:6]

    W, H = 1000, 330
    s = []
    s.append(f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="GitHub stats for {USER}">
  <title>GitHub stats — {USER}</title>
  <style>
    .in {{ opacity: 0; animation: in .7s ease-out forwards; }}
    @keyframes in {{ from {{ opacity: 0; transform: translateY(8px); }} to {{ opacity: 1; transform: none; }} }}
    .cell {{ opacity: 0; animation: cell .35s ease-out forwards; }}
    @keyframes cell {{ to {{ opacity: 1; }} }}
    .bar {{ transform-box: fill-box; transform-origin: left; transform: scaleX(0); animation: grow 1.1s cubic-bezier(.2,.8,.2,1) forwards; }}
    @keyframes grow {{ to {{ transform: scaleX(1); }} }}
    .pulse {{ animation: pulse 2s ease-in-out infinite; }}
    @keyframes pulse {{ 50% {{ opacity: .35; }} }}
  </style>
  <rect width="{W}" height="{H}" rx="12" fill="{BG}"/>
  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12" fill="none" stroke="#21262D"/>
  <text x="32" y="40" fill="{MUTED}" font-family="{MONO}" font-size="12" letter-spacing="2">ACTIVITY · LAST 12 MONTHS</text>
  <circle cx="{W - 120}" cy="36" r="4" fill="{GREEN}" class="pulse"/>
  <text x="{W - 108}" y="40" fill="{MUTED}" font-family="{MONO}" font-size="11">auto-synced</text>""")

    tiles = [
        ("Contributions", cal["totalContributions"]),
        ("Commits", cc["totalCommitContributions"]),
        ("Pull Requests", cc["totalPullRequestContributions"]),
        ("Current Streak", f"{cur}d"),
        ("Best Streak", f"{best}d"),
        ("Public Repos", u["repositories"]["totalCount"]),
    ]
    tw = (W - 64 - 5 * 12) / 6
    for i, (label, val) in enumerate(tiles):
        x = 32 + i * (tw + 12)
        s.append(f"""  <g class="in" style="animation-delay:{0.1 + i * 0.08:.2f}s">
    <rect x="{x:.1f}" y="58" width="{tw:.1f}" height="74" rx="10" fill="#161B22" stroke="#30363D"/>
    <text x="{x + 14:.1f}" y="98" fill="{GREEN if i in (0, 3) else TEXT}" font-family="{SANS}" font-size="26" font-weight="800">{val}</text>
    <text x="{x + 14:.1f}" y="120" fill="{MUTED}" font-family="{SANS}" font-size="12">{label}</text>
  </g>""")

    # Contribution heatmap
    weeks = cal["weeks"][-53:]
    cs, gap = 11, 3
    gx, gy = 32, 160
    peak = max((d["contributionCount"] for d in days), default=0) or 1
    shades = ["#161B22", "#0B3D2E", "#0E6B4C", "#10A372", GREEN]
    for wi, w in enumerate(weeks):
        for d in w["contributionDays"]:
            wd = dt.date.fromisoformat(d["date"]).isoweekday() % 7
            c = d["contributionCount"]
            lvl = 0 if c == 0 else min(4, 1 + int(3 * c / peak))
            s.append(f'  <rect class="cell" style="animation-delay:{0.4 + wi * 0.018:.3f}s" x="{gx + wi * (cs + gap)}" y="{gy + wd * (cs + gap)}" width="{cs}" height="{cs}" rx="2.5" fill="{shades[lvl]}"><title>{d["date"]}: {c}</title></rect>')

    # Languages
    lx = gx + 53 * (cs + gap) + 22
    lw = W - lx - 32
    s.append(f'  <text x="{lx}" y="{gy + 10}" fill="{MUTED}" font-family="{MONO}" font-size="12" letter-spacing="2">TOP LANGUAGES</text>')
    for i, (name, (size, color)) in enumerate(top):
        y = gy + 30 + i * 16
        pct = size / total * 100
        s.append(f"""  <g class="in" style="animation-delay:{0.6 + i * 0.1:.2f}s">
    <circle cx="{lx + 5}" cy="{y - 4}" r="4" fill="{color}"/>
    <text x="{lx + 15}" y="{y}" fill="{TEXT}" font-family="{SANS}" font-size="12">{esc(name)}</text>
    <text x="{lx + lw}" y="{y}" fill="{MUTED}" font-family="{MONO}" font-size="11" text-anchor="end">{pct:.1f}%</text>
  </g>""")
    # stacked bar
    bx = lx
    by = gy + 30 + len(top) * 16 + 4
    for i, (name, (size, color)) in enumerate(top):
        w = lw * size / sum(v[0] for _, v in top)
        s.append(f'  <rect class="bar" style="animation-delay:{0.9 + i * 0.12:.2f}s" x="{bx:.1f}" y="{by}" width="{max(w - 2, 1):.1f}" height="8" rx="3" fill="{color}"/>')
        bx += w

    s.append(f"""  <text x="32" y="{H - 22}" fill="{MUTED}" font-family="{MONO}" font-size="11">★ {stars} stars · {u['followers']['totalCount']} followers · updated {dt.datetime.utcnow():%Y-%m-%d %H:%M} UTC</text>
</svg>""")
    return "\n".join(s)


if __name__ == "__main__":
    if not TOKEN:
        sys.exit("GITHUB_TOKEN is not set")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(fetch()), encoding="utf-8")
    print("wrote", OUT)
