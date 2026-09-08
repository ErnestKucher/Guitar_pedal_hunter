from scrapers.reverb_scraper import scrape_reverb, get_sold_prices, create_session
import statistics
import sys
import utils.database
from datetime import date

def normalize_query(query):
        return query.lower().strip()

def deduplicate(listings):
    unique = {}
    for l in listings:
        if l.get("id"):
            unique[l["id"]] = l
    return list(unique.values())

if __name__ == "__main__":
    query = normalize_query(" ".join(sys.argv[1:]))

    if not query:
        print("Please provide a search query as a command-line argument.")
        sys.exit(1)

    print(f"Searching for: {query}")

    try:
        session = create_session()
    except Exception as e:
        print(f"Error occurred while creating session: {e}")
        sys.exit(1)

    try:
        results = scrape_reverb(query, session=session)
    except Exception as e:
        print(f"Error occurred while scraping: {e}")
        sys.exit(1)

    try:
        sold_results = get_sold_prices(query, session=session)
    except Exception as e:
        print(f"Error occurred while fetching sold prices: {e}")
        sys.exit(1)
    
    results = deduplicate(results)
    for l in results:
        utils.database.save_price_history(
            search_query=query,
            listing_id=l["id"],
            listing_title=l["title"],
            listing_price=l["total_price"],
            listing_condition=l["condition"],
            listing_url=l["url"],
            listing_type= "active"
        )
    sold_results = deduplicate(sold_results)
    for l in sold_results:
        utils.database.save_price_history(
            search_query=query,
            listing_id=l["id"],
            listing_title=l["title"],
            listing_price=l["total_price"],
            listing_condition=l["condition"],
            listing_url=l["url"],
            listing_type= "sold"
        )
    seen_deals = utils.database.load_seen()


    sold_by_condition = {}
    for l in sold_results:
        if l["total_price"] is not None:
            condition = l["condition"]
            if condition not in sold_by_condition:
                sold_by_condition[condition] = []
            sold_by_condition[condition].append(l["total_price"])

    if not sold_by_condition:
        print("No sold listings found. Cannot calculate median price.")
        sys.exit(1)

    median_by_condition = {condition: statistics.median(prices) for condition, prices in sold_by_condition.items()}

    print(f"Found {len(results)} active listings")
    print(f"Median sold price by condition:")
    for condition, median_price in median_by_condition.items():
        print(f"  {condition}: {round(median_price, 2)}")

    below_median = sorted(
        [l for l in results if l["condition"] in median_by_condition and l["total_price"] is not None and l["total_price"] < median_by_condition[l["condition"]]],
        key=lambda x: x["total_price"]
    )

    new_deals = []
    for l in below_median:
        if l["id"] not in seen_deals:
            new_deals.append(l)
            utils.database.save_seen_deals(
                listing_id=l["id"],
                title=l["title"],
                price=l["total_price"],
                url=l["url"],
                condition=l["condition"],
                found_at=date.today().isoformat()
            )

    utils.database.prune_seen_deals(max_age_days=30)
    print(f"New deals found: {len(new_deals)}")

    if new_deals:
        print(f"\n🔥 Deals below median:\n")

        for index, l in enumerate(new_deals[:5], start=1):
            condition_median = median_by_condition[l["condition"]]
            diff = condition_median - l["total_price"]
            percent = (diff / condition_median) * 100
            print("=" * 50)
            print(f"[{index}] {l['title']}")
            print(f"💰 Price:         {l['total_price']:.2f} EUR")
            print(f"📉 Below Median:  {diff:.2f} EUR ({percent:.1f}%)")
            print(f"📦 Condition:     {l['condition']}")
            print(f"🔗 {l['url']}")
    else:
        print("✅ No NEW undervalued listings found")