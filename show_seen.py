from utils.database import load_seen

seen_deals = load_seen()

if not seen_deals:
    print("No saved deals.")
    exit()

print(f"Saved deals: {len(seen_deals)}\n")

for index, (deal_id, deal) in enumerate(seen_deals.items(), start=1):

    print("=" * 60)
    print(f"[{index}] {deal['title']}")
    print(f"💰 Price:      {deal['price']:.2f} EUR")
    print(f"📦 Condition:  {deal['condition']}")
    print(f"📅 Found at:   {deal['found_at']}")
    print(f"🔗 {deal['url']}")