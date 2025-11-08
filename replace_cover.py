import os
import json
import requests

# === CONFIG ===
IMAGES_DIR = "images"
COVERS_JSON = "docs/covers.json"
REQUESTS_JSON = "replace_requests.json"  # file with replacement requests

# Ensure folders exist
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs("docs", exist_ok=True)

def sanitize_filename(name):
    invalid = '<>:"/\\|?*'
    for ch in invalid:
        name = name.replace(ch, '')
    return name.strip()

def load_json(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_json(data, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def download_image(url, filename):
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        filepath = os.path.join(IMAGES_DIR, filename)
        with open(filepath, "wb") as f:
            f.write(response.content)
        print(f"✅ Downloaded and replaced: {filename}")
        return True
    except requests.RequestException as e:
        print(f"❌ Failed to download {url}: {e}")
        return False

def main():
    # Load current covers and replacement requests
    covers = load_json(COVERS_JSON)
    requests_list = load_json(REQUESTS_JSON)

    if not requests_list:
        print("⚠️ No replacement requests found.")
        return

    for req in requests_list:
        title = req.get("title")
        new_url = req.get("newUrl")
        if not title or not new_url:
            continue

        filename = sanitize_filename(title) + ".jpg"

        # Download and replace image
        if download_image(new_url, filename):
            # Update covers.json
            for cover in covers:
                if cover["title"] == title:
                    cover["url"] = new_url
                    break
            else:
                # Title not in covers.json, add it
                covers.append({"title": title, "url": new_url})

    # Save updated covers.json
    save_json(covers, COVERS_JSON)
    print(f"✅ Updated {COVERS_JSON}")

    # Clear requests file after processing
    save_json([], REQUESTS_JSON)
    print(f"✅ Cleared {REQUESTS_JSON}")

if __name__ == "__main__":
    main()
