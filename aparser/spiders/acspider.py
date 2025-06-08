import json
from typing import Any
from typing import AsyncGenerator
from typing import Generator
from typing import cast
from urllib.parse import urlencode

import scrapy
from scrapy import Request
from scrapy.http import TextResponse


class CitySpider(scrapy.Spider):
    """Scrapy spider to fetch city metadata (UUIDs, slugs) from Alkoteka API.

    Features:
    - Pagination handling
    - UUID deduplication
    - Combined parsing of regular/accented cities
    - JSON response validation
    """

    name: str = "cities"
    allowed_domains: list[str] = ["alkoteka.com"]
    base_api_url: str = "https://alkoteka.com/web-api/v1/city"

    HEADERS: dict[str, str] = {
        "User-Agent": "Mozilla/5.0 (...) Chrome/125.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Referer": "https://alkoteka.com/",
    }

    async def start(self) -> AsyncGenerator[Request, None]:
        """Initiate city data collection.

        Yields:
            Initial API request with pagination parameters
        """
        params = {
            "city_uuid": "7188bf0b-6b63-11eb-80cd-00155d039009",  # Default city
            "per_page": "20",
        }
        url = self.base_api_url + "?" + urlencode(params)
        self.logger.info(f"Requesting city list from: {url}")
        yield scrapy.Request(url, headers=self.HEADERS, callback=self.parse)

    def parse(
        self, response: TextResponse, **kwargs: Any
    ) -> Generator[dict[str, Any] | Request, None, None]:
        """Process city API response with deduplication and pagination.

        Args:
            response: API response containing city data
            **kwargs: Additional callback arguments

        Yields:
            Dictionaries with city metadata (name, UUID, slug)
        """
        response = cast(TextResponse, response)
        self.logger.info(f"Fetched city data from {response.url}")

        try:
            response_data = response.json()
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parse failed: {e}")
            return

        all_cities = response_data.get("results", [])
        accented_cities = response_data.get("meta", {}).get("accented", [])
        combined = accented_cities + all_cities

        if not combined:
            self.logger.error(
                f"No city data found. Response keys: {response_data.keys()}"
            )
            return

        self.logger.info(f"Parsed {len(combined)} cities total")

        seen_uuids: set[str] = set()
        for city in combined:
            if not (city_uuid := city.get("uuid")):
                continue
            if city_uuid not in seen_uuids:
                seen_uuids.add(city_uuid)
                yield {
                    "name": city.get("name"),
                    "uuid": city_uuid,
                    "slug": city.get("slug"),
                }

        # Handle pagination
        if response_data.get("meta", {}).get("has_more_pages"):
            current_page = response_data["meta"].get("current_page", 1)
            next_page = current_page + 1
            self.logger.info(f"Paginating to city page {next_page}...")
            yield response.follow(
                f"{self.base_api_url}?page={next_page}",
                headers=self.HEADERS,
                callback=self.parse,
            )
