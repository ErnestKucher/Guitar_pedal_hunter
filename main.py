from scrapers.reverb_scraper import scrape_reverb, get_sold_prices
from config.configurations import pedals_list
from analysis.deal_finder import calculate_median, evaluate_listing

search = "analogman sunface"
print(get_sold_prices(search)[1])

print(scrape_reverb(search)[1])
