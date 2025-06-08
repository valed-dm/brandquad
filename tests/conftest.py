import json
from unittest.mock import MagicMock

import pytest
from scrapy import Request
from scrapy.http import TextResponse


@pytest.fixture
def mock_config():
    return MagicMock(
        CITY_UUID="city123",
        CATEGORY_SLUGS=["vodka", "whiskey"],
        full_api_url="https://api.alkoteka.com/v1/products",
        HEADERS={"User-Agent": "test-agent"},
        BASE_URL="https://alkoteka.com",
    )


@pytest.fixture
def response_factory():
    def _create_response(body: dict, url="https://example.com/api", meta=None):
        return TextResponse(
            url=url,
            request=Request(url, meta=meta or {}),
            body=json.dumps(body).encode("utf-8"),
            encoding="utf-8",
        )

    return _create_response
