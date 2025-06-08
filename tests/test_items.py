from itemadapter import ItemAdapter
import pytest
from scrapy.http import HtmlResponse

from aparser.items import AssetsData
from aparser.items import MetaData
from aparser.items import PriceData
from aparser.items import ProductItem
from aparser.items import StockData


# -------------------
# PriceData tests
# -------------------


def test_price_data_discount_tag():
    item = PriceData(current=80.0, original=100.0)
    assert item["sale_tag"] == "Скидка 20%"


def test_price_data_no_discount():
    item = PriceData(current=100.0, original=100.0)
    assert ItemAdapter(item).get("sale_tag") is None


# -------------------
# StockData tests
# -------------------


def test_stock_data_defaults():
    item = StockData(in_stock=True)
    assert ItemAdapter(item).get("count") is None


def test_stock_data_with_count():
    item = StockData(in_stock=True, count=15)
    assert item["count"] == 15


# -------------------
# AssetsData tests
# -------------------


def test_assets_data_defaults():
    item = AssetsData(main_image="http://image.url")
    adapter = ItemAdapter(item)
    assert adapter.get("set_images") is None
    assert adapter.get("view360") is None
    assert adapter.get("video") is None


# -------------------
# MetaData tests
# -------------------


def test_metadata_casts_to_string():
    meta = MetaData()
    meta["views"] = 123
    assert meta["views"] == "123"


def test_metadata_none_becomes_empty_string():
    meta = MetaData()
    meta["description"] = None
    assert meta["description"] == ""


# -------------------
# ProductItem tests
# -------------------


@pytest.fixture
def product_item():
    return ProductItem(
        timestamp=0,
        RPC="RPC123",
        url="http://example.com",
        title="Test Product",
        marketing_tags=[],
        brand="TestBrand",
        section=["TestSection"],
        price_data=PriceData(current=10.0, original=20.0),
        stock=StockData(in_stock=True),
        assets=AssetsData(main_image="http://image.url"),
    )


def test_product_item_process_title_adds_color_volume(product_item):
    html = """
        <div class="color" data-value="Red"></div>
        <span class="volume">500ml</span>
    """
    response = HtmlResponse(url="http://example.com", body=html, encoding="utf-8")
    product_item.process_title(response)

    assert product_item["title"] == "Test Product, Red, 500ml"


def test_product_item_process_title_ignores_existing_data(product_item):
    product_item["title"] = "Test Product, Red, 500ml"

    html = """
        <div class="color" data-value="Red"></div>
        <span class="volume">500ml</span>
    """
    response = HtmlResponse(url="http://example.com", body=html, encoding="utf-8")
    product_item.process_title(response)

    assert product_item["title"] == "Test Product, Red, 500ml"  # unchanged


def test_product_item_count_variants(product_item):
    html = """
        <div class="variant-option" data-type="color"></div>
        <div class="variant-option" data-type="volume"></div>
        <div class="variant-option" data-type="something-else"></div>
    """
    response = HtmlResponse(url="http://example.com", body=html, encoding="utf-8")
    product_item.count_variants(response)

    assert product_item["variants"] == 2
