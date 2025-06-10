import time
from typing import Any

from aparser.items import AssetsData
from aparser.items import MetaData
from aparser.items import PriceData
from aparser.items import ProductItem
from aparser.items import StockData


def create_item_from_api(api_data: dict[str, Any]) -> ProductItem:
    """Transform API response into a validated ProductItem.

    Args:
        api_data: Raw API response containing product details

    Returns:
        ProductItem: Structured product data with:
            - Basic info (title, URL, brand)
            - Pricing data (current/original prices)
            - Stock availability
            - Categorized metadata

    Example:
        >>> api_response = {"name": "Vodka", "price": 1500}
        >>> item = create_item_from_api(api_response)
        >>> item["title"]
        'Vodka'
    """
    category_info = api_data.get("category", {})
    parent_category_info = category_info.get("parent", {})

    item = ProductItem(
        timestamp=int(time.time()),
        RPC=str(api_data.get("vendor_code")),
        url=api_data.get("product_url"),
        title=f"{api_data.get('name')}, {api_data.get('subname')}".strip(", "),
        marketing_tags=[
            label.get("text")
            for label in api_data.get("action_labels", [])
            if label.get("text")
        ],
        brand="Unknown",  # Default if not provided
        section=list(
            filter(None, [parent_category_info.get("name"), category_info.get("name")])
        ),
        price_data=PriceData(
            current=float(api_data.get("price", 0)),
            original=float(api_data.get("prev_price") or api_data.get("price", 0)),
        ),
        stock=StockData(
            in_stock=api_data.get("available", False),
            count=int(api_data.get("quantity_total") or 0),
        ),
        assets=AssetsData(
            main_image=api_data.get("image_url"),
            set_images=[],  # Populated separately if available
        ),
        metadata=MetaData(),  # Initialized empty
        variants=1,  # Default single variant
    )

    # Parse filter labels into metadata
    for label in api_data.get("filter_labels", []):
        key = label.get("filter")
        value = label.get("title")
        if key and value:
            item["metadata"][key] = value

    item["metadata"]["__description"] = ""  # Placeholder

    return item
