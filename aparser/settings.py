from pathlib import Path

from aparser.core.load_proxies import build_valid_proxy_pool
from aparser.core.logger_setup import configure_logging


# ==============================================================================
# CORE PROJECT SETTINGS
# ==============================================================================
BOT_NAME = "aparser"
SPIDER_MODULES = ["aparser.spiders"]
NEWSPIDER_MODULE = "aparser.spiders"
USE_PROXIES = False
FEED_EXPORT_ENCODING = "utf-8"
FEED_EXPORT_INDENT = 4
FEED_STORE_EMPTY = False
FEED_OVERWRITE = True
FEED_EXPORTERS = {"json": "aparser.exporters.CustomJsonItemExporter"}

# The Twisted reactor is always a good idea for modern Scrapy projects.
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

# ==============================================================================
# DOWNLOADER MIDDLEWARES
# ==============================================================================
# By disabling the automatic User-Agent middlewares, we guarantee that the
# User-Agent we set in the spider's headers is the one that gets used.
DOWNLOADER_MIDDLEWARES = {
    "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": None,
    "scrapy_fake_useragent.middleware.RandomUserAgentMiddleware": None,
    "aparser.middlewares.DynamicProxyMiddleware": 745 if USE_PROXIES else None,
    "aparser.middlewares.CategoryScopedProxyMiddleware": 750 if USE_PROXIES else None,
}

# ==============================================================================
# CRAWLING POLITENESS & STRATEGY (AUTOTHROTTLE)
# This is the best way to handle servers sensitive to request rates.
# ==============================================================================
ROBOTSTXT_OBEY = False

# Enable and configure the AutoThrottle extension.
AUTOTHROTTLE_ENABLED = True

# The initial download delay (in seconds).
AUTOTHROTTLE_START_DELAY = 2.0

# The maximum download delay to be set in case of high latencies.
AUTOTHROTTLE_MAX_DELAY = 60.0

# The average number of requests Scrapy should be sending in parallel to
# each remote server. Setting this to 1.0 is a very strong and safe
# strategy against rate-limiters, reinforcing our spider's serial logic.
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0

# Enable showing throttling stats for every response received
# (optional, good for debugging).
AUTOTHROTTLE_DEBUG = True

# The DOWNLOAD_DELAY and CONCURRENT_REQUESTS_PER_DOMAIN settings are ignored
# when AutoThrottle is enabled. We set global CONCURRENT_REQUESTS as a safety net.
CONCURRENT_REQUESTS = 2

# ==============================================================================
# DATA HANDLING & PIPELINES
# ==============================================================================
ITEM_PIPELINES = {
    "aparser.pipelines.ItemPreparationPipeline": 100,
}

FEEDS = {
    "results.json": {
        "format": "json",
        "fields": [
            "timestamp",
            "RPC",
            "url",
            "title",
            "marketing_tags",
            "brand",
            "section",
            "price_data",
            "stock",
            "assets",
            "metadata",
            "variants",
        ],
        "item_export_kwargs": {
            "default": lambda x: "" if x is None else x,
            "ensure_ascii": False,
        },
        "overwrite": True,
    }
}

# ==============================================================================
# SESSION & ERROR HANDLING
# ==============================================================================
COOKIES_ENABLED = True
RETRY_ENABLED = True
RETRY_TIMES = 3
DOWNLOAD_TIMEOUT = 5

# ==============================================================================
# LOGGING (Custom Setup)
# Project uses a custom logging configuration.
# ==============================================================================
# Disable Scrapy's default logging configuration to allow custom setup.
LOG_ENABLED = False
LOG_FORMATTER = "aparser.core.logger_setup.SilentItemScrapedFormatter"

configure_logging(
    log_level="INFO",
    log_dir=str(Path(__file__).parent.parent / "logs"),
    log_file_name="aparser.log",
)

PROXY_LIST = build_valid_proxy_pool() if USE_PROXIES else []
