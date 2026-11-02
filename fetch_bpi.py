import json
import csv
import urllib.request

url = "https://site.web.api.espn.com/apis/fitt/v3/sports/basketball/mens-college-basketball/powerindex?limit=400"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

req = urllib.request.Request(url, headers=headers)

try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode("utf-8"))

    rows = [["Rank", "Team", "BPI", "SOR"]]
    
    entries = data.get("teams", [])
    if not entries:
        entries = data.get("powerIndexes", []) or data.get("groups", [{}])[0].get("standings", {}).get("entries", [])

    # Print the available stat names from the first team that has stats for debugging
    for entry in entries:
        stats = entry.get("stats", [])
        if stats:
            print("Sample team stat keys found:", [s.get("name") for s in stats])
            break

    for entry in entries:
        team_info = entry.get("team", {})
        team_name = team_info.get("displayName") or team_info.get("name") or team_info.get("abbreviation") or ""
        
        stats = entry.get("stats", [])
        
        bpi_rank = ""
        bpi_val = ""
        sor_val = ""

        for s in stats:
            name = str(s.get("name", "")).lower()
            val = s.get("displayValue") if s.get("displayValue") is not None else s.get("value", "")
            
            if name in ["bpirank", "rank", "bpi_rank"]:
                bpi_rank = val
            elif name in ["bpi", "bpirating"]:
                bpi_val = val
            # Let's catch any stat name containing 'sor' or 'resume'
            elif "sor" in name or "resume" in name:
                sor_val = val

        if team_name:
            rows.append([bpi_rank, team_name, bpi_val, sor_val])

    with open("bpi_rankings.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    print(f"Successfully wrote {len(rows) - 1} teams to bpi_rankings.csv")

except Exception as e:
    print(f"Error fetching ESPN data: {e}")
