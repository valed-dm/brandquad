import pytest
from scrapy import Field
from scrapy import Item
from scrapy.exceptions import DropItem
from scrapy.spiders import Spider

from aparser.pipelines import ItemPreparationPipeline


# Fake nested item
class NestedItem(Item):
    foo = Field()
    bar = Field()


# Fake outer item
class ProductItem(Item):
    name = Field()
    nested = Field()


class DummySpider(Spider):
    name = "dummy"


def test_pipeline_converts_nested_items_to_dicts():
    pipeline = ItemPreparationPipeline()
    spider = DummySpider()

    nested = NestedItem(foo="abc", bar=123)
    item = ProductItem(name="Test Item", nested=nested)

    result = pipeline.process_item(item, spider)

    assert isinstance(result["nested"], dict)
    assert result["nested"]["foo"] == "abc"
    assert result["nested"]["bar"] == 123


def test_pipeline_raises_on_none():
    pipeline = ItemPreparationPipeline()
    spider = DummySpider()

    with pytest.raises(DropItem, match="Received None item"):
        pipeline.process_item(None, spider)
