import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.parse import urljoin

import scrapy


class TestSpider(scrapy.Spider):
    name = "test"

    async def start(self):
        self.logger.info("Test spider is working!")
        yield scrapy.Request("https://example.com", self.parse)

    async def parse(self, response, **kwargs):
        self.logger.info(f"Got response from {response.url}")


class AlkotekaReconSpider(scrapy.Spider):
    name = "alkoteka_recon"

    # === CONTROL PANEL ===
    # Change the MODE to test different theories. Start with 1, then 2, then 3.
    MODE = 1
    # =====================

    # --- Target Configuration ---
    TARGET_SLUG = "produkty-1"
    CITY_UUID = "985b3eea-46b4-11e7-83ff-00155d026416"  # Krasnodar
    BASE_URL = "https://alkoteka.com"

    # --- A Simple, Generic User-Agent ---
    SIMPLE_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        " (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
    }

    async def start(self):
        # --- THEORY 1: The Simplest Direct API Call ---
        if self.MODE == 1:
            self.logger.info(
                "--- TESTING MODE 1: Direct API call with simple headers ---"
            )
            params = {
                "city_uuid": self.CITY_UUID,
                "page": "1",
                "per_page": "20",
                "root_category_slug": self.TARGET_SLUG,
            }
            api_url = (
                urljoin(self.BASE_URL, "/web-api/v1/product") + "?" + urlencode(params)
            )
            headers = self.SIMPLE_HEADERS.copy()
            headers["Referer"] = urljoin(self.BASE_URL, f"/catalog/{self.TARGET_SLUG}")

            yield scrapy.Request(
                url=api_url, headers=headers, callback=self.parse_debug
            )

        # --- THEORY 2: The Minimalist Two-Step Dance (Get Session, then API) ---
        elif self.MODE == 2:
            self.logger.info("--- TESTING MODE 2: Minimalist Two-Step Dance ---")
            self.logger.info("Step 2a: Visiting catalog page to get session cookie.")
            catalog_url = urljoin(self.BASE_URL, f"/catalog/{self.TARGET_SLUG}")
            yield scrapy.Request(
                url=catalog_url,
                headers=self.SIMPLE_HEADERS,
                callback=self.fire_simple_api_request,
                cb_kwargs={"referer": catalog_url},
            )

        # --- THEORY 3: The Minimalist Three-Step Dance (Age Gate) ---
        elif self.MODE == 3:
            self.logger.info(
                "--- TESTING MODE 3: Minimalist Three-Step Dance (Age Gate) ---"
            )
            self.logger.info("Step 3a: Visiting main page for initial session.")
            yield scrapy.Request(
                url=self.BASE_URL,
                headers=self.SIMPLE_HEADERS,
                callback=self.confirm_simple_age,
            )

    def fire_simple_api_request(self, response, referer):
        self.logger.info("Step 2b: Firing API request with session cookie.")
        params = {
            "city_uuid": self.CITY_UUID,
            "page": "1",
            "per_page": "20",
            "root_category_slug": self.TARGET_SLUG,
        }
        api_url = (
            urljoin(self.BASE_URL, "/web-api/v1/product") + "?" + urlencode(params)
        )
        headers = self.SIMPLE_HEADERS.copy()
        headers["Referer"] = referer
        yield scrapy.Request(url=api_url, headers=headers, callback=self.parse_debug)

    def confirm_simple_age(self, response):
        self.logger.info("Step 3b: Sending minimalist age confirmation.")
        age_confirm_url = urljoin(self.BASE_URL, "/api/common/confirm-age")
        xsrf_token = response.css('meta[name="csrf-token"]::attr(content)').get()
        headers = self.SIMPLE_HEADERS.copy()
        headers["Referer"] = self.BASE_URL + "/"
        headers["X-Requested-With"] = "XMLHttpRequest"
        headers["X-XSRF-TOKEN"] = xsrf_token

        yield scrapy.Request(
            url=age_confirm_url,
            method="POST",
            headers=headers,
            body=json.dumps({}),
            callback=self.start_simple_category_crawl,
        )

    def start_simple_category_crawl(self, response):
        self.logger.info("Step 3c: Age confirmed. Now visiting catalog page.")
        catalog_url = urljoin(self.BASE_URL, f"/catalog/{self.TARGET_SLUG}")
        yield scrapy.Request(
            url=catalog_url,
            headers=self.SIMPLE_HEADERS,
            callback=self.fire_simple_api_request,
            cb_kwargs={"referer": catalog_url},
        )

    def parse_debug(self, response):
        self.logger.info(f"--- RESULTS FOR MODE {self.MODE} ---")
        self.logger.info(
            f"Received response with status: {response.status} from {response.url}"
        )

        output_file = Path(f"debug_response_mode_{self.MODE}.json")
        output_file.write_bytes(response.body)
        self.logger.info(f"Full response saved to {output_file.resolve()}")

        try:
            data = response.json()
            products = data.get("data", [])
            if products:
                self.logger.critical(
                    f"!!!!!!!!!! SUCCESS on MODE {self.MODE} !!!!!!!!!!!"
                )
                self.logger.critical(
                    f"Found {len(products)} products. This is the winning strategy."
                )
            else:
                self.logger.error(
                    f"FAILURE on MODE {self.MODE}: API response was valid JSON"
                    f" but contained no products."
                )
        except Exception as e:
            self.logger.error(
                f"FAILURE on MODE {self.MODE}: Could not parse response as JSON."
                f" Error: {e}"
            )
