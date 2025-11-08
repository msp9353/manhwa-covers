import os
import json
import requests
from urllib.parse import quote

IMAGES_DIR = "images"
REQUESTS_FILE = "replace_requests.json"

def sanitize_filename(name):
    invalid = '<>:"/\\|?*'
    for ch in invalid:
        name = name.replace(ch, '')
    return name.strip()

def main():
    if not os.path.exists(REQUESTS_FILE):
        print(f"{REQUESTS_FILE} not found.")
        return

    with open(REQUESTS_FILE, "r", encoding="utf-8") as f:
        requests_list = json.load(f)

    if not os.path.exists(IMAGES_DIR):
        os.makedirs(IMAGES_DIR)

    for req in requests_list:
        title = req["title"]
        url = req["newUrl"]
        filename = sanitize_filename(title) + ".jpg"
        filepath = os.path.join(IMAGES_DIR, filename)
        try:
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            with open(filepath, "wb") as f:
                f.write(resp.content)
            print(f"✅ Replaced: {filename}")
        except Exception as e:
            print(f"❌ Failed to replace {filename}: {e}")

    print("All replacement requests processed.")

if __name__ == "__main__":
    main()
