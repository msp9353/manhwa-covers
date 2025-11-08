import sys
import os
import json
import requests

IMAGES_DIR = "images"
COVERS_JSON = "docs/covers.json"

def sanitize_filename(name):
    invalid = '<>:"/\\|?*'
    for ch in invalid:
        name = name.replace(ch, '')
    return name.strip()

def download_image(url, filepath):
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    with open(filepath, "wb") as f:
        f.write(resp.content)
    print(f"⬇️ Saved new image to {filepath}")

def update_covers_json(filename, url):
    if not os.path.exists(COVERS_JSON):
        covers = []
    else:
        with open(COVERS_JSON, "r", encoding="utf-8") as f:
            covers = json.load(f)

    # Replace the url for the given filename
    found = False
    for item in covers:
        if item["title"] + ".jpg" == filename:
            item["url"] = url
            found = True
            break
    if not found:
        # if not found, add it
        title = filename.rsplit(".", 1)[0]
        covers.append({"title": title, "url": url})

    with open(COVERS_JSON, "w", encoding="utf-8") as f:
        json.dump(covers, f, ensure_ascii=False, indent=2)
    print(f"✅ Updated covers.json")

def main():
    if len(sys.argv) != 3:
        print("Usage: python replace_cover.py <filename> <new_url>")
        sys.exit(1)

    filename = sys.argv[1]
    new_url = sys.argv[2]

    filepath = os.path.join(IMAGES_DIR, filename)
    os.makedirs(IMAGES_DIR, exist_ok=True)

    download_image(new_url, filepath)
    update_covers_json(filename, new_url)

if __name__ == "__main__":
    main()
