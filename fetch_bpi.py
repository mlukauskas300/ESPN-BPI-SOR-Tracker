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

        # Loop through categories
        for cat in entry.get("categories", []):
            cat_name = str(cat.get("name", "")).lower()
            
            # Inspect ranks, values, and totals dictionaries
            ranks = cat.get("ranks", {})
            values = cat.get("values", {})
            totals = cat.get("totals", {})
            
            # Merge dictionaries to check all stored stat key-value pairs
            combined_stats = {}
            if isinstance(ranks, dict): combined_stats.update(ranks)
            if isinstance(values, dict): combined_stats.update(values)
            if isinstance(totals, dict): combined_stats.update(totals)
            
            for key, val in combined_stats.items():
                k_lower = str(key).lower()
                v_str = str(val) if val is not None else ""
                
                # Capture BPI Rank
                if k_lower in ["bpirank", "bpi_rank", "rank"] and "bpi" in cat_name:
                    bpi_rank = v_str
                # Capture BPI Rating
                elif k_lower in ["bpi", "rating", "bpi_rating"] and "bpi" in cat_name:
                    bpi_val = v_str
                # Capture SOR Rank
                elif k_lower in ["sor", "strengthofrecord", "sor_rank"] or ("sor" in cat_name and k_lower == "rank"):
                    if v_str not in ["--", None, ""]:
                        sor_val = v_str

        rows.append([bpi_rank, team_name, bpi_val, sor_val])

    with open("bpi_rankings.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    print(f"Successfully wrote {len(rows) - 1} teams to bpi_rankings.csv")

except Exception as e:
    print(f"Error processing ESPN data: {e}")
