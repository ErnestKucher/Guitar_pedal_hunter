from scrapers.reverb_scraper import scrape_reverb, get_sold_prices
import sys

if __name__ == "__main__":
    query = " ".join(sys.argv[1:])

    if not query:
        print("Please provide a search query as a command-line argument.")
        sys.exit(1)

    print(f"Searching for: {query}")

    results = scrape_reverb(query)
    sold_results = get_sold_prices(query)

    sold_prices = []
    for l in sold_results:
        price = l["price"]
        try:
            if price is not None:
                sold_prices.append(float(price))
        except (ValueError, TypeError):
            continue

    avg_price = sum(sold_prices) / len(sold_prices)

    prices = []
    for l in results:
        price = l["price"]
        try:
            if price is not None:
                prices.append(float(price))
        except (ValueError, TypeError):
            continue

    print(f"Found {len(results)} active listings")
    print(f"Average sold price: {round(avg_price, 2)}")

    below_avg = sorted(
        [l for l in results if l["price"] is not None and float(l["price"]) < avg_price],
        key=lambda x: x["price"]
    )

    if below_avg:
        print(f"\n🔥 Deals below average ({round(avg_price, 2)} EUR):\n")

        for l in below_avg:
            print(f"{l['price']} EUR | {l['condition']} | {l['url']}")
    else:
        print("No deals found below average price")