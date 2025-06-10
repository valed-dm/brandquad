from io import BytesIO
from typing import Any
from typing import BinaryIO
from typing import Dict
from typing import Optional
from typing import Union
from typing import cast

from itemadapter import ItemAdapter
from scrapy.exporters import JsonItemExporter
from scrapy.item import Item


class CustomJsonItemExporter(JsonItemExporter):
    """JSON exporter that handles Scrapy Items and None values safely.

    Features:
    - Automatic conversion of Scrapy Items to dictionaries
    - Silent skipping of None values
    - Configurable ASCII escaping (default: False)
    - Type-safe file handling
    """

    def __init__(self, file: BinaryIO, **kwargs: Any) -> None:
        """Initialize exporter with JSON-specific settings.

        Args:
            file: Binary file handle for output
            kwargs: Additional exporter options:
                - ensure_ascii: Force ASCII escaping (default: False)
                - indent: Pretty-printing indentation
        """
        kwargs["ensure_ascii"] = kwargs.get("ensure_ascii", False)
        super().__init__(cast(BytesIO, file), **kwargs)

    def export_item(self, item: Optional[Union[Item, Dict[str, Any]]]) -> None:
        """Process and export a single item to JSON format.

        Handles:
        - None values (silently skips)
        - Scrapy Item objects (converts to dict)
        - Regular dictionaries (passed through)

        Args:
            item: Data to export. Can be:
                - None (skipped)
                - Scrapy Item
                - Dictionary
        """
        if item is None:
            return

        if hasattr(item, "items"):
            item = dict(ItemAdapter(item).asdict())

        super().export_item(item)
