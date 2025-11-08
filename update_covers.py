import os
import csv
import requests
from urllib.parse import quote

# === CONFIG ===
SHEET_ID = "YOUR_SHEET_ID_HERE"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"
IMAGES_DIR = "images"

# === SETUP ===
os.makedirs(IMAGES_DIR, exist_ok=True)

def sanitize_filename(name):
    # Replace characters not allowed in filenames
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
    r = requests.get(url)
    if r.status_code != 200:
        print(f"❌ Failed to fetch Jikan data for {title}")
        return None
    data = r.json()
    results = data.get("data", [])
    if not results:
        print(f"⚠️ No results for {title}")
        return None
    return results[0]["images"]["jpg"]["image_url"]

def download_image(title, image_url):
    filename = sanitize_filename(title) + ".jpg"
    filepath = os.path.join(IMAGES_DIR, filename)
    if os.path.exists(filepath):
        print(f"✅ Skipped existing: {filename}")
        return
    img_data = requests.get(image_url).content
    with open(filepath, "wb") as f:
        f.write(img_data)
    print(f"⬇️  Saved: {filename}")

def main():
    print("Fetching titles from Google Sheet...")
    titles = get_titles_from_sheet()
    print(f"Found {len(titles)} titles.")
    for title in titles:
        filename = sanitize_filename(title) + ".jpg"
        filepath = os.path.join(IMAGES_DIR, filename)
        if os.path.exists(filepath):
            print(f"✅ Already exists: {title}")
            continue
        cover_url = get_cover_url(title)
        if cover_url:
            download_image(title, cover_url)

if __name__ == "__main__":
    main()
