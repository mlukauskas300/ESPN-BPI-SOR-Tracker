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
        team_name = team_info.get("displayName") or team_info.get("name") or ""
        if not team_name:
            continue

        bpi_rank = ""
        bpi_val = ""
        sor_val = ""

        for cat in entry.get("categories", []):
            cat_name = str(cat.get("name", "")).lower()
            cat_display = str(cat.get("displayName", "")).lower()
            
            # Check ranks or values maps
            ranks = cat.get("ranks", {})
            values = cat.get("values", {})
            
            # If this category relates to overall power index / BPI
            if "bpi" in cat_name or "powerindex" in cat_name or "overall" in cat_name:
                if "bpirank" in ranks:
                    bpi_rank = ranks["bpirank"]
                elif "rank" in ranks:
                    bpi_rank = ranks["rank"]
                
                if "bpi" in values:
                    bpi_val = values["bpi"]
                elif "rating" in values:
                    bpi_val = values["rating"]

            # If this category relates to resume / strength of record
            if "resume" in cat_name or "sor" in cat_name or "strengthofrecord" in cat_name or "resume" in cat_display:
                if "strengthofrecord" in ranks:
                    sor_val = ranks["strengthofrecord"]
                elif "sor" in ranks:
                    sor_val = ranks["sor"]
                elif "rank" in ranks:
                    sor_val = ranks["rank"]
                elif "strengthofrecord" in values:
                    sor_val = values["strengthofrecord"]
                elif "sor" in values:
                    sor_val = values["sor"]

        rows.append([bpi_rank, team_name, bpi_val, sor_val])

    with open("bpi_rankings.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    print(f"Successfully processed and wrote {len(rows) - 1} teams to bpi_rankings.csv")

except Exception as e:
    print(f"Error fetching ESPN data: {e}")
