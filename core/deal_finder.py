import statistics
from datetime import date
from scrapers.reverb_scraper import scrape_reverb, get_sold_prices, create_session
import utils.database
from utils.telegram import send_telegram_message
from scrapers.ebay_scraper import scrape_ebay


def normalize_query(query):
    return query.lower().strip()


def deduplicate(listings):
    unique = {}
    for l in listings:
        if l.get("id"):
            unique[l["id"]] = l
    return list(unique.values())


def find_deals(query, session=None):
    query = normalize_query(query)

    if session is None:
        session = create_session()

    results = scrape_reverb(query, session=session)
    sold_results = get_sold_prices(query, session=session)

    results = deduplicate(results)
    sold_results = deduplicate(sold_results)

    for l in results:
        utils.database.save_price_history(
            search_query=query,
            listing_id=l["id"],
            listing_title=l["title"],
            listing_price=l["total_price"],
            listing_condition=l["condition"],
            listing_url=l["url"],
            listing_type="active"
        )

    for l in sold_results:
        utils.database.save_price_history(
            search_query=query,
            listing_id=l["id"],
            listing_title=l["title"],
            listing_price=l["total_price"],
            listing_condition=l["condition"],
            listing_url=l["url"],
            listing_type="sold"
        )

    sold_by_condition = {}
    for l in sold_results:
        if l["total_price"] is not None:
            condition = l["condition"]
            if condition not in sold_by_condition:
                sold_by_condition[condition] = []
            sold_by_condition[condition].append(l["total_price"])

    if not sold_by_condition:
        return {
            "error": "No sold listings found. Cannot calculate median price.",
            "active_count": len(results),
            "median_by_condition": {},
            "new_deals": []
        }

    median_by_condition = {
        condition: statistics.median(prices)
        for condition, prices in sold_by_condition.items()
    }

    below_median = sorted(
        [l for l in results if l["condition"] in median_by_condition
         and l["total_price"] is not None
         and l["total_price"] < median_by_condition[l["condition"]]],
        key=lambda x: x["total_price"]
    )

    seen_deals = utils.database.load_seen()

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

    if new_deals:
        message = f"🔥 New undervalued listings found for '{query}':\n\n"
        for index, l in enumerate(new_deals[:5], start=1):
            condition_median = median_by_condition[l["condition"]]
            diff = condition_median - l["total_price"]
            percent = (diff / condition_median) * 100
            message += (
                f"[{index}] {l['title']}\n"
                f"💰 Price:         {l['total_price']:.2f} EUR\n"
                f"📉 Below Median:  {diff:.2f} EUR ({percent:.1f}%)\n"
                f"📦 Condition:     {l['condition']}\n"
                f"🔗 {l['url']}\n\n"
            )
        send_telegram_message(message)

    return {
        "active_count": len(results),
        "median_by_condition": median_by_condition,
        "new_deals": new_deals
    }