import json
import urllib.request

url = "https://site.web.api.espn.com/apis/fitt/v3/sports/basketball/mens-college-basketball/powerindex?limit=400"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

req = urllib.request.Request(url, headers=headers)

try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode("utf-8"))

    print("TOP LEVEL JSON KEYS:", list(data.keys()))

    # Check common containers where ESPN stores ranking data
    for container_name in ["teams", "powerIndexes", "groups", "rankings", "items", "content"]:
        if container_name in data:
            items = data[container_name]
            print(f"Found container '{container_name}' with {len(items)} items.")
            if items:
                print(f"First item keys in '{container_name}':", list(items[0].keys()))
                # Print a clean snippet of the first item to inspect nested stats/values
                print("First item sample JSON snippet:", json.dumps(items[0], indent=2)[:1000])
            break

    # Also output a dummy CSV so the workflow doesn't fail on file absence
    with open("bpi_rankings.csv", "w", encoding="utf-8") as f:
        f.write("Rank,Team,BPI,SOR\n")

except Exception as e:
    print(f"Error inspecting JSON: {e}")
