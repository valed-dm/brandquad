import logging
import random

from scrapy import Request
from scrapy import Spider
from scrapy.downloadermiddlewares.retry import RetryMiddleware


logger = logging.getLogger(__name__)


class DynamicProxyMiddleware(RetryMiddleware):
    """Proxy management middleware that automatically removes failing proxies.

    Inherits from RetryMiddleware to handle:
    - Failed proxy detection
    - Automatic proxy rotation
    - Request retry logic
    """

    def __init__(self, settings) -> None:
        super().__init__(settings)
        self.proxies: list[str] = settings.getlist("PROXY_LIST")

    @classmethod
    def from_crawler(cls, crawler) -> "DynamicProxyMiddleware":
        """Factory method for Scrapy middleware initialization."""
        return cls(crawler.settings)

    def _retry(self, request: Request, reason: str, spider: Spider) -> Request | None:
        """Handle proxy failure by removing bad proxy from rotation.

        Args:
            request: The failed request
            reason: Failure reason text
            spider: Current spider instance

        Returns:
            Either a retry Request or None
        """
        proxy: str | None = request.meta.get("proxy")
        if proxy in self.proxies:
            spider.logger.warning(f"Removing bad proxy: {proxy} (reason: {reason})")
            self.proxies.remove(proxy)
        return super()._retry(request, reason, spider)


class CategoryScopedProxyMiddleware:
    """Middleware that assigns proxies based on category index for consistency."""

    def __init__(self, proxies: list[str]) -> None:
        """
        Args:
            proxies: List of proxy URLs (e.g. ["http://proxy1:8080", ...])
        """
        self.proxies = proxies

    @classmethod
    def from_crawler(cls, crawler) -> "CategoryScopedProxyMiddleware":
        """Standard Scrapy middleware factory pattern."""
        return cls(crawler.settings.getlist("PROXY_LIST"))

    def process_request(self, request: Request, spider: Spider) -> None:
        """Assign proxy based on category index or random selection.

        Args:
            request: Outgoing request object
            spider: Current spider instance
        """
        if not self.proxies:
            return
        idx: int | None = request.cb_kwargs.get("category_index")
        if idx is not None:
            proxy: str = self.proxies[idx % len(self.proxies)]
        else:
            proxy = random.choice(self.proxies)
        request.meta["proxy"] = proxy
        logger.debug(f"Proxy assigned: {proxy}")
