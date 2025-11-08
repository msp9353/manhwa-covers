import os
import csv
import requests
import time
import json
from urllib.parse import quote

# === CONFIG ===
SHEET_ID = "125magt7y48FLQRzBUgz-H1FmxfaK6edvIKdOGFSBpY8"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"
IMAGES_DIR = "images"
OUTPUT_JSON = "docs/covers.json"
DELAY_SECONDS = 0.4  # wait between requests to avoid rate limiting
MAX_RETRIES = 3      # retry failed requests this many times

# === SETUP ===
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs("docs", exist_ok=True)  # ensure docs folder exists

def sanitize_filename(name):
    invalid = '<>:"/\\|?*'
    for ch in invalid:
        name = name.replace(ch, '')
    return name.strip()

def get_titles_from_sheet():
    response = requests.get(CSV_URL)
    response.raise_for_status()
    decoded = response.content.decode('utf-8')
    reader = csv.reader(decoded.splitlines())
    titles = []
    for row in reader:
        if row and row[0].strip() and row[0].lower() != "title":
            titles.append(row[0].strip())
    return titles

def get_cover_url(title):
    query = quote(title)
    url = f"https://api.jikan.moe/v4/manga?q={query}&limit=1"

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = requests.get(url, timeout=10)
            if r.status_code != 200:
                print(f"❌ Attempt {attempt}: Failed for {title} (status {r.status_code})")
                time.sleep(DELAY_SECONDS * attempt)
                continue

            data = r.json()
            results = data.get("data", [])
            if not results:
                print(f"⚠️ No results for {title}")
                return None
            return results[0]["images"]["jpg"]["image_url"]

        except requests.RequestException as e:
            print(f"❌ Attempt {attempt}: Exception for {title}: {e}")
            time.sleep(DELAY_SECONDS * attempt)

    return None  # failed all retries

def download_image(title, image_url):
    filename = sanitize_filename(title) + ".jpg"
    filepath = os.path.join(IMAGES_DIR, filename)
    if os.path.exists(filepath):
        print(f"✅ Skipped existing: {filename}")
        return filepath
    img_data = requests.get(image_url).content
    with open(filepath, "wb") as f:
        f.write(img_data)
    print(f"⬇️  Saved: {filename}")
    return filepath

def main():
    print("Fetching titles from Google Sheet...")
    titles = get_titles_from_sheet()
    print(f"Found {len(titles)} titles.")

    covers_list = []

    for title in titles:
        filename = sanitize_filename(title) + ".jpg"
        filepath = os.path.join(IMAGES_DIR, filename)
        if os.path.exists(filepath):
            print(f"✅ Already exists: {title}")
        else:
            cover_url = get_cover_url(title)
            if cover_url:
                filepath = download_image(title, cover_url)
            else:
                print(f"⚠️ Skipping {title}, no image found")
                continue
            time.sleep(DELAY_SECONDS)

        # Add to JSON list (URL-encoded path)
        covers_list.append({
            "title": title,
            "path": f"images/{quote(filename)}"
        })

    # Write JSON file
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(covers_list, f, ensure_ascii=False, indent=2)
    print(f"✅ Written JSON to {OUTPUT_JSON}")

if __name__ == "__main__":
    main()
