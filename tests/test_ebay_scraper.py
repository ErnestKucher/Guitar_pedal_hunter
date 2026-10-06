from scrapers.ebay_scraper import parse_ebay_item

def test_parse_ebay_item_normal():
    item = {
        "itemId": "v1|123|0",
        "title": "MXR Uni-Vibe",
        "condition": "Gebraucht",
        "conditionId": "3000",
        "price": {"value": "150.00", "currency": "EUR"},
        "shippingOptions": [{"shippingCost": {"value": "10.00", "currency": "EUR"}}],
        "itemWebUrl": "https://www.ebay.de/itm/123"
    }
    result = parse_ebay_item(item)
    assert result["price"] == 150.0
    assert result["shipping"] == 10.0
    assert result["total_price"] == 160.0

def test_parse_ebay_item_missing_price():
    item = {
        "itemId": "v1|123|0",
        "title": "MXR Uni-Vibe",
        "condition": "Gebraucht",
        "conditionId": "3000",
        "shippingOptions": [{"shippingCost": {"value": "10.00", "currency": "EUR"}}],
        "itemWebUrl": "https://www.ebay.de/itm/123"
    }
    result = parse_ebay_item(item)
    assert result["price"] is None
    assert result["total_price"] is None

def test_parse_ebay_item_missing_shipping():
    item = {
        "itemId": "v1|123|0",
        "title": "MXR Uni-Vibe",
        "condition": "Gebraucht",
        "conditionId": "3000",
        "price": {"value": "150.00", "currency": "EUR"},
        "itemWebUrl": "https://www.ebay.de/itm/123"
    }
    result = parse_ebay_item(item)
    assert result["price"] == 150.0
    assert result["shipping"] is None
    assert result["total_price"] is None