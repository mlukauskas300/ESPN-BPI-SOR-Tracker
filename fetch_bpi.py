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

    for entry in entries:
        team_info = entry.get("team", {})
        team_name = team_info.get("displayName") or team_info.get("name") or team_info.get("abbreviation") or ""
        
        bpi_rank = ""
        bpi_val = ""
        sor_val = ""

        # ESPN nests metrics inside category stats
        for cat in entry.get("categories", []):
            for s in cat.get("stats", []):
                name = str(s.get("name", "")).lower()
                abbr = str(s.get("abbreviation", "")).lower()
                val = s.get("displayValue") if s.get("displayValue") is not None else s.get("value", "")

                # Match BPI Rank
                if name in ["bpirank", "rank", "bpi_rank"] or abbr in ["bpi rk", "bpi rank"]:
                    bpi_rank = val
                # Match BPI Rating
                elif name in ["bpi", "bpirating"] or abbr == "bpi":
                    bpi_val = val
                # Match SOR Rank / Strength of Record
                elif any(k in name for k in ["sor", "strengthofrecord", "resume"]) or any(k in abbr for k in ["sor", "res"]):
                    if val not in ["--", None, ""]:
                        sor_val = val

        if team_name:
            rows.append([bpi_rank, team_name, bpi_val, sor_val])

    with open("bpi_rankings.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    print(f"Successfully processed and wrote {len(rows) - 1} teams to bpi_rankings.csv")

except Exception as e:
    print(f"Error fetching ESPN data: {e}")
