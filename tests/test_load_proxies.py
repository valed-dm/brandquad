from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from requests import RequestException
from requests import Timeout
from requests.exceptions import SSLError

from aparser.core import load_proxies


@pytest.mark.parametrize(
    "response_text,expected_count",
    [
        ("1.1.1.1:80\n2.2.2.2:8080\n", 2),
        ("", 0),
    ],
)
@patch("aparser.core.load_proxies.requests.get")
def test_fetch_proxy_list(mock_get, response_text, expected_count):
    mock_resp = MagicMock()
    mock_resp.text = response_text
    mock_get.return_value = mock_resp

    proxies = load_proxies.fetch_proxy_list(limit=10)
    assert all(p.startswith("http://") for p in proxies)
    assert len(proxies) == min(expected_count, 10)


@patch("aparser.core.load_proxies.requests.get")
def test_check_proxy_success(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_get.return_value = mock_resp

    assert load_proxies.check_proxy("http://fakeproxy") is True


@patch("aparser.core.load_proxies.requests.get")
def test_check_proxy_failure_due_to_status(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 500
    mock_get.return_value = mock_resp

    assert load_proxies.check_proxy("http://fakeproxy") is False


@patch("aparser.core.load_proxies.requests.get")
def test_check_proxy_exception(mock_get):
    mock_get.side_effect = RequestException("Simulated timeout")
    assert load_proxies.check_proxy("http://fakeproxy") is False


@pytest.mark.parametrize(
    "exception", [RequestException("Timeout"), ConnectionError(), Timeout(), SSLError()]
)
def test_check_proxy_various_exceptions(exception):
    with patch("aparser.core.load_proxies.requests.get", side_effect=exception):
        assert load_proxies.check_proxy("http://fakeproxy") is False


@patch("aparser.core.load_proxies.fetch_proxy_list")
@patch("aparser.core.load_proxies.check_proxy")
def test_build_valid_proxy_pool(mock_check_proxy, mock_fetch_proxy_list):
    mock_fetch_proxy_list.return_value = [
        "http://proxy1",
        "http://proxy2",
        "http://proxy3",
    ]
    # Let's say only proxy1 and proxy3 are valid
    mock_check_proxy.side_effect = lambda p: p in ("http://proxy1", "http://proxy3")

    result = load_proxies.build_valid_proxy_pool()

    assert set(result) == {"http://proxy1", "http://proxy3"}
