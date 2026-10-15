import json
import csv
import urllib.request

url = "https://site.web.api.espn.com/apis/fitt/v3/sports/basketball/mens-college-basketball/powerindex"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

req = urllib.request.Request(url, headers=headers)

try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode("utf-8"))

    rows = [["Rank", "Team", "BPI", "SOR"]]
    
    entries = data.get("groups", [{}])[0].get("standings", {}).get("entries", [])
    if not entries:
        entries = data.get("powerIndexes", [])

    for entry in entries:
        team_name = entry.get("team", {}).get("displayName", "") or entry.get("team", {}).get("name", "")
        stats = entry.get("stats", [])
        
        bpi_rank = next((s["value"] for s in stats if s.get("name") in ["bpiRank", "rank"]), "")
        bpi = next((s["value"] for s in stats if s.get("name") == "bpi"), "")
        sor = next((s["value"] for s in stats if s.get("name") == "sor"), "")
        
        rows.append([bpi_rank, team_name, bpi, sor])

    with open("bpi_rankings.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    print("Successfully created bpi_rankings.csv")

except Exception as e:
    print(f"Error fetching ESPN data: {e}")
