import os
import json
import requests

IMAGES_DIR = "images"
COVERS_JSON = "docs/covers.json"
REQUESTS_JSON = "docs/replace_requests.json"

os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs("docs", exist_ok=True)

# Load existing covers
with open(COVERS_JSON, "r", encoding="utf-8") as f:
    covers = json.load(f)

# Load replacement requests
if os.path.exists(REQUESTS_JSON):
    with open(REQUESTS_JSON, "r", encoding="utf-8") as f:
        requests_list = json.load(f)
else:
    requests_list = []

if not requests_list:
    print("No replacement requests found.")
    exit(0)

for req in requests_list:
    title = req["title"]
    new_url = req["url"]
    # Find the cover entry
    for cover in covers:
        if cover["title"] == title:
            # Download new image
            filename = os.path.basename(cover["url"])
            local_path = os.path.join(IMAGES_DIR, filename)
            try:
                img_data = requests.get(new_url).content
                with open(local_path, "wb") as f:
                    f.write(img_data)
                cover["url"] = new_url
                print(f"Updated cover for {title}")
            except Exception as e:
                print(f"Failed to update {title}: {e}")

# Save updated covers.json
with open(COVERS_JSON, "w", encoding="utf-8") as f:
    json.dump(covers, f, ensure_ascii=False, indent=2)

# Clear requests
with open(REQUESTS_JSON, "w", encoding="utf-8") as f:
    json.dump([], f)
