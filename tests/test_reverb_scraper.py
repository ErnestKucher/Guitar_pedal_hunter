from scrapers.reverb_scraper import is_valid_listing

def test_is_valid_listing_excluded_keyword():
    listing = {"title": "Fuzz Face clone"}
    result = is_valid_listing(listing)
    assert result is False

def test_is_valid_listing_no_excluded_keyword():
    listing = {"title": "Dunlop Fuzz Face mini"}
    result = is_valid_listing(listing)
    assert result is True

def test_is_valid_listing_empty_title():
    listing = {}
    result = is_valid_listing(listing)
    assert result is True