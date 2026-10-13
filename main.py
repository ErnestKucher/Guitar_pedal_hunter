import sys
from core.deal_finder import find_deals
from utils.database import create_tables

if __name__ == "__main__":
    query = " ".join(sys.argv[1:])
    create_tables()

    if not query:
        print("Please provide a search query as a command-line argument.")
        sys.exit(1)

    print(f"Searching for: {query}")

    try:
        result = find_deals(query)
    except Exception as e:
        print(f"Error occurred while finding deals: {e}")
        sys.exit(1)

    if "error" in result:
        print(result["error"])
        sys.exit(1)
    

    print(f"Found {result['active_count']} active listings")
    print("Median sold price by condition:")
    for condition, median_price in result["median_by_condition"].items():
        print(f"  {condition}: {round(median_price, 2)}")

    new_deals = result["new_deals"]
    print(f"New deals found: {len(new_deals)}")

    if new_deals:
        print("\n🔥 Deals below median:\n")
        for index, l in enumerate(new_deals[:5], start=1):
            condition_median = result["median_by_condition"][l["condition"]]
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