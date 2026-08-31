# Pedal Hunter

Automatically finds underpriced guitar pedal listings on Reverb.com by comparing 
active listings to recent sold prices — grouped by condition, so you're never 
comparing a mint pedal's price to a beat-up one's.

## Why

Manually browsing Reverb for a good deal means opening dozens of listings and 
guessing whether a price is actually good, based on gut feeling. Pedal Hunter 
automates that judgment call: it pulls real recent sold prices for the same 
search, calculates a fair median price *per condition*, and flags active 
listings priced meaningfully below that — so you only look at listings 
actually worth your time.

## How it works

1. Queries Reverb's GraphQL API for active listings matching a search term
2. Queries the same API for recently *sold* listings matching that search
3. Groups sold prices by condition (Mint, Excellent, Good, etc.) and calculates 
   a median price per condition — avoiding the mistake of blending prices 
   across very different conditions
4. Flags active listings priced below their condition's median, sorted by 
   biggest discount
5. Tracks previously-seen deals so you're only notified about new ones on 
   repeat runs, and automatically prunes deals older than 30 days

## Example output

Searching for: univibe
Found 93 active listings
Median sold price by condition:
Very Good: 181.75
Excellent: 206.04
Mint: 295.0
Brand New: 140.5
B-Stock: 418.66
Good: 240.69
New deals found: 3

==================================================
[1] MXR M68 Uni-Vibe Effect Pedal
💰 Price: 115.98 EUR
📉 Below Median: 124.71 EUR (51.8%)
📦 Condition: Good
🔗 https://reverb.com/item/101215603-mxr-m68-uni-vibe-effect-pedal


## Setup

```bash
git clone https://github.com/ErnestKucher/Guitar_pedal_hunter.git
cd Guitar_pedal_hunter
python -m venv venv
venv\Scripts\activate   # on Windows
pip install -r requirements.txt
```

## Usage

```bash
python main.py "univibe"
```

Replace `"univibe"` with any pedal name or search term.

## Tech stack

- **Python** — core logic
- **Requests** — HTTP calls to Reverb's GraphQL API
- **JSON** — lightweight persistence for tracking seen deals

## Roadmap

- [ ] Move deal storage from JSON to a proper database (SQLite)
- [ ] Add a FastAPI web interface for browsing deals and triggering searches
- [ ] Price history tracking and trend analysis (pandas + charts)
- [ ] Compare Reverb used prices against Thomann new prices

## Disclaimer

This project queries Reverb's public GraphQL endpoint for personal, 
non-commercial, educational use. It is not affiliated with or endorsed 
by Reverb.