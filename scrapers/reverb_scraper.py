import requests
import math
import time
import json

with open("D:\\Programming\\pedal-hunter\\config\\query_text_active.graphql", "r", encoding="utf-8") as f:
    query_text_active = f.read()
with open("D:\\Programming\\pedal-hunter\\config\\query_text_sold.graphql", "r", encoding="utf-8") as f:
    query_text_sold = f.read()

def scrape_reverb(search_query, max_pages=None):

    url = "https://gql.reverb.com/graphql"

    session = requests.Session()

    session.headers.update({
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/json",
        "Origin": "https://reverb.com",
        "Referer": "https://reverb.com/",
        "x-display-currency": "EUR",
        "x-shipping-region": "LT"
    })

    # 🍪 cookies
    session.get("https://reverb.com")

    encoded_query = search_query.replace(" ", "+")

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
    response = session.post(url, json=payload)

    print("STATUS:", response.status_code)

    if response.status_code != 200:
        print(response.text)
        return

    data = response.json()

    if "data" not in data:
        print("ERROR RESPONSE:")
        print(data)
        return

    results = data["data"]["marketplaceListingsSearch"]

    total = results["pagination"]["total"]
    page_size = payload["variables"]["input"]["pageSize"]
    total_pages = math.ceil(total / page_size)

    if max_pages:
        total_pages = min(total_pages, max_pages)

    print(f"TOTAL LISTINGS: {total}")
    print(f"TOTAL PAGES: {total_pages}")

    # 🔁 loop per puslapius
    for page in range(1, total_pages + 1):

        print(f"\n--- PAGE {page} ---\n")

        payload["variables"]["input"]["page"] = page

        payload["variables"]["input"]["currentSearchParams"] = (
            f"query={encoded_query}&page={page}"
        )

        response = session.post(url, json=payload)

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
            title = item.get("title", "N/A")
            slug = item.get("slug", "")
            listing_id = item.get("id", "")
            price = (
                item.get("pricing", {})
                    .get("buyerPrice", {})
                    .get("display", "N/A")
            )
            condition = (
                item.get("condition", {})
                    .get("displayName", "N/A")
            )
            shipping = "N/A"

            for shipping_price in item.get("shipping", {}).get("shippingPrices", []):
                rate = shipping_price.get("rate")
                if rate and rate.get("display"):
                    shipping = rate["display"]
                    break

            listing_id = item.get("_id", "").replace("id:", "")
            slug = item.get("slug")
            url_item = f"https://reverb.com/item/{listing_id}-{slug}"

            print(f"Title: {title}")
            print(f"Price: {price}")
            print(f"Condition: {condition}")
            print(f"Shipping: {shipping}")
            print(f"URL: {url_item}")
            print("-----------")

        # 💤 anti-ban
        time.sleep(2)

def get_sold_prices(search_query):

    url = "https://gql.reverb.com/graphql"

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

    encoded_query = search_query.replace(" ", "+")

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

    response = session.post(url, json=payload)

    print("STATUS:", response.status_code)

    data = response.json()

    if "data" not in data:
        print("ERROR:", data)
        return

    listings = data["data"]["marketplaceListingsSearch"]["listings"]

    for item in listings:
        title = item.get("title")
        price = (
            item.get("pricing", {})
                .get("buyerPrice", {})
                .get("display")
        )
        condition = (
                item.get("condition", {})
                    .get("displayName", "N/A")
            )
        shipping = "N/A"

        for shipping_price in item.get("shipping", {}).get("shippingPrices", []):
            rate = shipping_price.get("rate")
            if rate and rate.get("display"):
                shipping = rate["display"]
                break

        print(f"Title: {title}")
        print(f"Sold: {price}")
        print(f"Condition: {condition}")
        print(f"Shipping: {shipping}")
        print("-----------")

    time.sleep(2)


    