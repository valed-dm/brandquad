import io
import json

from scrapy import Field
from scrapy import Item

from aparser.exporters import CustomJsonItemExporter


class DummyItem(Item):
    name = Field()
    price = Field()


def test_export_dict_item():
    output = io.BytesIO()
    exporter = CustomJsonItemExporter(output)
    exporter.start_exporting()
    exporter.export_item({"name": "Apple", "price": 1.5})
    exporter.finish_exporting()

    result = json.loads(output.getvalue().decode("utf-8"))
    assert result == [{"name": "Apple", "price": 1.5}]


def test_export_scrapy_item():
    item = DummyItem(name="Banana", price=0.99)
    output = io.BytesIO()
    exporter = CustomJsonItemExporter(output)
    exporter.start_exporting()
    exporter.export_item(item)
    exporter.finish_exporting()

    result = json.loads(output.getvalue().decode("utf-8"))
    assert result == [{"name": "Banana", "price": 0.99}]


def test_export_none_item():
    output = io.BytesIO()
    exporter = CustomJsonItemExporter(output)
    exporter.start_exporting()
    exporter.export_item(None)
    exporter.finish_exporting()

    # should still be valid JSON (an empty list if nothing exported)
    result = json.loads(output.getvalue().decode("utf-8"))
    assert result == []
