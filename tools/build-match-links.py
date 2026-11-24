"""Publish static Open Graph pages for JFL matches and player profiles."""
import os
import base64
import json
import re
from datetime import date
from hashlib import sha256
from html import escape
from pathlib import Path
from urllib.parse import quote, urlencode, urljoin, urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "matches"
source = (ROOT / "index.html").read_text()
site_url = os.getenv("JFL_PAGES_URL", "").strip().rstrip("/")
if not site_url:
    owner, repo = os.getenv("GITHUB_REPOSITORY", "somebasicgoats/JFL").split("/", 1)
    site_url = f"https://{owner}.github.io/" + ("" if repo.lower() == f"{owner.lower()}.github.io" else repo)
site_url = site_url.rstrip("/") + "/"
url, key = re.search(r'SUPABASE_URL="([^"]+)",SUPABASE_KEY="([^"]+)"', source).groups()


def fetch(table, **params):
    rows = []
    while True:
        endpoint = url + "/rest/v1/" + table + "?" + urlencode({
            **params, "limit": 500, "offset": len(rows),
        })
        with urlopen(Request(endpoint, headers={"apikey": key}), timeout=45) as response:
            batch = json.load(response)
        rows.extend(batch)
        if len(batch) < 500:
            return rows


def normal(name):
    return " ".join(name.lower().split())


def score(teams, side):
    def total(team, field):
        return sum(int(p.get(field) or 0) for p in team["players"])
    return total(teams[side], "g") + total(teams[1-side], "o")


def write_page(filename, title, description, fragment, image=None):
    target = "../#" + fragment
    page_url = urljoin(site_url, "matches/" + filename)
    if image and image.startswith("data:image/webp;base64,"):
        asset = filename.removesuffix(".html") + ".webp"
        (OUT / asset).write_bytes(base64.b64decode(image.split(",", 1)[1], validate=True))
        image = urljoin(site_url, "matches/" + asset)
    if not image or urlparse(image).scheme != "https":
        image = urljoin(site_url, "matches/jfl-preview.png")
    image_meta = f'<meta property="og:image" content="{escape(image, quote=True)}">' 
    (OUT / filename).write_text(f'''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)} · {escape(league_name)}</title><meta property="og:type" content="website">
<link rel="canonical" href="{escape(page_url, quote=True)}">
<meta property="og:url" content="{escape(page_url, quote=True)}">
<meta property="og:site_name" content="{escape(league_name, quote=True)}">
<meta property="og:title" content="{escape(title, quote=True)}">
<meta property="og:description" content="{escape(description, quote=True)}">
<meta name="theme-color" content="#FFE033">
<meta name="twitter:card" content="summary">{image_meta}
</head><body><h1>{escape(title)}</h1><p>{escape(description)}</p>
<a href="{escape(target, quote=True)}">Open on JFL</a><script>location.replace({json.dumps(target)})</script></body></html>''', encoding="utf-8")


settings = {r["key"]: r["value"] for r in fetch(
    "settings", select="key,value", order="key"
)}
players = {r["name_key"]: r for r in fetch("players", select="name_key,name,first,last", order="name_key")}
names = settings.get("team_names") or {}
league_name = settings.get("league-name") or "New Korp FC League"
roster = {}
previews = {"match": {}, "player": {}}
OUT.mkdir(exist_ok=True)
logo = re.search(r'<div class="brand"><img [^>]*src="data:image/png;base64,([^"]+)"', source)
if logo:
    (OUT / "jfl-preview.png").write_bytes(base64.b64decode(logo.group(1), validate=True))
for game in fetch("games", select="*", order="date.asc,ts.asc.nullsfirst,id.asc"):
    teams = game.get("teams") or []
    if len(teams) != 2:
        continue
    for team in teams:
        for player in team["players"]:
            if player.get("n") and normal(player["n"]) != "n/a":
                roster[normal(player["n"])] = player["n"]
    day = date.fromisoformat(game["date"])
    game_id = str(game["id"])
    label = [t.get("label") or names.get(t["name"], t["name"]) for t in teams]
    title = f'{label[0]} {score(teams,0)}–{score(teams,1)} {label[1]}'
    kind = "Interlevel" if game["type"] == "vs" else "Sec 5"
    filename = "match-" + sha256(game_id.encode()).hexdigest()[:24] + ".html"
    write_page(filename, title, f'{day:%b %d, %Y} · {kind} · Goal timeline and box score', "match/" + quote(game_id, safe=""))
    previews["match"][game_id] = "matches/" + filename
for profile in fetch("profiles", select="name", order="name"):
    name = profile.get("name")
    if name:
        roster[normal(name)] = name
for player_key, player in players.items():
    roster[player_key] = player["name"]
for player_key, name in roster.items():
    player = players.get(player_key) or {}
    full = f'{player["first"]} {player["last"]}' if player.get("first") and player.get("last") else name
    filename = "player-" + sha256(player_key.encode()).hexdigest()[:24] + ".html"
    write_page(filename, full, f"Season stats, game log and awards · {league_name}", "player/" + quote(player_key, safe=""), settings.get("photo:" + player_key))
    previews["player"][player_key] = "matches/" + filename
(OUT / "published.js").write_text("window.jflPreviews="+json.dumps(previews, sort_keys=True)+";\n", encoding="utf-8")
print(f'Generated {len(previews["match"])} match and {len(previews["player"])} player previews')
