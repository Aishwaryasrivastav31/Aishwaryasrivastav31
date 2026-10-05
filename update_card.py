#!/usr/bin/env python3
"""Builds dark_mode.svg and light_mode.svg for the GitHub profile README.

Runs inside GitHub Actions (see .github/workflows/update.yml).
Edit the INFO block below to change what the card says.
"""
import datetime as dt
import io
import json
import os
import sys
import time
import urllib.request
from xml.sax.saxutils import escape

from PIL import Image, ImageOps

USER = "Aishwaryasrivastav31"
PROMPT = "aishwarya@github"

# ---- EDIT ME: (label, value). Lines with an empty value are skipped. -------
INFO = [
    ("OS", "Linux, Windows"),
    ("Uptime", "{uptime}"),                     # filled in automatically
    ("Host", ""),                               # e.g. your college / employer
    ("Kernel", "Machine Learning | Deep Learning | Research"),
    ("IDE", "VS Code, Jupyter"),
    None,                                       # None = blank line
    ("Languages.Programming", "Python, SQL"),
    ("Languages.Frameworks", "PyTorch, scikit-learn, Pandas"),
    ("Languages.Real", "Hindi, English"),
    None,
    ("Research.Focus", ""),                     # e.g. Explainable AI, NLP
    ("Research.ORCID", "0009-0009-8546-2944"),
    ("Projects", "AdaptiveSpread, DATA-WORK-AUTOMATION"),
    ("Hobbies", "Coffee, making docs look aesthetic"),
]
CONTACT = [
    ("Email", ""),
    ("LinkedIn", ""),
    ("GitHub", USER),
    ("Location", "New Delhi, India"),
]
# ---------------------------------------------------------------------------

COLS, ROWS = 44, 21          # ASCII art size in characters
WIDTH = 56                   # info column width in characters
CW, LH, FS = 9.6, 20, 16     # char width, line height, font size (px)
RAMP = " .:-=+*#%@"
THEMES = {
    "dark":  dict(bg="#161b22", fg="#c9d1d9", key="#ffa657", val="#a5d6ff", dot="#616e7f"),
    "light": dict(bg="#f6f8fa", fg="#24292f", key="#953800", val="#0a3069", dot="#b6c2d0"),
}
API = "https://api.github.com"
TOKEN = os.environ.get("GH_TOKEN", "")


def api(path, body=None, tries=1):
    """GET (or POST when body is given) against the GitHub API."""
    for attempt in range(tries):
        req = urllib.request.Request(
            path if path.startswith("http") else API + path,
            data=json.dumps(body).encode() if body else None,
            headers={"Authorization": f"Bearer {TOKEN}",
                     "Accept": "application/vnd.github+json",
                     "User-Agent": USER},
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            if r.status == 202:              # GitHub is still computing stats
                time.sleep(4)
                continue
            raw = r.read()
            return json.loads(raw) if raw else None
    return None


def gql(query, **variables):
    out = api("/graphql", {"query": query, "variables": variables})
    if out.get("errors"):
        raise RuntimeError(out["errors"])
    return out["data"]


def fetch_stats():
    repos, stars, cursor = [], 0, None
    while True:
        d = gql("""query($u:String!,$c:String){user(login:$u){
            createdAt avatarUrl(size:400) followers{totalCount}
            repositories(first:100,after:$c,ownerAffiliations:OWNER,isFork:false){
              totalCount pageInfo{hasNextPage endCursor}
              nodes{name stargazerCount}}}}""", u=USER, c=cursor)["user"]
        for n in d["repositories"]["nodes"]:
            repos.append(n["name"])
            stars += n["stargazerCount"]
        if not d["repositories"]["pageInfo"]["hasNextPage"]:
            break
        cursor = d["repositories"]["pageInfo"]["endCursor"]

    created = dt.datetime.fromisoformat(d["createdAt"].replace("Z", "+00:00"))
    now = dt.datetime.now(dt.timezone.utc)
    commits = 0
    for year in range(created.year, now.year + 1):
        c = gql("""query($u:String!,$f:DateTime!,$t:DateTime!){user(login:$u){
            contributionsCollection(from:$f,to:$t){
              totalCommitContributions restrictedContributionsCount}}}""",
                u=USER, f=f"{year}-01-01T00:00:00Z", t=f"{year}-12-31T23:59:59Z")
        c = c["user"]["contributionsCollection"]
        commits += c["totalCommitContributions"] + c["restrictedContributionsCount"]

    added = deleted = 0
    for name in repos:                       # lines of code written by USER
        try:
            for person in api(f"/repos/{USER}/{name}/stats/contributors", tries=4) or []:
                if (person.get("author") or {}).get("login", "").lower() == USER.lower():
                    added += sum(w["a"] for w in person["weeks"])
                    deleted += sum(w["d"] for w in person["weeks"])
        except Exception as e:               # empty repo etc. - just skip it
            print(f"  loc skipped for {name}: {e}", file=sys.stderr)

    return dict(created=created, avatar=d["avatarUrl"],
                followers=d["followers"]["totalCount"],
                repos=d["repositories"]["totalCount"], stars=stars,
                commits=commits, added=added, deleted=deleted)


def uptime(created):
    today = dt.datetime.now(dt.timezone.utc).date()
    start = created.date()
    y, m, d = today.year - start.year, today.month - start.month, today.day - start.day
    if d < 0:
        m -= 1
        d += ((today.replace(day=1) - dt.timedelta(days=1)).day)
    if m < 0:
        y, m = y - 1, m + 12
    plural = lambda n, w: f"{n} {w}{'' if n == 1 else 's'}"
    return ", ".join([plural(y, "year"), plural(m, "month"), plural(d, "day")])


def ascii_art(img, invert):
    """Square photo -> ROWS lines of COLS characters."""
    img = ImageOps.autocontrast(ImageOps.fit(img.convert("L"), (400, 400)), cutoff=2)
    img = img.resize((COLS, ROWS), Image.LANCZOS)
    px = img.load()
    lines = []
    for y in range(ROWS):
        row = ""
        for x in range(COLS):
            v = px[x, y] / 255
            if invert:                       # light theme: dark ink on pale paper
                v = 1 - v
            row += RAMP[min(len(RAMP) - 1, int(v * len(RAMP)))]
        lines.append(row)
    return lines


def build_lines(s):
    """Returns a list of ('rule', title) / ('kv', key, value) / ('blank',)."""
    out = [("rule", PROMPT)]
    for item in INFO:
        if item is None:
            out.append(("blank",))
        elif item[1]:
            out.append(("kv", item[0], item[1].format(uptime=uptime(s["created"]))))
    contact = [("kv", k, v) for k, v in CONTACT if v]
    if contact:
        out += [("blank",), ("rule", "- Contact")] + contact
    out += [("blank",), ("rule", "- GitHub Stats"),
            ("kv", "Repos", f"{s['repos']:,}"),
            ("kv", "Stars", f"{s['stars']:,}"),
            ("kv", "Commits", f"{s['commits']:,}"),
            ("kv", "Followers", f"{s['followers']:,}")]
    if s["added"] or s["deleted"]:
        out.append(("kv", "Lines of Code",
                    f"{s['added'] - s['deleted']:,} (+{s['added']:,}, -{s['deleted']:,})"))
    return out


def render(theme, art, lines):
    t = THEMES[theme]
    pad, gap = 20, 24
    right_x = pad + COLS * CW + gap
    width = int(right_x + WIDTH * CW + pad)
    height = max(len(lines), ROWS) * LH + 2 * pad
    art_top = (height - ROWS * LH) / 2
    txt_top = (height - len(lines) * LH) / 2

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
           f'viewBox="0 0 {width} {height}" font-family="Consolas, \'DejaVu Sans Mono\', '
           f'\'Courier New\', monospace" font-size="{FS}px">',
           '<style>text{white-space:pre}</style>',
           f'<rect width="{width}" height="{height}" rx="14" fill="{t["bg"]}"/>',
           f'<g fill="{t["fg"]}">']
    for i, row in enumerate(art):
        svg.append(f'<text x="{pad}" y="{art_top + (i + .75) * LH:.1f}" '
                   f'textLength="{COLS * CW:.1f}" xml:space="preserve">{escape(row)}</text>')
    svg.append('</g>')

    for i, line in enumerate(lines):
        if line[0] == "blank":
            continue
        y = f"{txt_top + (i + .75) * LH:.1f}"
        if line[0] == "rule":
            title = line[1] + " "
            body = (f'<tspan fill="{t["fg"]}">{escape(title)}</tspan>'
                    f'<tspan fill="{t["dot"]}">{"-" * (WIDTH - len(title))}</tspan>')
        else:
            _, key, val = line
            val = val if len(key) + len(val) + 4 <= WIDTH else val[:WIDTH - len(key) - 5] + "…"
            dots = "." * (WIDTH - len(key) - len(val) - 3)
            body = (f'<tspan fill="{t["key"]}">{escape(key)}</tspan>'
                    f'<tspan fill="{t["fg"]}">:</tspan>'
                    f'<tspan fill="{t["dot"]}"> {dots} </tspan>'
                    f'<tspan fill="{t["val"]}">{escape(val)}</tspan>')
        svg.append(f'<text x="{right_x:.1f}" y="{y}" textLength="{WIDTH * CW:.1f}" '
                   f'xml:space="preserve">{body}</text>')
    svg.append('</svg>')
    return "\n".join(svg)


def main():
    if len(sys.argv) > 2 and sys.argv[1] == "--demo":      # local preview only
        img = Image.open(sys.argv[2])
        s = dict(created=dt.datetime(2023, 7, 1, tzinfo=dt.timezone.utc), repos=0,
                 stars=0, commits=0, followers=0, added=0, deleted=0)
    else:
        if not TOKEN:
            sys.exit("GH_TOKEN is not set")
        s = fetch_stats()
        with urllib.request.urlopen(s["avatar"], timeout=30) as r:
            img = Image.open(io.BytesIO(r.read()))
        print({k: v for k, v in s.items() if k != "avatar"})
    if img.mode in ("RGBA", "LA", "P"):                    # flatten transparency
        img = img.convert("RGBA")
        img = Image.alpha_composite(Image.new("RGBA", img.size, "white"), img)
    lines = build_lines(s)
    for theme in THEMES:
        art = ascii_art(img, invert=(theme == "light"))
        with open(f"{theme}_mode.svg", "w", encoding="utf-8") as f:
            f.write(render(theme, art, lines))
    print("wrote dark_mode.svg and light_mode.svg")


if __name__ == "__main__":
    main()
