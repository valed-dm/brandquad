from scrapy import Item
from scrapy import Spider
from scrapy.exceptions import DropItem


class ItemPreparationPipeline:
    """Pipeline that prepares Items for serialization by converting nested Items
     to dicts.

    Ensures all nested Item objects (e.g., PriceData, StockData) are converted to plain
    dictionaries before reaching exporters. This prevents serialization errors in
    JSON/CSV exporters.
    """

    @staticmethod
    def process_item(item: Item, spider: Spider) -> Item:
        """Convert all nested Item objects within the item to dictionaries.

        Args:
            item: The scraped item to process
            spider: The spider that scraped the item

        Returns:
            The same item with all nested Items converted to dicts

        Raises:
            DropItem: If the input item is None
        """
        if item is None:
            raise DropItem("Received None item")

        for field, value in item.items():
            if hasattr(value, "items"):  # Check if it's a Scrapy Item or similar
                item[field] = dict(value)

        return item
