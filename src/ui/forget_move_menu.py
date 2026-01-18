# ABOUTME: Move selection menu for forgetting a move
# ABOUTME: Shows the Pokemon's current moves without PP or type details

from typing import Optional

from src.engine import constants


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

        menu_width = 120 * constants.UI_SCALE
        menu_height = (8 + len(self.move_ids) * 12) * constants.UI_SCALE
        padding = 4 * constants.UI_SCALE

        border_width = 2 * constants.UI_SCALE
        inner_offset = 2 * constants.UI_SCALE
        renderer.draw_rect(constants.COLOR_BLACK, (x, y, menu_width, menu_height), border_width)
        renderer.draw_rect(
            constants.COLOR_WHITE,
            (x + inner_offset, y + inner_offset,
             menu_width - (inner_offset * 2), menu_height - (inner_offset * 2)),
            0
        )

        for i, move_id in enumerate(self.move_ids):
            move_y = y + padding + i * (12 * constants.UI_SCALE)
            cursor = ">" if i == self.cursor_position else " "
            move_name = move_id.upper().replace("-", " ")
            renderer.draw_text(
                cursor,
                x + padding,
                move_y,
                constants.COLOR_BLACK,
                10 * constants.UI_SCALE
            )
            renderer.draw_text(
                move_name,
                x + padding + (10 * constants.UI_SCALE),
                move_y,
                constants.COLOR_BLACK,
                10 * constants.UI_SCALE
            )

    def activate(self):
        """Activate the menu."""
        self.is_active = True
        self.cursor_position = 0

    def deactivate(self):
        """Deactivate the menu."""
        self.is_active = False
