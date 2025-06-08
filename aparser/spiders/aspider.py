import json
import logging
from typing import Any
from typing import AsyncGenerator
from typing import Generator
from typing import cast
from urllib.parse import urlencode
from urllib.parse import urljoin

import scrapy
from scrapy import Request
from scrapy.http import Response
from scrapy.http import TextResponse

from aparser.core.config import aconfig
from aparser.item_factories.alkoteka_factory import create_item_from_api
from aparser.items import ProductItem


logger = logging.getLogger(__name__)


class AlkotekaSpider(scrapy.Spider):
    """Scrapy spider for crawling alkoteka.com product API with async support.

    Requires TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
    Features:
    - Sequential category crawling
    - Automatic pagination
    - API response validation
    - Error-resilient parsing
    """

    name = "alkoteka"
    allowed_domains = ["alkoteka.com"]

    PER_PAGE = "50"
    KEY_PAGE = "current_page"
    KEY_HAS_MORE = "has_more_pages"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize spider with configuration."""
        super().__init__(*args, **kwargs)
        self.config = aconfig

    async def start(self) -> AsyncGenerator[Request, Any]:
        """Initiate crawling by requesting the first category.

        Yields:
            First category request or logs warning if no categories configured.
        """
        if not self.config.CATEGORY_SLUGS:
            self.logger.warning("No categories to scrape.")
            return

        # Start the chain with the first category (index 0)
        yield self.create_category_request(category_index=0)

    def build_api_url(self, slug: str, page: int = 1) -> str:
        """Construct API URL with query parameters.

        Args:
            slug: Category identifier
            page: Pagination number

        Returns:
            Complete API URL with encoded parameters
        """
        params = {
            "city_uuid": self.config.CITY_UUID,
            "page": str(page),
            "per_page": self.PER_PAGE,
            "root_category_slug": slug,
        }
        return f"{self.config.full_api_url}?{urlencode(params)}"

    def build_headers(self, referer_slug: str) -> dict[str, str]:
        """Generate request headers with dynamic Referer.

        Args:
            referer_slug: Category slug for Referer header

        Returns:
            Headers dictionary with configured User-Agent and Referer
        """
        headers = self.config.HEADERS.copy()
        headers["Referer"] = urljoin(
            str(self.config.BASE_URL), f"/catalog/{referer_slug}"
        )
        return headers

    def handle_pagination(
        self, meta: dict, slug: str, category_index: int, referer: str
    ) -> Request | None:
        """Generate next page request if more pages exist.

        Args:
            meta: API response metadata
            slug: Current category slug
            category_index: Position in category list
            referer: Referer URL for headers

        Returns:
            Next page Request if available, else None
        """
        if meta.get(self.KEY_HAS_MORE) is True:
            next_page = int(meta.get(self.KEY_PAGE, 1)) + 1
            self.logger.info(f"Paginating to page {next_page} for '{slug}'...")

            url = self.build_api_url(slug, next_page)
            headers = self.build_headers(referer_slug=slug)

            return scrapy.Request(
                url=url,
                headers=headers,
                callback=self.parse_api,
                cb_kwargs={
                    "category_index": category_index,
                    "referer": headers["Referer"],
                },
            )
        return None

    def create_category_request(self, category_index: int) -> Request:
        """Generate initial request for a category.

        Args:
            category_index: Position in CATEGORY_SLUGS list

        Returns:
            Configured Request for the category's first page
        """
        slug = self.config.CATEGORY_SLUGS[category_index]
        self.logger.info(f"--- Starting crawl for new category: '{slug}' ---")

        url = self.build_api_url(slug, page=1)
        headers = self.build_headers(referer_slug=slug)

        return scrapy.Request(
            url=url,
            headers=headers,
            callback=self.parse_api,
            cb_kwargs={"category_index": category_index, "referer": headers["Referer"]},
        )

    def parse_api(
        self, response: Response, category_index: int, referer: str
    ) -> Generator[Request | ProductItem, Any, None]:
        """Process API response and handle pagination/category chaining.

        Args:
            response: API response
            category_index: Current category position
            referer: Referer URL

        Yields:
            ProductItems or next page/category requests
        """
        response = cast(TextResponse, response)
        try:
            slug = self.config.CATEGORY_SLUGS[category_index]
        except IndexError:
            self.logger.error(f"Invalid category index: {category_index}")
            return

        products = self.parse_products(response, slug)
        for item in products:
            yield item

        try:
            meta = response.json().get("meta", {})
        except json.JSONDecodeError:
            yield from self.chain_to_next_category(category_index)
            return

        next_page_request = self.handle_pagination(meta, slug, category_index, referer)
        if next_page_request:
            yield next_page_request
        else:
            yield from self.chain_to_next_category(category_index)

    def chain_to_next_category(
        self,
        current_category_index: int,
    ) -> Generator[Request | ProductItem, Any, None]:
        """Transition to the next category or complete crawl.

        Args:
            current_category_index: Completed category position

        Yields:
            Next category request if available
        """
        slug = self.config.CATEGORY_SLUGS[current_category_index]
        self.logger.info(f"Finished all pages for category '{slug}'.")
        next_category_index = current_category_index + 1
        if next_category_index < len(self.config.CATEGORY_SLUGS):
            # Chain to the next category in the list.
            yield self.create_category_request(category_index=next_category_index)
        else:
            self.logger.info("--- All categories have been crawled successfully! ---")

    def parse_products(self, response: TextResponse, slug: str) -> list[ProductItem]:
        """Extract and transform product data from API response.

        Args:
            response: API response
            slug: Category identifier

        Returns:
            List of validated ProductItems
        """
        try:
            data = response.json()
        except json.JSONDecodeError:
            self.logger.error(
                f"Failed to parse JSON for slug '{slug}' — {response.url}"
            )
            return []

        products_data = data.get("results", [])
        current_page = data.get("meta", {}).get(self.KEY_PAGE, 1)

        if products_data:
            self.logger.info(
                f"SUCCESS: Found {len(products_data)} products for '{slug}'"
                f" on page {current_page}."
            )
        else:
            self.logger.warning(
                f"No products found for slug: {slug} on page {current_page}."
            )

        return [create_item_from_api(blob) for blob in products_data]
