"""Builds dark_mode.svg and light_mode.svg for the GitHub profile README.

Edit the INFO list below to change what the card says, then run:

    python generate.py

In GitHub Actions the script also pulls live stats (repos, stars, commits,
followers) from the GitHub API. Without network access it reuses stats.json.
"""
import json
import os
import urllib.request
from xml.sax.saxutils import escape

USER = "Aishwaryasrivastav31"
TITLE = "aishwarya@srivastav"

# ("key", "value") -> dotted line   |   "- Heading" -> section rule   |   "" -> gap
INFO = [
    ("Role", "ML · Deep Learning · Explainable AI"),
    ("Degree", "BCA, Data Science & Machine Learning (2025)"),
    ("College", "Banarsidas Chandiwala Inst. of Technology"),
    ("University", "Guru Gobind Singh Indraprastha University"),
    ("Location", "New Delhi, India"),
    "",
    ("Languages.Code", "Python, SQL"),
    ("Languages.Real", "Hindi, English"),
    ("Stack.ML", "PyTorch, scikit-learn, Pandas, LightGBM"),
    ("Stack.XAI", "SHAP, DiCE, Evidently AI, RAG, MLflow, DVC"),
    ("Stack.Deploy", "Docker, FastAPI, Streamlit, Tableau, Git"),
    ("Daily.Drivers", "Claude, VS Code, Jupyter, Colab"),
    "",
    ("Research.Focus", "Explainable AI for regulated domains"),
    ("Research.Also", "RAG pipelines, gaps in ML / LLM systems"),
    ("Project", "Explainable Loan Decision Copilot"),
    ("Publication", "Snowflake in Data Science (GeeksforGeeks)"),
    ("Book.Chapter", "Speech Emotion Recognition (in progress)"),
    ("Badge", "HackerRank SQL, 5-Star Gold"),
    "",
    "- Contact",
    ("Email", "srivastavaishwarya93@gmail.com"),
    ("LinkedIn", "aishwarya-srivastav"),
    ("GitHub", USER),
    "",
    "- GitHub Stats",
    "STATS",
]

THEMES = {
    "dark":  dict(bg="#161b22", text="#c9d1d9", key="#ffa657", value="#a5d6ff",
                  dots="#616e7f", art="#c9d1d9"),
    "light": dict(bg="#f6f8fa", text="#24292f", key="#953800", value="#0a3069",
                  dots="#8c959f", art="#24292f"),
}

# Geometry. Every line gets an explicit textLength, so the layout is identical
# whichever monospace font the viewer's machine ends up using.
PAD = 22
ART_FS, ART_CW, ART_LH = 9.2, 5.5, 11.0
FS, CW, LH = 13, 7.8, 19
WIDTH_CH = 60                      # characters per info line
GAP = 30
FONT = "Consolas, 'DejaVu Sans Mono', Menlo, 'Courier New', monospace"


def api(path):
    req = urllib.request.Request("https://api.github.com/" + path)
    req.add_header("Accept", "application/vnd.github+json")
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def fetch_stats():
    user = api(f"users/{USER}")
    repos, page = [], 1
    while True:
        batch = api(f"users/{USER}/repos?per_page=100&type=owner&page={page}")
        repos += batch
        if len(batch) < 100:
            break
        page += 1
    commits = api(f"search/commits?q=author:{USER}&per_page=1")["total_count"]
    return {
        "repos": user["public_repos"],
        "followers": user["followers"],
        "stars": sum(r["stargazers_count"] for r in repos),
        "commits": commits,
    }


def load_stats():
    here = os.path.dirname(os.path.abspath(__file__))
    cache = os.path.join(here, "stats.json")
    try:
        stats = fetch_stats()
        json.dump(stats, open(cache, "w"), indent=2)
        print("stats refreshed:", stats)
    except Exception as e:                       # offline, rate-limited, ...
        print("could not reach GitHub, using stats.json:", e)
        stats = json.load(open(cache)) if os.path.exists(cache) else {}
    return {k: f"{stats[k]:,}" if k in stats else "-"
            for k in ("repos", "followers", "stars", "commits")}


def kv(key, value, width=WIDTH_CH):
    """'. Key: ....... value' padded with dots to exactly `width` chars."""
    dots = width - len(key) - len(value) - 5
    if dots < 2:
        raise ValueError(f"line too long, shorten it: {key}: {value}")
    return [("text", ". "), ("key", key), ("text", ":"),
            ("dots", " " + "." * dots + " "), ("value", value)], width


def pair(k1, v1, k2, v2):
    half = (WIDTH_CH - 1) // 2
    a, _ = kv(k1, v1, half)
    b, _ = kv(k2, v2, WIDTH_CH - 1 - half)          # its ". " prefix is dropped
    return a + [("text", " | ")] + b[1:], WIDTH_CH


def build_lines(stats):
    lines = [([("text", TITLE + " "), ("text", "─" * (WIDTH_CH - len(TITLE) - 1))],
              WIDTH_CH)]
    for item in INFO:
        if item == "":
            lines.append(None)
        elif item == "STATS":
            lines.append(pair("Repos", stats["repos"], "Stars", stats["stars"]))
            lines.append(pair("Commits", stats["commits"],
                              "Followers", stats["followers"]))
        elif isinstance(item, str):
            head = item + " "
            lines.append(([("text", head + "─" * (WIDTH_CH - len(head)))], WIDTH_CH))
        else:
            lines.append(kv(*item))
    return lines


def render(theme, art, lines):
    c = THEMES[theme]
    art_cols = max(len(l) for l in art)
    art_w, art_h = art_cols * ART_CW, len(art) * ART_LH
    info_w, info_h = WIDTH_CH * CW, len(lines) * LH
    W = round(PAD + art_w + GAP + info_w + PAD)
    H = round(max(art_h, info_h) + 2 * PAD)
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" font-family="{FONT}" role="img" '
        f'aria-label="Aishwarya Srivastav: profile card">',
        "<style>text{white-space:pre}"
        + "".join(f".{k}{{fill:{c[k]}}}" for k in ("text", "key", "value", "dots"))
        + "</style>",
        f'<rect width="{W}" height="{H}" rx="15" fill="{c["bg"]}"/>',
        f'<g font-size="{ART_FS}" fill="{c["art"]}">',
    ]
    y0 = (H - art_h) / 2 + ART_FS * 0.8
    for i, line in enumerate(art):
        body = line.lstrip(" ")
        if not body:
            continue
        x = PAD + (len(line) - len(body)) * ART_CW
        out.append(f'<text x="{x:.1f}" y="{y0 + i * ART_LH:.1f}" xml:space="preserve" '
                   f'textLength="{len(body) * ART_CW:.1f}">{escape(body)}</text>')
    out.append("</g>")
    out.append(f'<g font-size="{FS}">')
    x = PAD + art_w + GAP
    y0 = (H - info_h) / 2 + FS
    for i, line in enumerate(lines):
        if line is None:
            continue
        spans, n = line
        inner = "".join(f'<tspan class="{cls}">{escape(t)}</tspan>' for cls, t in spans)
        out.append(f'<text x="{x:.1f}" y="{y0 + i * LH:.1f}" xml:space="preserve" '
                   f'textLength="{n * CW:.1f}">{inner}</text>')
    out.append("</g></svg>")
    return "\n".join(out) + "\n"


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    lines = build_lines(load_stats())
    for theme in THEMES:
        art = open(os.path.join(here, f"ascii_{theme}.txt")).read().rstrip("\n").split("\n")
        with open(os.path.join(here, f"{theme}_mode.svg"), "w") as f:
            f.write(render(theme, art, lines))
        print("wrote", f"{theme}_mode.svg")


if __name__ == "__main__":
    main()
