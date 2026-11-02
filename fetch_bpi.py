import json
import csv
import urllib.request

# Updated ESPN Power Index endpoint
url = "https://site.web.api.espn.com/apis/fitt/v3/sports/basketball/mens-college-basketball/powerindex"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

req = urllib.request.Request(url, headers=headers)

try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode("utf-8"))

    rows = [["Rank", "Team", "BPI", "SOR"]]

    # Traverse nested groups or top-level powerIndexes
    groups = data.get("groups", [])
    entries = []
    
    if groups and isinstance(groups, list):
        entries = groups[0].get("standings", {}).get("entries", [])
    
    if not entries:
        entries = data.get("powerIndexes", [])

    for entry in entries:
        team_info = entry.get("team", {})
        team_name = team_info.get("displayName") or team_info.get("name") or team_info.get("abbreviation") or ""
        stats = entry.get("stats", [])
        
        bpi_rank = ""
        bpi_val = ""
        sor_val = ""

        for s in stats:
            name = s.get("name", "")
            val = s.get("value", s.get("displayValue", ""))
            
            if name in ["bpiRank", "rank", "bpi_rank"]:
                bpi_rank = val
            elif name in ["bpi", "bpiRating"]:
                bpi_val = val
            elif name in ["sor", "sorRank", "sor_rank"]:
                sor_val = val

        if team_name:
            rows.append([bpi_rank, team_name, bpi_val, sor_val])

    with open("bpi_rankings.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    print(f"Successfully wrote {len(rows) - 1} teams to bpi_rankings.csv")

except Exception as e:
    print(f"Error fetching ESPN data: {e}")
