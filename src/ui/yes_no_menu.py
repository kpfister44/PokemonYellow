# ABOUTME: Yes/No prompt menu for battle dialogs
# ABOUTME: Handles simple confirmation input with a two-option cursor

from typing import Optional
from src.engine.constants import COLOR_BLACK, COLOR_WHITE


class YesNoMenu:
    """Two-option yes/no menu used in battle dialogs."""

    def __init__(self):
        self.options = ["YES", "NO"]
        self.cursor_index = 0
        self.is_active = False

    def handle_input(self, input_handler) -> Optional[bool]:
        """
        Handle input for yes/no selection.

        Returns:
            True for YES, False for NO/cancel, None for no action
        """
        if not self.is_active:
            return None

        if input_handler.is_just_pressed("up") or input_handler.is_just_pressed("down"):
            self.cursor_index = (self.cursor_index + 1) % len(self.options)
            return None

        if input_handler.is_just_pressed("a"):
            return self.cursor_index == 0

        if input_handler.is_just_pressed("b"):
            return False

        return None

    def render(self, renderer, x: int, y: int) -> None:
        """Render the menu at the given position."""
        if not self.is_active:
            return

        menu_width = 44
        option_height = 12
        menu_height = option_height * len(self.options) + 8
        padding = 4

        renderer.draw_rect(COLOR_BLACK, (x, y, menu_width, menu_height), 2)
        renderer.draw_rect(COLOR_WHITE, (x + 2, y + 2, menu_width - 4, menu_height - 4), 0)

        for i, option in enumerate(self.options):
            option_y = y + padding + i * option_height
            cursor = ">" if i == self.cursor_index else " "
            renderer.draw_text(cursor, x + padding, option_y, COLOR_BLACK, 10)
            renderer.draw_text(option, x + padding + 10, option_y, COLOR_BLACK, 10)

    def activate(self):
        """Activate the menu."""
        self.is_active = True
        self.cursor_index = 0

    def deactivate(self):
        """Deactivate the menu."""
        self.is_active = False
