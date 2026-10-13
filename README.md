# Pedal Hunter

Finds underpriced used guitar pedals on Reverb by comparing active listings
with condition-specific sold-price medians, then sends the best deals to
Telegram together with reference prices from eBay and Thomann.

## Why

Checking whether a used pedal is a good deal means opening many listings and
guessing. Pedal Hunter automates that: it pulls recent sold prices, computes a
fair median per condition (a "Mint" and a "Good" pedal are never compared
against each other), and flags active listings priced below that median.

## Features

- Reverb: active + sold listings via Reverb's GraphQL endpoint, with retries
  and polite delays
- Per-condition median sold prices; only listings below their own
  condition's median are flagged
- SQLite storage: `seen_deals` (no repeat notifications, auto-pruned after
  30 days) and `price_history` (every scraped listing, active and sold,
  timestamped, for trend analysis)
- eBay: official Browse API with OAuth2 client-credentials flow
- Thomann: search results parsed from the page's embedded `dataLayer` JSON
- Telegram bot notifications
- FastAPI endpoints (`/`, `/deals`, `/search?query=...`)
- Shared business logic in `core/deal_finder.py`, used by both CLI and API
- pytest suite (15 tests)

## How it works

1. Scrape active and sold listings from Reverb, deduplicate
2. Save everything to `price_history`
3. Group sold prices by condition, compute medians
4. Flag active listings below their condition's median
5. Save new deals to `seen_deals`, prune old ones
6. Fetch eBay and Thomann reference listings for the same query
7. Send a Telegram summary

## Example notification

```
***New undervalued listings found for 'mxr uni vibe' in Reverb***

[1] MXR M68 Uni-Vibe (Black)
Price:         125.00 EUR
Below Median:  33.29 EUR (21.0%)
Condition:     Mint
URL: https://reverb.com/item/...

***Similar listings available on Thomann***
[1] M68 Uni-Vibe Chorus/Vibrato
Price: 163.90 EUR
```

## Setup

```bash
git clone https://github.com/ErnestKucher/Guitar_pedal_hunter.git
cd Guitar_pedal_hunter
python -m venv venv
venv\Scripts\activate      # Windows
pip install -r requirements.txt
python -m utils.database
```

Create a `.env` file (see `.env.example`):

```
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
EBAY_PROD_CLIENT_ID=
EBAY_PROD_CLIENT_SECRET=
```

Create the database tables once:

```bash
python -m utils.database
```

## Usage

```bash
python main.py "mxr uni vibe"       # CLI
python show_seen.py                 # list saved deals
uvicorn app:app --reload            # API, docs at /docs
pytest tests/                       # run tests
```

## Project structure

```
core/deal_finder.py     shared business logic
scrapers/               reverb_scraper.py, ebay_scraper.py, thomann_scraper.py
utils/                  database.py, telegram.py, helpers.py
app.py                  FastAPI app
main.py                 CLI entry point
tests/                  pytest tests
```

## Known limitations

- eBay and Thomann results are reference listings, not like-for-like matches:
  search is by keyword, so accessories can appear (title keyword filtering
  reduces but does not remove this)
- eBay condition labels are in German and don't map one-to-one to Reverb's
- Thomann shipping is a flat 9.90 EUR constant
- Reverb uses an unofficial endpoint and may change without notice

## Roadmap

- [ ] Docker + cloud deployment
- [ ] Scheduled runs (Airflow)
- [ ] Price-trend analysis notebook on `price_history`
- [ ] Smarter product matching across marketplaces

## Disclaimer

Personal, non-commercial, educational project. Not affiliated with Reverb,
eBay or Thomann. Scraping follows each site's robots.txt, with low request rates.