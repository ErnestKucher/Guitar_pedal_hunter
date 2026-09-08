from main import normalize_query
from main import deduplicate
from scrapers.reverb_scraper import is_valid_listing

def test_normalize_query_lower_and_strip_combined():
    result = normalize_query("Fuzz Face")
    assert result == "fuzz face"

def test_normalize_query_strips_whitespace():
    result = normalize_query("     UnIvebe     ")
    assert result == "univebe"

def test_deduplicate_removes_duplicates_ids():
    listings = [
        {"id": "1", "title": "Listing 1"},
        {"id": "2", "title": "Listing 2"},
        {"id": "1", "title": "Listing 1 Duplicate"},
    ]
    result = deduplicate(listings)
    assert len(result) == 2

def test_deduplicate_empty_list():
    listings = []
    result = deduplicate(listings)
    assert result == []

def test_deduplicate_is_missing_id():
    listings = [
        {"title": "Listing 1"},
        {"id": "2", "title": "Listing 2"},
        {"id": "1", "title": "Listing 1 Duplicate"},
    ]
    result = deduplicate(listings)
    assert len(result) == 2