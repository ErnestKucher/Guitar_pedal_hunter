import requests
import base64
import os
from dotenv import load_dotenv

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
        "q": query
    }
    response = requests.get(url, headers=headers, params=params)
    return response

if __name__ == "__main__":
    token_response = get_ebay_token()
    access_token = token_response.json()["access_token"]
    
    search_response = search_ebay("fuzz face", access_token)
    print(search_response.status_code)
    result = search_response.json()
    print(f"Total results: {result.get('total')}")
    
    if "itemSummaries" in result:
        for num, item in enumerate(result["itemSummaries"][:5]):
            print(f"--------Item {num + 1}-------------:")
            print("Title:", item.get("title"))
            print("Condition:", item.get("condition"))
            print("Price:", item.get("price").get("value"))
            print("Shipping Cost:", item.get("shippingOptions")[0].get("shippingCost").get("value") if item.get("shippingOptions") else "N/A")
            print("Total Price:", float(item.get("price").get("value")) + float(item.get("shippingOptions")[0].get("shippingCost").get("value")) if item.get("shippingOptions") else "N/A")
            print("Item URL:", item.get("itemWebUrl"))