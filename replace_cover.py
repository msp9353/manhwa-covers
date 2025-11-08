import os
import json
import requests
from urllib.parse import urlparse

IMAGES_DIR = "images"
REQUESTS_FILE = "replace_requests.json"

def sanitize_filename(name):
    invalid = '<>:"/\\|?*'
    for ch in invalid:
        name = name.replace(ch, '')
    return name.strip()

if not os.path.exists(REQUESTS_FILE):
    print("No replace_requests.json found. Exiting.")
    exit(0)

with open(REQUESTS_FILE, "r", encoding="utf-8") as f:
    requests_list = json.load(f)

for req in requests_list:
    title = req.get("title")
    url = req.get("newUrl")
    if not title or not url:
        print(f"Skipping invalid request: {req}")
        continue

    filename = sanitize_filename(title) + ".jpg"
    filepath = os.path.join(IMAGES_DIR, filename)

    try:
        print(f"Downloading new image for '{title}'...")
        img_data = requests.get(url, timeout=10).content
        with open(filepath, "wb") as f:
            f.write(img_data)
        print(f"✅ Replaced image: {filename}")
    except Exception as e:
        print(f"❌ Failed to download {title}: {e}")

print("All replacement requests processed.")
