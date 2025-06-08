"""
Dynamic proxy removal during _retry.
Correct proxy assignment based on category_index.
Fallback to random.choice() when index is missing.
Graceful no-op behavior when no proxies are available.
"""

import logging
from unittest.mock import MagicMock

import pytest
from scrapy.http import Request
from scrapy.settings import Settings
from scrapy.spiders import Spider

from aparser.middlewares import CategoryScopedProxyMiddleware
from aparser.middlewares import DynamicProxyMiddleware


class DummySpider(Spider):
    name = "dummy"

    def __init__(self):
        super().__init__()
        self.crawler = MagicMock()


@pytest.fixture
def proxy_list():
    return ["http://proxy1", "http://proxy2", "http://proxy3"]


def test_dynamic_proxy_removal_on_retry(proxy_list, caplog):
    spider = DummySpider()
    settings = Settings({"PROXY_LIST": proxy_list.copy()})

    crawler = MagicMock()
    crawler.settings = settings

    middleware = DynamicProxyMiddleware.from_crawler(crawler)

    request = Request(url="http://example.com", meta={"proxy": "http://proxy2"})
    reason = Exception("Connection failed")

    with caplog.at_level(logging.WARNING):
        middleware._retry(request, reason, spider)

    assert "http://proxy2" not in middleware.proxies
    assert "Removing bad proxy: http://proxy2" in caplog.text


def test_category_scoped_proxy_selection(proxy_list, caplog):
    settings = Settings({"PROXY_LIST": proxy_list.copy()})
    crawler = MagicMock()
    crawler.settings = settings

    middleware = CategoryScopedProxyMiddleware.from_crawler(crawler)

    request = Request(
        url="http://example.com", cb_kwargs={"category_index": 1}, meta={}
    )
    spider = DummySpider()

    with caplog.at_level(logging.DEBUG):
        middleware.process_request(request, spider)

    assert "proxy" in request.meta
    assert request.meta["proxy"] == proxy_list[1]
    assert "Proxy assigned:" in caplog.text


def test_category_scoped_proxy_random_when_no_index(proxy_list):
    middleware = CategoryScopedProxyMiddleware(proxy_list)

    request = Request(url="http://example.com", meta={}, cb_kwargs={})
    spider = DummySpider()

    middleware.process_request(request, spider)

    assert request.meta["proxy"] in proxy_list


def test_category_scoped_proxy_no_proxies_does_nothing():
    middleware = CategoryScopedProxyMiddleware([])

    request = Request(url="http://example.com", meta={}, cb_kwargs={})
    spider = DummySpider()

    result = middleware.process_request(request, spider)

    assert result is None
    assert "proxy" not in request.meta
