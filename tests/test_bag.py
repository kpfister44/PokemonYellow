# ABOUTME: Tests bag inventory capacity and stacking rules
# ABOUTME: Covers countable vs non-countable item behavior

import pytest

from src.items.bag import Bag


class FakeItem:
    def __init__(self, countable: bool):
        self.countable = countable


def build_lookup(countable_ids: set[str]):
    def lookup(item_id: str) -> FakeItem:
        return FakeItem(item_id in countable_ids)
    return lookup


def test_bag_stacks_countable_items():
    bag = Bag(item_lookup=build_lookup({"potion"}))

    assert bag.add_item("potion") is True
    assert bag.add_item("potion") is True

    entries = bag.get_entries()
    assert len(entries) == 1
    assert entries[0].item_id == "potion"
    assert entries[0].quantity == 2


def test_bag_rejects_duplicate_non_countable_items():
    bag = Bag(item_lookup=build_lookup(set()))

    assert bag.add_item("bicycle") is True
    assert bag.add_item("bicycle") is False

    entries = bag.get_entries()
    assert len(entries) == 1
    assert entries[0].item_id == "bicycle"
    assert entries[0].quantity == 1


def test_bag_enforces_capacity_limit():
    bag = Bag(item_lookup=build_lookup(set()))

    for index in range(bag.MAX_SLOTS):
        assert bag.add_item(f"item-{index}") is True

    assert bag.add_item("item-overflow") is False
