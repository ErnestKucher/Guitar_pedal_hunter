from scrapers.reverb_scraper import scrape_reverb, get_sold_prices
from config.configurations import pedals_list
from analysis.deal_finder import calculate_median, evaluate_listing

def main():

    query = "MXR Phase 90"

    print(f"\n🔍 Searching: {query}\n")

    # 1. ACTIVE listings
    active_listings = scrape_reverb(query, max_pages=2)

    # 2. SOLD data
    sold_listings = get_sold_prices(query)

    sold_prices = [
        x["price"] for x in sold_listings
        if x.get("price") is not None
    ]

    median = calculate_median(sold_prices)

    if not median:
        print("❌ No sold data found")
        return

    print(f"\n📊 Median sold price: {median}\n")

    # 3. Evaluate
    deals = []

    for item in active_listings:

        price = item.get("price")
        shipping = item.get("shipping")

        if price is None:
            continue

        status, score = evaluate_listing(price, median, shipping)

        item["score"] = round(score, 2)
        item["status"] = status
        item["median"] = median

        if "BUY" in status:
            deals.append(item)

        print(f"{item['title']}")
        print(f"Price: {price} + {shipping} shipping")
        print(f"Score: {round(score, 2)}")
        print(f"Status: {status}")
        print(item["url"])
        print("-----------")

    # 4. Summary
    print("\n====================")
    print(f"🔥 BUY opportunities: {len(deals)}")
    print("====================\n")


if __name__ == "__main__":
    main()