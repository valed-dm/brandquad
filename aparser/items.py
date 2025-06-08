from typing import Any

from scrapy import Field
from scrapy import Item
from scrapy.http import Response


class PriceData(Item):
    """Structured price information with automatic discount calculation.

    Attributes:
        current: Current selling price (required)
        original: Original price (required)
        sale_tag: Auto-generated discount tag when current < original (default: "")
    """

    current = Field(required=True)
    original = Field(required=True)
    sale_tag = Field(default="")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._calculate_sale_tag()

    def _calculate_sale_tag(self) -> None:
        """Auto-generates discount tag in format 'Скидка X%' when current < original."""
        if self["current"] < self["original"]:
            discount = round(100 - (self["current"] / self["original"]) * 100)
            self["sale_tag"] = f"Скидка {discount}%"


class StockData(Item):
    """Inventory status representation.

    Attributes:
        in_stock: Availability flag (required)
        count: Available quantity (default: 0)
    """

    in_stock = Field(required=True)
    count = Field(default=0)  # 0 if not applicable


class AssetsData(Item):
    """Product media assets container.

    Attributes:
        main_image: Primary image URL (required)
        set_images: List of alternate image URLs (default: [])
        view360: 360-degree view URLs (default: [])
        video: Product video URLs (default: [])
    """

    main_image = Field(required=True)  # URL to primary image
    set_images = Field(default_factory=list)  # Alternative images
    view360 = Field(default_factory=list)  # 360-view URLs
    video = Field(default_factory=list)  # Product video URLs


class MetaData(dict[str, str]):
    """String-only metadata dictionary with automatic value cleaning.

    Ensures all values are:
    - Converted to strings
    - Empty string if None
    """

    def __setitem__(self, key: str, value: Any) -> None:
        cleaned_value = str(value) if value is not None else ""
        super().__setitem__(key, cleaned_value)


class ProductItem(Item):
    """Complete product data structure with helpers.

    Attributes:
        timestamp: Unix timestamp (required)
        RPC: Product code (required)
        title: Product name (required)
        price_data: PriceData instance (required)
        stock: StockData instance (required)
        variants: Count of color/volume options (default: 1)
    """

    timestamp = Field(required=True)
    RPC = Field(required=True)
    url = Field(required=True)
    title = Field(required=True)
    marketing_tags = Field(default_factory=list)
    brand = Field(required=True)
    section = Field(required=True)
    price_data = Field(required=True)
    stock = Field(required=True)
    assets = Field(required=True)
    metadata = Field(default=MetaData)
    variants = Field(default=1)

    def process_title(self, response: Response) -> None:
        """Appends missing color/volume to title if detected in response.

        Args:
            response: Scrapy Response containing product page HTML
        """
        color = response.css(".color::attr(data-value)").get()
        volume = response.css(".volume::text").get()

        if (color or volume) and not any(
            x in self["title"] for x in (color, volume) if x
        ):
            self["title"] = (
                f"{self['title']}, {', '.join(filter(None, [color, volume]))}"
            )

    def count_variants(self, response: Response) -> None:
        """Calculates variants based on color/volume options in response.

        Args:
            response: Scrapy Response containing variant options
        """
        variants = response.css(".variant-option::attr(data-type)").getall()
        self["variants"] = sum(1 for v in variants if v in ("color", "volume"))
