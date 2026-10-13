import requests
import base64
import os
from dotenv import load_dotenv
from utils.helpers import to_float, is_valid_listing

load_dotenv()
EBAY_PROD_CLIENT_ID = os.getenv("EBAY_PROD_CLIENT_ID")
EBAY_PROD_CLIENT_SECRET = os.getenv("EBAY_PROD_CLIENT_SECRET")

def get_ebay_token():
    url = "https://api.ebay.com/identity/v1/oauth2/token"
    
    credentials = f"{EBAY_PROD_CLIENT_ID}:{EBAY_PROD_CLIENT_SECRET}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {encoded_credentials}"
    }
    
    body = {
        "grant_type": "client_credentials",
        "scope": "https://api.ebay.com/oauth/api_scope"
    }
    
    response = requests.post(url, headers=headers, data=body)
    return response

def search_ebay(query, access_token):
    url = "https://api.ebay.com/buy/browse/v1/item_summary/search"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-EBAY-C-MARKETPLACE-ID": "EBAY_DE"
    }
    params = {
        "q": f' "{query}"'
    }
    response = requests.get(url, headers=headers, params=params)
    return response

def parse_ebay_item(item):
    price = to_float(item.get("price", {}).get("value") if item.get("price") else None)
    shipping_cost = to_float(item.get("shippingOptions", [{}])[0].get("shippingCost", {}).get("value") if item.get("shippingOptions") else None)
    total_price = price + shipping_cost if price is not None and shipping_cost is not None else None

    return {
        "id": item.get("itemId"),
        "title": item.get("title"),
        "condition": item.get("condition"),
        "price": price,
        "shipping": shipping_cost,
        "total_price": total_price,
        "url": (item.get("itemWebUrl") or "").split("?")[0]
    }

def scrape_ebay(query):
    token_response = get_ebay_token()
    if token_response.status_code != 200:
        return {"error": "Could not authenticate with eBay."}

    access_token = token_response.json().get("access_token")
    if not access_token:
        return {"error": "Could not authenticate with eBay."}

    search_response = search_ebay(query, access_token)
    if search_response.status_code != 200:
        return {"error": "eBay search failed."}

    items = search_response.json().get("itemSummaries", [])
    if not items:
        return {"error": f"No information found for '{query}' on eBay."}

    parsed = [parse_ebay_item(item) for item in items]
    listings = [item for item in parsed if is_valid_listing(item)]
    return {"listings": listings}

if __name__ == "__main__":
    print(scrape_ebay("uni vibe")["listings"][0])
