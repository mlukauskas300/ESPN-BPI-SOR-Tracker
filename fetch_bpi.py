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

    for i, entry in enumerate(entries):
        team_info = entry.get("team", {})
        team_name = team_info.get("displayName", "")
        
        bpi_rank = ""
        bpi_val = ""
        sor_val = ""

        all_stats = []
        for cat in entry.get("categories", []):
            for s in cat.get("stats", []):
                name = s.get("name", "")
                disp = s.get("displayValue", "")
                all_stats.append(f"{name}={disp}")
                
                # Broad capture logic
                lower_name = name.lower()
                if lower_name in ["bpi", "bpirating"]:
                    bpi_val = disp
                elif lower_name in ["bpirank", "bpi_rank", "rank"]:
                    bpi_rank = disp
                elif "strengthofrecord" in lower_name or lower_name == "sor" or "resume" in lower_name:
                    if disp not in ["--", None, ""]:
                        sor_val = disp

        # Print stats for the first 3 teams to the GitHub Actions logs so we can read them
        if i < 3 and team_name:
            print(f"DEBUG STATS FOR {team_name}: {all_stats}")

        if team_name:
            rows.append([bpi_rank, team_name, bpi_val, sor_val])

    with open("bpi_rankings.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    print(f"Successfully processed {len(rows) - 1} teams.")

except Exception as e:
    print(f"Error fetching data: {e}")
