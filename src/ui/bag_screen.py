# ABOUTME: Bag screen UI component for listing items
# ABOUTME: Renders item names, counts, and descriptions

from typing import Callable, Optional

from src.engine import constants
from src.items.bag import Bag, BagEntry
from src.items.item_loader import ItemLoader


class BagScreen:
    """Bag UI component for item selection."""

    def __init__(self, bag: Bag, item_loader: ItemLoader, entry_filter: Optional[Callable] = None):
        self.bag = bag
        self.item_loader = item_loader
        self.entry_filter = entry_filter
        self.cursor_index = 0
        self.scroll_offset = 0
        self.message = ""

    def move_cursor(self, direction: int):
        entries = self.get_entries()
        if not entries:
            return
        self.cursor_index = (self.cursor_index + direction) % len(entries)

    def get_entries(self) -> list[BagEntry]:
        entries = self.bag.get_entries()
        if not self.entry_filter:
            return entries

        filtered = []
        for entry in entries:
            item = self.item_loader.get_item(entry.item_id)
            if self.entry_filter(item):
                filtered.append(entry)
        return filtered

    def get_selected_entry(self) -> Optional[BagEntry]:
        entries = self.get_entries()
        if not entries:
            return None
        if self.cursor_index >= len(entries):
            self.cursor_index = max(0, len(entries) - 1)
        return entries[self.cursor_index]

    def get_visible_entries(self) -> tuple[list[BagEntry], int]:
        entries = self.get_entries()
        line_height = 14 * constants.UI_SCALE
        list_height = constants.GAME_HEIGHT - (32 * constants.UI_SCALE)
        max_lines = list_height // line_height

        self._adjust_scroll(len(entries), max_lines)

        visible = entries[self.scroll_offset:self.scroll_offset + max_lines]
        return visible, self.scroll_offset

    def set_message(self, message: str) -> None:
        self.message = message

    def render(self, renderer) -> None:
        renderer.clear((248, 248, 248))

        line_height = 14 * constants.UI_SCALE
        list_height = constants.GAME_HEIGHT - (32 * constants.UI_SCALE)
        max_lines = list_height // line_height
        font_size = 16 * constants.UI_SCALE

        entries = self.get_entries()
        visible_entries, start_index = self.get_visible_entries()

        for i in range(min(max_lines, len(visible_entries))):
            entry = visible_entries[i]
            item = self.item_loader.get_item(entry.item_id)
            y = (4 * constants.UI_SCALE) + (i * line_height)

            if start_index + i == self.cursor_index:
                renderer.draw_text("▶", 4 * constants.UI_SCALE, y, font_size=font_size)

            name_text = item.name.upper()
            renderer.draw_text(name_text, 16 * constants.UI_SCALE, y, font_size=font_size)

            if entry.quantity > 1:
                qty_text = f"x{entry.quantity}"
                renderer.draw_text(
                    qty_text,
                    constants.GAME_WIDTH - (28 * constants.UI_SCALE),
                    y,
                    font_size=font_size
                )

        self._render_description(renderer, entries)

    def _adjust_scroll(self, total_entries: int, max_lines: int) -> None:
        if total_entries <= max_lines:
            self.scroll_offset = 0
            return

        if self.cursor_index < self.scroll_offset:
            self.scroll_offset = self.cursor_index
        elif self.cursor_index >= self.scroll_offset + max_lines:
            self.scroll_offset = self.cursor_index - max_lines + 1

    def _render_description(self, renderer, entries: list[BagEntry]) -> None:
        box_height = 32 * constants.UI_SCALE
        box_y = constants.GAME_HEIGHT - box_height
        border_width = 1 * constants.UI_SCALE
        renderer.draw_rect((248, 248, 248), (0, box_y, constants.GAME_WIDTH, box_height), 0)
        renderer.draw_rect((0, 0, 0), (0, box_y, constants.GAME_WIDTH, box_height), border_width)

        text = self.message
        if not text:
            entry = self.get_selected_entry()
            if entry:
                item = self.item_loader.get_item(entry.item_id)
                text = item.flavor_text or item.effect

        if text:
            renderer.draw_text(
                text,
                8 * constants.UI_SCALE,
                box_y + (6 * constants.UI_SCALE),
                font_size=16 * constants.UI_SCALE
            )
