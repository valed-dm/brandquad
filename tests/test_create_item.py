import time

from aparser.item_factories.alkoteka_factory import create_item_from_api
from aparser.items import ProductItem


def test_create_item_from_api_basic():
    now = int(time.time())

    api_data = {
        "vendor_code": "123",
        "product_url": "https://example.com/product/123",
        "name": "Vodka",
        "subname": "Premium",
        "price": 100.0,
        "prev_price": 120.0,
        "available": True,
        "quantity_total": 5,
        "image_url": "https://example.com/image.jpg",
        "category": {
            "name": "Vodka",
            "parent": {"name": "Alcohol"},
        },
        "action_labels": [{"text": "Discount"}, {"text": ""}],
        "filter_labels": [
            {"filter": "volume", "title": "0.5L"},
            {"filter": "origin", "title": "Russia"},
        ],
    }

    item = create_item_from_api(api_data)

    assert isinstance(item, ProductItem)
    assert item["RPC"] == "123"
    assert item["url"] == "https://example.com/product/123"
    assert item["title"] == "Vodka, Premium"
    assert item["marketing_tags"] == ["Discount"]
    assert item["brand"] == "Unknown"
    assert item["section"] == ["Alcohol", "Vodka"]
    assert item["price_data"]["current"] == 100.0
    assert item["price_data"]["original"] == 120.0
    assert item["stock"]["in_stock"] is True
    assert item["stock"]["count"] == 5
    assert item["assets"]["main_image"] == "https://example.com/image.jpg"
    assert item["assets"]["set_images"] == []
    assert item["variants"] == 1
    assert item["metadata"]["volume"] == "0.5L"
    assert item["metadata"]["origin"] == "Russia"
    assert item["metadata"]["__description"] == ""
    assert abs(item["timestamp"] - now) <= 2  # within 2 seconds of now


def test_create_item_from_api_missing_fields():
    api_data = {}

    item = create_item_from_api(api_data)

    assert item["RPC"] == "None"
    assert item["url"] is None
    assert item["title"] == "None, None"
    assert item["marketing_tags"] == []
    assert item["brand"] == "Unknown"
    assert item["section"] == []
    assert item["price_data"]["current"] == 0.0
    assert item["price_data"]["original"] == 0.0
    assert item["stock"]["in_stock"] is False
    assert item["stock"]["count"] == 0
    assert item["assets"]["main_image"] is None
    assert item["assets"]["set_images"] == []
    assert item["metadata"]["__description"] == ""
