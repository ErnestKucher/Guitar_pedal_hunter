import requests
from bs4 import BeautifulSoup
import time
import random
import json
from urllib.parse import quote_plus

from sqlalchemy import TIME

STANDARD_SHIPPING_EUR = 9.90

def build_search_url(query, page=1, page_size=50):
    encoded_query = quote_plus(query)
    url = f'https://www.thomannmusic.com/en-lt/search.html?ls={page_size}&pg={page}&sw={encoded_query}'
    return url

def fetch_page(url, max_retries=3):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response
            elif response.status_code == 429:
                wait_time = 2 * attempt
                print(f"[/WARM] Rate limited (429). Waiting {wait_time}s before retrying...")
                time.sleep(wait_time)
            elif 500 <= response.status_code < 600:
                print(f"[/WARM] Server error {response.status_code}. Retrying...")
                time.sleep(1.5 * attempt)
            else:
                print(f"[ERROR] Failed to fetch {url}, status code: {response.status_code}")
                return None
            
        except requests.RequestException as e:
            print(f"[ERROR] Request failed: {e}")
            time.sleep(1.5 * attempt)

        print("[ERROR] Max retries reached. Giving up.")
        return None

def parse_html(response):
    soup = BeautifulSoup(response.text, "html.parser")
    return soup

def get_product_cards(soup):
    cards = soup.find_all("div", class_="product")
    return cards

def get_urls_by_id(soup):
    cards = get_product_cards(soup)
    urls_by_id = {}
    for card in cards:
        id_tag = card.find("input", attrs={"name": "ar"})
        url_tag = card.find("a", class_="product__content")
        if id_tag and url_tag:
            product_id = id_tag["value"]
            url = f"https://www.thomannmusic.com/en-lt/{url_tag['href']}"
            urls_by_id[product_id] = url
    return urls_by_id

def find_datalayer_script(soup):
    scripts = soup.find_all("script")
    for script in scripts:
        if script.string and "view_item_list" in script.string:
            return script.string
    return None

def parse_datalayer_json(script_text):
    start = script_text.find("(") + 1
    end = script_text.rfind(")")
    json_text = script_text[start:end]
    data = json.loads(json_text)
    return data

def build_listings(data, urls_by_id):
    listings = []
    for item in data["ecommerce"]["items"]:
        product_id = item["item_id"]
        url = urls_by_id.get(product_id)
        if url:
            listings.append({
                "id": product_id,
                "title": item["item_name"],
                "price": item["price"],
                "shipping": STANDARD_SHIPPING_EUR,
                "total_price": item["price"] + STANDARD_SHIPPING_EUR,
                "url": url
            })
    return listings

def scrape_thomann(query):
    url = build_search_url(query)
    response = fetch_page(url)
    
    if response is None:
        return {"error": "Could not reach Thomann. Please try again later."}
    
    soup = parse_html(response)
    script_text = find_datalayer_script(soup)
    
    if script_text is None:
        return {"error": f"No information found for '{query}' on Thomann."}
    
    data = parse_datalayer_json(script_text)
    urls_by_id = get_urls_by_id(soup)
    listings = build_listings(data, urls_by_id)
    
    return {"listings": listings}

if __name__ == "__main__":
    result = scrape_thomann("/")
    print(result)