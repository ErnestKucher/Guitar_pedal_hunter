# Pedal Hunter

Finds underpriced used guitar pedals on Reverb by comparing active listings
with condition-specific sold-price medians, then sends the best deals to
Telegram together with reference prices from eBay and Thomann.

Built as a learning project to practice web scraping, API integration,
SQL, testing and backend structure.

## Why

Checking whether a used pedal is a good deal means opening many listings and
guessing. Pedal Hunter automates that: it pulls recent sold prices, computes a
fair median per condition (a "Mint" and a "Good" pedal are never compared
against each other), and flags active listings priced below that median.

## Features

- **Reverb:** active and sold listings from Reverb's GraphQL endpoint, with
  retries, rate-limit handling and polite delays
- **Per-condition medians:** a listing is flagged only if it is cheaper than
  the median sold price for its own condition
- **SQLite storage**
  - `seen_deals`: no repeat notifications, entries pruned after 30 days
  - `price_history`: Reverb (active and sold) and Thomann (new) prices, tagged
    by `source`. Each sold listing is stored once, each active listing once
    per day, enforced by unique indexes
- **eBay:** official Browse API with the OAuth2 client-credentials flow
- **Thomann:** search results parsed from the page's embedded `dataLayer` JSON
- **Telegram notifications** with the top deals and reference prices
- **Failure isolation:** if eBay or Thomann fail, the Reverb alert still works
- **FastAPI** endpoints: `/`, `/deals`, `/search?query=...`
- **Tests:** pytest suite (16 tests) for the parsing, filtering and matching logic

## How it works

1. Scrape active and sold listings from Reverb and deduplicate them
2. Group sold prices by condition and compute the median for each
3. Flag active listings priced below their condition's median
4. Fetch reference listings from eBay and Thomann for the same query, and keep
   only titles that contain every word of the query
5. Save prices to `price_history`, and new deals to `seen_deals`
6. Send a Telegram summary

The same logic in `core/deal_finder.py` serves both the command line and the API.

## Example notification

```
***New undervalued listings found for 'fuzz face mini' in Reverb***

[1] Dunlop FFM1 Si Fuzz Face Mini Silicon Distortion
Price:         150.98 EUR
Below Median:  56.32 EUR (27.2%)
Condition:     Mint
URL: https://reverb.com/item/...

***Similar listings available on Thomann***
[1] Dunlop Jimi Hendrix Fuzz Face Mini
Price: 186.90 EUR
URL: (https://www.thomannmusic.com/...)
```

## Setup

```bash
git clone https://github.com/ErnestKucher/Guitar_pedal_hunter.git
cd Guitar_pedal_hunter
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy .env.example .env         # then fill in your values
python -m utils.database       # creates the SQLite tables
```

### Environment variables

| Variable | Where to get it |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Create a bot with @BotFather on Telegram |
| `TELEGRAM_CHAT_ID` | Send your bot a message, then open `https://api.telegram.org/bot<TOKEN>/getUpdates` and read `chat.id` |
| `EBAY_PROD_CLIENT_ID`, `EBAY_PROD_CLIENT_SECRET` | Production keys from the eBay developer portal |

**eBay note:** Production keys only work after you open the keyset's
*Notifications* page and choose "Exempted from Marketplace Account Deletion"
with the reason "I do not persist eBay data". Until then, token requests fail
with `invalid_client`.

## Usage

```bash
python main.py "mxr uni vibe"     # search from the command line
python show_seen.py               # list saved deals
uvicorn app:app --reload          # API, interactive docs at /docs
pytest tests/                     # run the tests
```

## Project structure

```
core/deal_finder.py   shared business logic (CLI and API)
scrapers/             reverb_scraper.py, ebay_scraper.py, thomann_scraper.py
utils/                database.py, telegram.py, helpers.py
config/               configurations.py (keyword filters), GraphQL queries
app.py                FastAPI app
main.py               command-line entry point
tests/                pytest tests
data/                 SQLite database (created on first run, not committed)
```

## Known limitations

- Search matching is strict: every query word must appear in the title, so
  "univibe" will not match "Uni-Vibe"
- eBay and Thomann results are reference listings, not like-for-like matches.
  Title keyword filtering reduces accessories and unrelated items but does not
  remove them
- eBay results are shown in the alert but not stored in `price_history`,
  because keyword search results are too noisy for trend analysis
- eBay condition labels are in German and do not map one-to-one to Reverb's
- Thomann shipping is a flat 9.90 EUR constant, included in the stored total
- Thomann and eBay are read from a single page of results
- Runs are manual for now

## What I learned

- Three kinds of data source: an undocumented GraphQL endpoint (Reverb),
  an official OAuth2 API (eBay) and a server-rendered page (Thomann)
- Designing SQLite tables and using partial unique indexes with
  `INSERT OR IGNORE` to prevent duplicate rows
- Separating shared logic from entry points, and testing it with pytest
- Keeping secrets out of the repository, and verifying the setup
  with a fresh clone

## Roadmap

- [ ] Scheduled daily runs, so `price_history` accumulates data
- [ ] Price-trend analysis notebook (SQL and pandas) on `price_history`
- [ ] Parallel requests to the three sources
- [ ] Docker and cloud deployment
- [ ] Smarter product matching across marketplaces

## Disclaimer

Personal, non-commercial, educational project. Not affiliated with Reverb,
eBay or Thomann. eBay data comes from its official Browse API. Thomann's
`robots.txt` was reviewed, and only public search pages are requested at a
low rate. Reverb data comes from a GraphQL endpoint used by its website,
which is undocumented and may change or be restricted at any time.