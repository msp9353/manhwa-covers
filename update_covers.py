import os
import csv
import requests
import time
from urllib.parse import quote

# === CONFIG ===
SHEET_ID = "125magt7y48FLQRzBUgz-H1FmxfaK6edvIKdOGFSBpY8"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"
IMAGES_DIR = "images"
OUTPUT_FILE = "docs/covers.txt"  # New file for HTML
DELAY_SECONDS = 0.4  # wait between requests to avoid rate limiting
MAX_RETRIES = 3      # retry failed requests this many times

# === SETUP ===
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

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
                print(f"❌ Attempt {attempt}: Failed to fetch Jikan data for {title} (status {r.status_code})")
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
        return filename  # return existing filename
    img_data = requests.get(image_url).content
    with open(filepath, "wb") as f:
        f.write(img_data)
    print(f"⬇️  Saved: {filename}")
    return filename

def main():
    print("Fetching titles from Google Sheet...")
    titles = get_titles_from_sheet()
    print(f"Found {len(titles)} titles.")

    cover_lines = []

    for title in titles:
        filename = sanitize_filename(title) + ".jpg"
        filepath = os.path.join(IMAGES_DIR, filename)
        if os.path.exists(filepath):
            print(f"✅ Already exists: {title}")
        else:
            cover_url = get_cover_url(title)
            if cover_url:
                filename = download_image(title, cover_url)
            else:
                continue  # skip if no cover

        # Add title|image path line
        cover_lines.append(f"{title}|images/{filename}")
        time.sleep(DELAY_SECONDS)  # ensure we don't exceed rate limits

    # Write covers.txt for HTML
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(cover_lines))

    print(f"📄 Wrote {len(cover_lines)} lines to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
