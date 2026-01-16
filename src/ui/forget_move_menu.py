# ABOUTME: Move selection menu for forgetting a move
# ABOUTME: Shows the Pokemon's current moves without PP or type details

from typing import Optional
from src.engine.constants import COLOR_BLACK, COLOR_WHITE


class ForgetMoveMenu:
    """Menu for choosing a move to forget."""

    def __init__(self, move_ids: list[str]):
        self.move_ids = move_ids[:4]
        self.cursor_position = 0
        self.is_active = False

    def handle_input(self, input_handler) -> tuple[Optional[str], bool]:
        """
        Handle navigation and selection.

        Returns:
            Tuple of (selected_move_id, cancelled)
        """
        if not self.is_active or not self.move_ids:
            return (None, False)

        if input_handler.is_just_pressed("up"):
            self.cursor_position = (self.cursor_position - 1) % len(self.move_ids)
        elif input_handler.is_just_pressed("down"):
            self.cursor_position = (self.cursor_position + 1) % len(self.move_ids)
        elif input_handler.is_just_pressed("a"):
            return (self.move_ids[self.cursor_position], False)
        elif input_handler.is_just_pressed("b"):
            return (None, True)

        return (None, False)

    def render(self, renderer, x: int, y: int) -> None:
        """Render move list at the given position."""
        if not self.is_active:
            return

        menu_width = 120
        menu_height = 8 + len(self.move_ids) * 12
        padding = 4

        renderer.draw_rect(COLOR_BLACK, (x, y, menu_width, menu_height), 2)
        renderer.draw_rect(COLOR_WHITE, (x + 2, y + 2, menu_width - 4, menu_height - 4), 0)

        for i, move_id in enumerate(self.move_ids):
            move_y = y + padding + i * 12
            cursor = ">" if i == self.cursor_position else " "
            move_name = move_id.upper().replace("-", " ")
            renderer.draw_text(cursor, x + padding, move_y, COLOR_BLACK, 10)
            renderer.draw_text(move_name, x + padding + 10, move_y, COLOR_BLACK, 10)

    def activate(self):
        """Activate the menu."""
        self.is_active = True
        self.cursor_position = 0

    def deactivate(self):
        """Deactivate the menu."""
        self.is_active = False
