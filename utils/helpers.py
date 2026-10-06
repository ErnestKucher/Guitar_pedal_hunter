from config.configurations import EXCLUDED_TITLE_KEYWORDS

def to_float(value):
    try:
        if value is None:
            return None
        return float(value)
    except (ValueError, TypeError):
        return None

def is_valid_listing(listing):
    title = listing.get("title", "").lower()

    for keyword in EXCLUDED_TITLE_KEYWORDS:
        if keyword in title:
            return False

    return True