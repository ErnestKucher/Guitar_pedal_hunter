import requests
import math
import time
import random
from urllib.parse import quote_plus
from config.configurations import EXCLUDED_TITLE_KEYWORDS
from pathlib import Path

CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"

with open(CONFIG_DIR / "query_text_active.graphql", "r", encoding="utf-8") as f:
    query_text_active = f.read()
with open(CONFIG_DIR / "query_text_sold.graphql", "r", encoding="utf-8") as f:
    query_text_sold = f.read().strip()

def create_session():
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/json",
        "Origin": "https://reverb.com",
        "Referer": "https://reverb.com/",
        "x-display-currency": "EUR",
        "x-shipping-region": "LT"
    })
    session.get("https://reverb.com")
    return session

def fetch(session, url, payload, max_retries=3):
    for attempt in range(1, max_retries + 1):
        try:
            response = session.post(url, json=payload, timeout=10)

            if response.status_code == 200:
                return response

            elif response.status_code == 429:
                wait_time = 2 * attempt
                print(f"[WARN] 429 rate limited. Waiting {wait_time}s...")
                time.sleep(wait_time)

            elif 500 <= response.status_code < 600:
                print(f"[WARN] Server error {response.status_code}. Retrying...")
                time.sleep(1.5 * attempt)

            else:
                print(f"[ERROR] Unexpected status {response.status_code}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Request failed: {e}")
            time.sleep(1.5 * attempt)

    print("[ERROR] Max retries reached. Giving up.")
    return None

def to_float(value):
    try:
        if value is None:
            return None
        return float(value)
    except (ValueError, TypeError):
        return None
    
def deduplicate(listings):
    unique = {}
    for l in listings:
        if l.get("id"):
            unique[l["id"]] = l
    return list(unique.values())

def is_valid_listing(listing):
    title = listing["title"].lower()

    for keyword in EXCLUDED_TITLE_KEYWORDS:
        if keyword in title:
            return False

    return True

def parse_listing(item):
    title = item.get("title", "N/A")
    raw_price = (
        item.get("pricing", {})
            .get("buyerPrice", {})
            .get("amount")
    )
    price = to_float(raw_price)

    condition = (
        item.get("condition", {})
            .get("displayName", "N/A")
    )
    shipping = None

    for shipping_price in item.get("shipping", {}).get("shippingPrices", []):
        rate = shipping_price.get("rate")
        if rate and rate.get("amount"):
            shipping = to_float(rate.get("amount"))
            break

    raw_id = item.get("_id", "")
    if not raw_id:
        print("[WARN] Missing ID in listing")
    listing_id = raw_id.replace("id:", "") if raw_id else None
    slug = item.get("slug","")
    url_item = f"https://reverb.com/item/{listing_id}-{slug}"

    if price is not None and shipping is not None:
        total_price = price + shipping
    else:
        total_price = None

    return {
        "title": title,
        "id": listing_id,
        "price": price,
        "condition": condition,
        "shipping": shipping,
        "url": url_item,
        "total_price": total_price
    }

def scrape_reverb(search_query, max_pages=None, session=None):

    all_listings = []
    url = "https://gql.reverb.com/graphql"
    encoded_query = quote_plus(search_query)

    # 🔹 pradinis payload (BE page paramo)
    payload = {
        "operationName": "MarketplaceListingsSearch",
        "variables": {
            "listViewEnabled": False,
            "input": {
                "query": search_query,
                "page": 1,
                "pageSize": 60,
                "currentSearchParams": f"query={encoded_query}"
            }
        },
        "query": query_text_active.strip()
    }

    # 🔹 pirmas request – sužinom total
    if session is None:
        session = create_session()
    response = fetch(session, url, payload)
    if not response:
        print("Failed to fetch data")
        return []

    data = response.json()

    results = data["data"]["marketplaceListingsSearch"]

    total = results["pagination"]["total"]
    page_size = payload["variables"]["input"]["pageSize"]
    total_pages = math.ceil(total / page_size)

    if max_pages:
        total_pages = min(total_pages, max_pages)

    # 🔁 loop per puslapius
    for page in range(1, total_pages + 1):

        payload["variables"]["input"]["page"] = page

        payload["variables"]["input"]["currentSearchParams"] = (
            f"query={encoded_query}&page={page}"
        )

        response = fetch(session, url, payload)
        if not response:
            print(f"[WARN] Page {page} failed after retries")
            continue

        if response.status_code != 200:
            print(f"❌ Failed page {page}")
            print(response.text[:300])
            continue

        # Pasitikrinam kokius duomenis gaunam:
        data = response.json()

        if "data" not in data:
            print(f"❌ Bad data on page {page}")
            print(data)
            continue

        listings = data["data"]["marketplaceListingsSearch"]["listings"]

        if not listings:
            print(f"⚠️ Empty page {page}")
            continue

        for item in listings:
            listing = parse_listing(item)
            if is_valid_listing(listing):
                all_listings.append(listing)

        # 💤 anti-ban
        time.sleep(random.uniform(1.5, 3.5))

    return deduplicate(all_listings)

def get_sold_prices(search_query, session=None) :

    sold_listings = []
    url = "https://gql.reverb.com/graphql"
    encoded_query = quote_plus(search_query)

    payload = {
        "operationName": "Core_Marketplace_Remixer_Search",
        "variables": {
            "listViewEnabled": False,
            "input": {
                "query": search_query,
                "page": 1,
                "pageSize": 60,
                "currentSearchParams": f"query={encoded_query}&product_type=effects-and-pedals&show_only_sold=true"
            }
        },
        "query": query_text_sold
    }

    if session is None:
        session = create_session()
    response = fetch(session, url, payload)
    if not response:
        print("❌ Failed to fetch data")
        return []
    data = response.json()

    if "data" not in data:
        print("ERROR:", data)
        return []

    results = data["data"]["marketplaceListingsSearch"]

    total = results["pagination"]["total"]
    page_size = payload["variables"]["input"]["pageSize"]
    total_pages = math.ceil(total / page_size)

    for page in range(1, total_pages + 1):
        payload["variables"]["input"]["page"] = page
        payload["variables"]["input"]["currentSearchParams"] = (
            f"query={encoded_query}&page={page}&product_type=effects-and-pedals&show_only_sold=true"
        )

        response = fetch(session, url, payload)
        if not response:
            print(f"[WARN] Page {page} failed after retries")
            continue

        if response.status_code != 200:
            print(f"❌ Failed page {page}")
            continue

        data = response.json()

        if "data" not in data:
            print(f"❌ Bad data page {page}")
            continue

        listings = data["data"]["marketplaceListingsSearch"]["listings"]

        for item in listings:
            sold_listings.append(parse_listing(item))

        time.sleep(random.uniform(1.5, 3.5))

    return deduplicate(sold_listings)


    