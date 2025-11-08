import sys
import os
import requests
from urllib.parse import quote

if len(sys.argv) != 3:
    print("Usage: replace_cover.py <title> <new_url>")
    sys.exit(1)

title = sys.argv[1]
new_url = sys.argv[2]

IMAGES_DIR = "images"

def sanitize_filename(name):
    invalid = '<>:"/\\|?*'
    for ch in invalid:
        name = name.replace(ch, '')
    return name.strip()

filename = sanitize_filename(title) + ".jpg"
filepath = os.path.join(IMAGES_DIR, filename)

# Download the new image
try:
    resp = requests.get(new_url, timeout=10)
    resp.raise_for_status()
    with open(filepath, "wb") as f:
        f.write(resp.content)
    print(f"✅ Replaced image: {filename}")
except Exception as e:
    print(f"❌ Failed to download new image: {e}")
    sys.exit(1)
