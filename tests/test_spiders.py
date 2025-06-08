from unittest.mock import MagicMock

import scrapy
from scrapy import Request
from scrapy.http import TextResponse

from aparser.items import ProductItem
from aparser.spiders.aspider import AlkotekaSpider


async def test_start_method_starts_first_category(mock_config):
    spider = AlkotekaSpider()
    spider.config = mock_config

    gen = spider.start()
    req = await anext(gen)
    assert isinstance(req, scrapy.Request)
    assert "vodka" in req.url


def test_parse_api_yields_items_and_next_page(mock_config, response_factory):
    spider = AlkotekaSpider()
    spider.config = mock_config

    body = {
        "results": [{"id": 1, "title": "Test Vodka"}],
        "meta": {"current_page": 1, "has_more_pages": True},
    }

    response = response_factory(body)
    items = list(
        spider.parse_api(
            response, category_index=0, referer="https://alkoteka.com/catalog/vodka"
        )
    )

    product_items = [i for i in items if not isinstance(i, scrapy.Request)]
    requests = [i for i in items if isinstance(i, scrapy.Request)]

    assert len(product_items) == 1
    assert len(requests) == 1
    assert "page=2" in requests[0].url


def test_parse_api_handles_json_error(mock_config):
    spider = AlkotekaSpider()
    spider.config = mock_config

    response = TextResponse(
        url="https://fake.com",
        body=b"not-json",
        encoding="utf-8",
        request=Request(url="https://fake.com"),
    )

    results = list(spider.parse_api(response, category_index=0, referer="ref"))
    assert any(isinstance(i, scrapy.Request) for i in results)  # next category fallback


def test_chain_to_next_category_yields_next_request(mock_config):
    spider = AlkotekaSpider()
    spider.config = mock_config

    result = list(spider.chain_to_next_category(0))
    assert len(result) == 1
    assert isinstance(result[0], scrapy.Request)
    assert "whiskey" in result[0].url


def test_parse_products_extracts_items(mock_config, response_factory):
    spider = AlkotekaSpider()
    spider.config = mock_config

    body = {
        "results": [{"id": 42, "title": "Gin Tonic"}],
        "meta": {"current_page": 1},
    }

    response = response_factory(body)
    items = spider.parse_products(response, slug="gin")
    assert len(items) == 1
    assert isinstance(items[0], dict | scrapy.Item)


def test_parse_products_mocked():
    response = MagicMock(spec=TextResponse)
    response.url = "https://example.com/api"
    response.json.return_value = {"results": [{}], "meta": {"current_page": 1}}

    spider = AlkotekaSpider()
    spider.config = MagicMock()
    spider.config.CATEGORY_SLUGS = ["wine"]

    products = spider.parse_products(response, slug="wine")

    assert isinstance(products, list)
    assert len(products) == 1

    product = products[0]
    assert isinstance(product, ProductItem)
    product_dict = dict(product)

    assert product_dict["brand"] == "Unknown"
    assert product_dict["title"] == "None, None"
    assert product_dict["price_data"]["current"] == 0.0
