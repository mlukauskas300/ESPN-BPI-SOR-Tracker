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

try:
    data_base = fetch_json(base_url)
    data_resume = fetch_json(resume_url)

    teams_dict = {}

    # 1. Process Base API (BPI & BPI Rank)
    entries_base = data_base.get("teams", [])
    for entry in entries_base:
        t_info = entry.get("team", {})
        t_name = t_info.get("displayName") or t_info.get("name") or t_info.get("abbreviation") or ""
        if not t_name:
            continue

        if t_name not in teams_dict:
            teams_dict[t_name] = {"bpi_rank": "", "bpi": "", "sor": ""}

        for s in entry.get("stats", []):
            name = str(s.get("name", "")).lower()
            abbr = str(s.get("abbreviation", "")).lower()
            val = s.get("displayValue") if s.get("displayValue") is not None else s.get("value", "")

            if name in ["bpirank", "rank", "bpi_rank"] or abbr in ["bpi rk", "bpi rank"]:
                teams_dict[t_name]["bpi_rank"] = val
            elif name in ["bpi", "bpirating"] or abbr == "bpi":
                teams_dict[t_name]["bpi"] = val

    # 2. Process Resume API (SOR Rank)
    entries_resume = data_resume.get("teams", [])
    for entry in entries_resume:
        t_info = entry.get("team", {})
        t_name = t_info.get("displayName") or t_info.get("name") or t_info.get("abbreviation") or ""
        if not t_name:
            continue

        if t_name not in teams_dict:
            teams_dict[t_name] = {"bpi_rank": "", "bpi": "", "sor": ""}

        for s in entry.get("stats", []):
            name = str(s.get("name", "")).lower()
            abbr = str(s.get("abbreviation", "")).lower()
            val = s.get("displayValue") if s.get("displayValue") is not None else s.get("value", "")

            if any(k in name for k in ["sor", "resume"]) or any(k in abbr for k in ["sor", "res"]):
                if val not in ["--", None]:
                    teams_dict[t_name]["sor"] = val

    # Assemble rows
    rows = [["Rank", "Team", "BPI", "SOR"]]
    for team_name, vals in teams_dict.items():
        rows.append([vals["bpi_rank"], team_name, vals["bpi"], vals["sor"]])

    with open("bpi_rankings.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    print(f"Successfully merged and wrote {len(rows) - 1} teams to bpi_rankings.csv")

except Exception as e:
    print(f"Error processing data: {e}")
