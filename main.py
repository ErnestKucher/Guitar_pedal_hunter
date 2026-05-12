from scrapers.reverb_scraper import scrape_reverb, get_sold_prices
import statistics
import sys
from utils.storage import load_seen, save_seen
from datetime import date

if __name__ == "__main__":
    query = " ".join(sys.argv[1:])

    if not query:
        print("Please provide a search query as a command-line argument.")
        sys.exit(1)

    print(f"Searching for: {query}")

    results = scrape_reverb(query)
    sold_results = get_sold_prices(query)

    def deduplicate(listings):
        unique = {}
        for l in listings:
            if l.get("id"):
                unique[l["id"]] = l
        return list(unique.values())
    
    results = deduplicate(results)
    sold_results = deduplicate(sold_results)
    seen_deals = load_seen()

    sold_prices = [l["total_price"] for l in sold_results if l["total_price"] is not None]
    if not sold_prices:
        print("No sold listings found. Cannot calculate median price.")
        sys.exit(1)

    median_price = statistics.median(sold_prices)
    print(f"Found {len(results)} active listings")
    print(f"Median sold price: {round(median_price, 2)}")

    below_median = sorted(
        [l for l in results if l["total_price"] is not None and l["total_price"] < median_price],
        key=lambda x: x["total_price"]
    )

    new_deals = []
    for l in below_median:
        if l["id"] not in seen_deals:
            new_deals.append(l)
            seen_deals[l["id"]] = {
                "title": l["title"],
                "price": l["total_price"],
                "url": l["url"],
                "condition": l["condition"],
                "found_at": str(date.today())
            }
    save_seen(seen_deals)
    print(f"New deals found: {len(new_deals)}")

    if new_deals:
        print(f"\n🔥 Deals below median ({round(median_price, 2)} EUR):\n")

        for index, l in enumerate(new_deals[:5], start=1):
            diff = median_price - l["total_price"]
            percent = (diff / median_price) * 100
            print("=" * 50)
            print(f"[{index}] {l['title']}")
            print(f"💰 Price:         {l['total_price']:.2f} EUR")
            print(f"📉 Below Median:  {diff:.2f} EUR ({percent:.1f}%)")
            print(f"📦 Condition:     {l['condition']}")
            print(f"🔗 {l['url']}")
    else:
        print("✅ No NEW undervalued listings found")