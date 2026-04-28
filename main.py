from scrapers.reverb_scraper import scrape_reverb, get_sold_prices
from config.configurations import pedals_list

print("Pedal Hunter started")

#scrape_reverb("MRX M68 Uni-Vibe")
get_sold_prices("analogman sun face")

# for pedal in pedals_list:
#     scrape_reverb(pedal)

print("Pedal Hunter finished")

