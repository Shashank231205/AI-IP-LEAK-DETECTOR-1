import requests
import csv
import time
import os
from itertools import cycle

# SerpAPI keys
SERP_API_KEYS = [
    "07df5b70798f8195fc6418fce15b1cce141af5ec5cae3c86ca0e50079b4e3d9b",
    "94345e7764eb66bc27b44140378ee2b72f59d4678aa383e6dddb98aa31840ced",
    "1c142a265e2cf7143d9aac1a7cb3f85e4d3260f4cfc1775688eb7c3006f91a51",
    "bd22f3b84b47630ac85089d4cbb64c828e56abe086b6217b445b2bcbea57e120",
]

# Constants
MAX_DESCRIPTIONS = 20
MIN_DESCRIPTIONS = 5
WAIT_BETWEEN_REQUESTS = 2
RETRIES = 4
OUTPUT_CSV = "product_descriptions.csv"

def load_products(file_path="product_list.txt"):
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def fetch_descriptions(product, api_key):
    url = "https://serpapi.com/search.json"
    params = {
        "q": product,
        "engine": "google",
        "api_key": api_key
    }
    try:
        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()
        data = response.json()
        descriptions = []

        if "organic_results" not in data:
            print("  ⚠ No organic_results found.")
            return []

        for result in data["organic_results"]:
            snippet = result.get("snippet", "")
            if snippet:
                descriptions.append(snippet.strip())
        return list(set(descriptions))[:MAX_DESCRIPTIONS]

    except Exception as e:
        print(f"  ❌ Error for {product} with key {api_key[:6]}...: {e}")
        return []

def save_to_csv(data, filename):
    file_exists = os.path.isfile(filename)
    with open(filename, "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(["Product", "Description"])
        for product, descriptions in data.items():
            for desc in descriptions:
                writer.writerow([product, desc])

def main():
    products = load_products("product_list.txt")
    key_pool = cycle(SERP_API_KEYS)

    for i, product in enumerate(products, 1):
        print(f"\n[{i}/{len(products)}] Processing: {product}")
        all_descs = []

        for attempt in range(RETRIES):
            api_key = next(key_pool)
            new_descs = fetch_descriptions(product, api_key)
            all_descs.extend(new_descs)
            all_descs = list(set(all_descs))  # deduplicate
            print(f"  🔄 Attempt {attempt+1} - Got {len(all_descs)} so far")
            if len(all_descs) >= MIN_DESCRIPTIONS:
                break
            time.sleep(WAIT_BETWEEN_REQUESTS)

        if all_descs:
            to_save = all_descs[:MAX_DESCRIPTIONS]
            save_to_csv({product: to_save}, OUTPUT_CSV)
            print(f"  ✅ Saved {len(to_save)} descriptions.")
        else:
            print(f"  ⚠ Still 0 descriptions, saving empty entry.")
            save_to_csv({product: ["No description found"]}, OUTPUT_CSV)

        time.sleep(WAIT_BETWEEN_REQUESTS)

    print("\n✅ Done. Output saved to:", os.path.abspath(OUTPUT_CSV))

if __name__ == "__main__":
    main()
