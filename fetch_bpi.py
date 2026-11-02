import json
import csv
import urllib.request

base_url = "https://site.web.api.espn.com/apis/fitt/v3/sports/basketball/mens-college-basketball/powerindex?limit=400"
resume_url = "https://site.web.api.espn.com/apis/fitt/v3/sports/basketball/mens-college-basketball/powerindex?limit=400&view=resume"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def fetch_json(url):
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return {}

data_base = fetch_json(base_url)
data_resume = fetch_json(resume_url)

teams_dict = {}

# 1. Base BPI
for entry in data_base.get("teams", []):
    t_name = entry.get("team", {}).get("displayName", "")
    if not t_name: continue
    if t_name not in teams_dict:
        teams_dict[t_name] = {"bpi_rank": "", "bpi": "", "sor": ""}
    for s in entry.get("stats", []):
        name = str(s.get("name", "")).lower()
        val = s.get("displayValue") if s.get("displayValue") is not None else s.get("value", "")
        if name in ["bpirank", "rank", "bpi_rank"]: teams_dict[t_name]["bpi_rank"] = val
        elif name in ["bpi", "bpirating"]: teams_dict[t_name]["bpi"] = val

# 2. Resume SOR
resume_entries = data_resume.get("teams", [])
print(f"DEBUG: Found {len(resume_entries)} teams in resume endpoint response.")

for entry in resume_entries:
    t_name = entry.get("team", {}).get("displayName", "")
    if not t_name: continue
    if t_name not in teams_dict:
        teams_dict[t_name] = {"bpi_rank": "", "bpi": "", "sor": ""}
    
    stats = entry.get("stats", [])
    # Print sample stats for Notre Dame or Villanova to debug
    if "Notre Dame" in t_name or "Villanova" in t_name:
        print(f"DEBUG {t_name} stats in resume API:", stats)

    for s in stats:
        name = str(s.get("name", "")).lower()
        val = s.get("displayValue") if s.get("displayValue") is not None else s.get("value", "")
        if "sor" in name or "resume" in name:
            if val not in ["--", None]:
                teams_dict[t_name]["sor"] = val

rows = [["Rank", "Team", "BPI", "SOR"]]
sor_count = 0
for team_name, vals in teams_dict.items():
    rows.append([vals["bpi_rank"], team_name, vals["bpi"], vals["sor"]])
    if vals["sor"]:
        sor_count += 1

print(f"DEBUG: Total teams with non-empty SOR values: {sor_count}")

with open("bpi_rankings.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerows(rows)
