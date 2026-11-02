import json
import urllib.request

url = "https://site.web.api.espn.com/apis/fitt/v3/sports/basketball/mens-college-basketball/powerindex?limit=400"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

req = urllib.request.Request(url, headers=headers)

try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode("utf-8"))

    entries = data.get("teams", [])
    if entries:
        first_team = entries[0]
        print("FIRST TEAM KEYS:", list(first_team.keys()))
        print("FIRST TEAM FULL JSON:", json.dumps(first_team, indent=2)[:1500])

    with open("bpi_rankings.csv", "w", encoding="utf-8") as f:
        f.write("Rank,Team,BPI,SOR\n")

except Exception as e:
    print(f"Error: {e}")
