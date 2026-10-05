#!/usr/bin/env python3
"""Builds dark_mode.svg and light_mode.svg for the GitHub profile README.

Uses only the Python standard library.

Runs inside GitHub Actions (see .github/workflows/update.yml).
Edit the INFO block below to change what the card says.
"""
import datetime as dt
import json
import os
import sys
import time
import urllib.request
from xml.sax.saxutils import escape


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

COLS, ROWS = 90, 45          # ASCII art size in characters
ACW, ALH, AFS = 4.8, 9.6, 8  # ASCII art char width, line height, font size (px)
WIDTH = 56                   # info column width in characters
CW, LH, FS = 9.6, 20, 16     # info char width, line height, font size (px)
THEMES = {
    "dark":  dict(bg="#161b22", fg="#c9d1d9", key="#ffa657", val="#a5d6ff", dot="#616e7f"),
    "light": dict(bg="#f6f8fa", fg="#24292f", key="#953800", val="#0a3069", dot="#b6c2d0"),
}
API = "https://api.github.com"
TOKEN = os.environ.get("GH_TOKEN", "")


# ASCII portrait, made once from the profile photo (one version per theme).
ART = {
"dark": [
    '                                                                                          ',
    '                                      .:;***;;:                                           ',
    '                                 .:*ll*;;**;;***;**;::                                    ',
    '                              .*JJl*;:..::;*;;lJ*;:;::;:                                  ',
    '                            :oJJll**;::::::::*Jol*::::::;.                                ',
    '                           *oJJl*l**;;:..::;*lJoJl*;:...::;                               ',
    '                         :ooJJll**ll;:::;*lJoo&&XXoll*::..:;                              ',
    '                        looJJJllll*::::*JoXXX&&&&X&Xool*:..:;                             ',
    '                       JoJJJl*lll;..;*JXX&&&&&&&&&X&XXoJ*::.:;                            ',
    '                      lJJll*lll*;::*JoX&Q&&QQQ&&X&XXXXXoJl;.::                            ',
    '                     .Jl*******;;*loX&QQQQQQ&&&&&XXXXXXXool:.::                           ',
    '                     J***;;*****JJooXQQ@QQQQQQ&&X&&&&&XXXoJ;.::                           ',
    '                    ;l**;;;;lJllllll**lJoX&Q&&&&XXXXXXXXX&o*.:.                           ',
    '                   .ll*l**;loJlX&XX&XoJlllloX&&XoJl*;;***lol.:.                           ',
    '                   .l&ol*:lXolXoJooJJJJllJX&&&XXJl**llJJooo*.:                            ',
    '                   ;JXol*loJlJoJl**;::****oQ@QQXJ*;;;;;*lJoJ::                            ',
    '                  :loXXoJJJJJXXooooJlllllJXQ@@Q&l*;;::****JJ;:                            ',
    '                  *lJX&JJlJo&&QQ&&XXXoXXXQQQ@QQQoJlllllJooXol                             ',
    '                 *lJll&oloXQQ@@QQQQ&&&&&&QQQQ@Q&&&XXooXoXX&Xl                             ',
    '                .*ll*lJJXQQ@@@@@QQ&&XXoJo&QQ@QQQ&oJoXX&&QQQQ*                             ',
    '                *lll**oloQQ@Q@QQ&&XXJJJJQQ&QQ&&X&XlJJoXX&QQ&.                             ',
    '               *ll**;;Jl:X@QQQ&&XXolloXXXJJXXJJllJl*lJooXX&J*                             ',
    '              :*ll**:.:;;lQ@QQ&&Xo*lo&Q&&XXJJlJJooJ**lJJoXJ:;:                            ',
    '             .llll;;:.:;*:oQQ&Q&Xo*;**ooJllllllllJl*;llJoJ;.;:                            ',
    '               *ll;.:.:;;::o&&&&XoJooJloXXXXXXool;;;;lJoJ;..**.                           ',
    '              .Jl*:;*:.;;::.lX&&XXXXXXXXoJJJllJJJJJJlJJJ:..:.*l:                          ',
    '              lJ*;:*:::;:;...loXX&&X&XXXoJll*l*lJooooJ;...:.::;**.. . ..                  ',
    '             .l**:::::::::...;JJooX&&&&XXXoJJJooooXJ*.......:.:;*lJoJJl*.                 ',
    '              l*:;::.:..:.:..:lJJJJJo&&&XXXXXXXXool:..........:::**llXl*.                 ',
    '             ;ol;:::::........*JJoJJJJJoXooooJJJl*;..............::::;*;;:.               ',
    '             ll*;::::...::....*JJoooooJJlll*l*l***:.......:..:.::.::;;;:;;*;*:.           ',
    '            :;:......::.:;;:.:;JJoooooJJJlllllll*:......:.....:::::::::;*lJJJo**..        ',
    '           .:.:;***;::::;*;::.;*JJoXooooJJJJJll*;::..........:.::::::::;;******llJJll;.   ',
    '          ...***;;*l*::;***;:::**lJooXoooooJJJl*;:...:...:......:::;;;;;*;;;;*lJJ&XQXJll*;',
    '  :;****;:::*l**loQ&oJ****;;*;:***lJooooooooJl**;;:..:..:.::.:..:;;;;:;;;***;**loXQQQQQQQ@',
    'JJoX&&QX&l**oQXXXQ@QoJ*;;;**;;;;*l*llooooXoXoJll*::...:.:::*:.:.::;;*;;;:;;l**l*oX&Q@@@@@@',
    'Q@@QQ@Q&QQ&&Q@Xo&Q@QXJl:;;;;*;;;;;llJloooXXooJoo*;:::.:::;:**:.:.:;*;*;;:.::;***J&&QQ@@@@@',
    'QQ@@QQ@&&@&&QQXoXQ@&oJJ;;;;;;;;;;;;llJJJoooooooQX*;::..::;:;;;:.:.:****;;:.::;;*JoX&QQ@@@@',
    '@QQ@@@&&QQQ&QQXXX@@&oool:::;;;:;;;:;;lJJJoooXo&@&ll**;;:;;**lJ*:.:::;*;*;;;:.::;;lJXXQQ@&&',
    '@QQQ@@&&QQX&@&X&Q@Q&ooool::::;;;;;;;*JXXXoJJo&QXoJoXXXXXXXXolJJ*::;:;;*;;;;:::::;*lJoooXQ@',
    '@@&&@QQ&Q&XQQ&&&Q@@&XooXo*:::;:;;*lo&QQQQXlo&&XXXo&&QQQQ&&X&Xlool*:;:::;*;;;:.:.:;*lo&&&Q@',
    'QQQX@@&&&&X@Q&&Q@@@&XXXXXXl***JoooXX&Q@&QXX&&&XXXQQQQQQQQQ&QQ&JJJJl*;:;::;;:;:.::;*lJoX&&Q',
    'QQQ&@Q&&XX&QQQQ@@@QQ&XX&&QQ&X&&QQ&XQQQ&QQQ&&&&&&Q@@@@@@@Q@QQQQ&oJJl*::;;:.:::.;:..;;llJXX&',
    'Q&&&QQ&&XX@QQQQ@@@@&Q&&&QQ@Q&&&QQ&&&Q&QQQ&&&&&&Q@@@@@@@@@@@@@@Q&XJl**;;;;...::.::.:;;lJJo&',
    '&&XX@&&XX&@QQQ@@@@QQQQQ@@@@QQ&&Q&Q&&Q&&QQQQ@QQ@@@@@@@@@@@@@@@@@Q&oJ**;;*;.:.:;:.:::.;:;lJo',
],
"light": [
    '                                                                                          ',
    '                                     .:;*:::...                                           ',
    '                                 :*JJoX&&XoX&XXXXXJ*:.                                    ',
    '                              .*lJoo&QQQQQXX&XJJX&&&QQX;                                  ',
    '                            ;lllJooX&QQ@QQQQ&XJlJXQQ&QQQX:                                ',
    '                          .*llJoXoooX&QQ@QQ&XJl*lJX&Q@@@Q&*                               ',
    '                         ;lllJJooooo&&QQ&oJll**;**lloX&Q@@Ql                              ',
    '                       .***llJJJJoX&QQ&oll**;;:;:;;**lJXQ@QQo                             ',
    '                       lllJJooJooX@QQoJ**;;::::;;;;;;**Jo&@QQ*                            ',
    '                      *lloJooJoo&Q&XJ*;;::::::;:;;;*;**llo&Q@&                            ',
    '                     :lJXXoXXoX&&XJl*;::.::::::;;**;**;**lJQ@Q;                           ',
    '                     lXXXX&XXoXXlll*;:...:..::;;;;;;;;;***l&@Q*                           ',
    '                    *oXX&X&XoJJJJJJoXooll;;:::;;;*;*;**;*;lXQQ;                           ',
    '                   :JooooX&J*JJ*;*;*;llJooJl;;;**JJX&X&XoJ*o@Q*                           ',
    '                   :J;*JXQo*lJ**JlllJlJJJl*;;:;*looooJJll*lo@Q                            ',
    '                   Jl*lJXJ*lJl*Jooo&Q&oXXol...:*JXX&&XXXJJlJQ.                            ',
    '                  lol;;lJlJJl****l*lJoJool*:...;JX&&QQXoXoll&.                            ',
    '                 .oJl*;llJll;::::;;*****;::...::*lJooJoJl**lJ                             ',
    '                 JoJJJ;lol;:....:.::;;;;;:.:...:;;;******;;;:                             ',
    '                *XJJoolJ;::.. ...:;;;*ll*;:..:::;ll***;:::.:.                             ',
    '               .oJooXo;Jl:.....:;;;*lJll:::.::;;;;Joll*;;:::                              ',
    '              .ooooo&&*o&;..:::;;*lJol;**lll*llooJJoJll**;;Jl                             ',
    '              *ooJo&&@QX&o..:::;*loo*;::;;*lJJJl**JoXJJl**lQX:                            ',
    '             .JJJoX&Q@QX&Q*:.::;;loXXol*JJJJJJooJJoXXoJJll&@&*                            ',
    '               ;Jo&QQQ@&X&Ql:::;;*JlllJ****;l**lJ&&&Xolll&@QXX:                           ',
    '              .JJXQXX@Q&XQQ@o;;;;**;**;*lllJJJlJllllJJlJQ@Q@QXo;                          ',
    '              *Jo&&XQ&QXQ&@@@o***;;;;;***loooooJll*llJX@@@Q@QQ&ol.   . .                  ',
    '              JoXQQQQQQ@&QQ@@&Jll**;;;;;**llllll***lX@@@@@@@QQQ&ooJllJJo.                 ',
    '              JX&&QQQ@@@Q@@@@QollJll*;;;;********lo&@@@@@@@@@@QQ&XooJ*Jo.                 ',
    '             .lo&Q&QQQQ@@@@@@@oJllllJll****llllJJXX@@@@@@@@@@@@@@QQQ&&X&J;.               ',
    '             *Jo&&QQQQ@@QQQ@@@oJll*llllJooooooooXX@@@@@@@@@@@Q@QQQQQ&&&&X&XXXJ.           ',
    '            *XQ@@@@@@@Q@Q&&Q@QXJl****lllJJJJJJooXQQ@@@@@@@@@@@QQQQQQQ&Q&XJJJlloJ:         ',
    '           lQ@QXXXoXQ&Q&&XX&@@&oJll***llllllJJoo&&Q@@@@@@Q@@@Q@QQ&QQQ&Q&&XoooXXoJJll;:    ',
    '          *@@XoX&XXoXQ&&oXX&&Q&XXolll**llllllJoX&&@@@@@@@@@@Q@@QQ&Q&X&&XXX&&&XJJl;;.*lJ*;;',
    '  ;*lJJoXQQQooXool::lJXXXXXX&&&XoooJ*l****lllJooX&Q@@Q@@QQQQ@@@@Q&&&&&&&XXXoXXoJ**::.:.:..',
    'Jll*;::;*JXol.**;:..*lo&XX&XXX&&XooJJlll****lJJoX&Q@@QQ@Q&QXQQQ@Q&&XXX&&Q&XoXoXol;::......',
    '....:..;:.;::.**;:..*Jo&&X&X&X&X&XoJJJl*l***lll*X&QQQ@QQ&&QXoQ@Q@QXXXX&&&@QQ&ooXJ;;:... . ',
    '.: ...:::.:;:.***..:*ll&&&&&&&&&&&&oJllll*****l:*o&QQQ@QQ&&&X&QQQ@QXXXXX&Q@QQ&&oJ*;;.... .',
    '.:....:;:.::.:**;..;*llJQ&&&&&&&&&&&XoJlllll**; ;JooX&&&&XXXoJXQ@QQQXXXX&&&QQQQ&Xol**:..::',
    ' ::: .::::;;.;;;:..;*l**oQQ&&&&&X&&XXl*;*llll;:;lll**;;*****olloQQ&&&&X&XX&&QQQQ&Xoll***:.',
    '..::..:;::*:.;;:...;**l**XQQQ&&&XXol;:.::;Jl::;***;::::::;;;;JlloX&&&Q&&X&X&&@Q@&&oo*;;;..',
    '..:;..;:;;;.::::. .:*****;JXXoJ****;:.::.**:;;;*;:...:.::.;:::lJllJX&Q&&Q&&Q&&@&Q&XJJl*;;:',
    ':::;..;:;*:.:::....:;;;;;:::;;:::;;:::::.::;:;;;:...........::;*JJJoQ&&&Q@Q&Q@&Q@Q&Xoll*;;',
    '::;;.:;;*;.::... ..:::;::..:;;::::;:.::::;::;:;: .. . . .... ..;;lJXX&&X&Q@@QQ@QQ@Q&&oJl*;',
    ';;;;.:;;;;..::.. ...:.... ..::::::;;::;..::.::. . .. .. . . ....;*JoX&XX&@QQQ&QQQQQQ&&Xol*',
],
}


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
    right_x = pad + COLS * ACW + gap
    width = int(right_x + WIDTH * CW + pad)
    height = int(max(len(lines) * LH, ROWS * ALH) + 2 * pad)
    art_top = (height - ROWS * ALH) / 2
    txt_top = (height - len(lines) * LH) / 2

    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
           f'viewBox="0 0 {width} {height}" font-family="Consolas, \'DejaVu Sans Mono\', '
           f'\'Courier New\', monospace" font-size="{FS}px">',
           '<style>text{white-space:pre}</style>',
           f'<rect width="{width}" height="{height}" rx="14" fill="{t["bg"]}"/>',
           f'<g fill="{t["fg"]}">']
    for i, row in enumerate(art):
        svg.append(f'<text x="{pad}" y="{art_top + (i + .8) * ALH:.1f}" font-size="{AFS}px" '
                   f'textLength="{COLS * ACW:.1f}" xml:space="preserve">{escape(row)}</text>')
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
    if "--demo" in sys.argv:                               # local preview only
        s = dict(created=dt.datetime(2023, 7, 1, tzinfo=dt.timezone.utc), repos=0,
                 stars=0, commits=0, followers=0, added=0, deleted=0)
    else:
        if not TOKEN:
            sys.exit("GH_TOKEN is not set")
        s = fetch_stats()
        print({k: v for k, v in s.items() if k != "avatar"})
    lines = build_lines(s)
    for theme in THEMES:
        with open(f"{theme}_mode.svg", "w", encoding="utf-8") as f:
            f.write(render(theme, ART[theme], lines))
    print("wrote dark_mode.svg and light_mode.svg")


if __name__ == "__main__":
    main()
