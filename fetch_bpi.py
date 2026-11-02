import json
import csv
import re
import urllib.request

url = "https://site.web.api.espn.com/apis/fitt/v3/sports/basketball/mens-college-basketball/powerindex?limit=400"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

req = urllib.request.Request(url, headers=headers)

def clean_rank(val):
    if val is None:
        return ""
    # Convert to string and strip ordinal suffixes (st, nd, rd, th)
    s = str(val).strip()
    cleaned = re.sub(r'(st|nd|rd|th)$', '', s, flags=re.IGNORECASE)
    return cleaned if cleaned not in ["-", ""] else ""

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
            ranks = cat.get("ranks", [])
            values = cat.get("values", [])
            
            # Category 0 is 'bpi'
            if cat_name == "bpi":
                if len(ranks) > 0:
                    bpi_rank = clean_rank(ranks[0])
                if len(values) > 0 and values[0] is not None:
                    bpi_val = values[0] # This is the BPI rating (e.g. 23.14)
            
            # Category 1 is 'resume' (contains Strength of Record / SOR)
            elif cat_name == "resume":
                for r in ranks:
                    cleaned_r = clean_rank(r)
                    if cleaned_r:
                        sor_val = cleaned_r
                        break
                if not sor_val:
                    for v in values:
                        if v not in ["-", None, ""]:
                            sor_val = str(v).strip()
                            break

        rows.append([bpi_rank, team_name, bpi_val, sor_val])

    with open("bpi_rankings.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    print(f"Successfully processed and wrote {len(rows) - 1} teams to bpi_rankings.csv")

except Exception as e:
    print(f"Error fetching ESPN data: {e}")
