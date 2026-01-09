# ABOUTME: Battle menu UI component for FIGHT/ITEM/PKM/RUN options
# ABOUTME: Implements 2x2 grid menu with cursor navigation for Pokemon Yellow battles

from typing import Optional
from src.engine.constants import COLOR_BLACK, COLOR_WHITE


class BattleMenu:
    """
    2x2 grid menu for battle command selection.

    Layout (Pokemon Yellow style):
    +----------+----------+
    | FIGHT    | ITEM     |
    +----------+----------+
    | PKM      | RUN      |
    +----------+----------+
    """

    def __init__(self):
        """Initialize battle menu."""
        self.options = [
            ["FIGHT", "ITEM"],
            ["PKM", "RUN"]
        ]
        self.cursor_row = 0
        self.cursor_col = 0
        self.is_active = False

    def handle_input(self, input_handler) -> Optional[str]:
        """
        Handle directional input and A/B buttons.

        Args:
            input_handler: Input handler with key state

        Returns:
            Selected option string or None if no selection
        """
        if not self.is_active:
            return None

        # Navigation
        if input_handler.is_just_pressed("up"):
            self.cursor_row = (self.cursor_row - 1) % 2
        elif input_handler.is_just_pressed("down"):
            self.cursor_row = (self.cursor_row + 1) % 2
        elif input_handler.is_just_pressed("left"):
            self.cursor_col = (self.cursor_col - 1) % 2
        elif input_handler.is_just_pressed("right"):
            self.cursor_col = (self.cursor_col + 1) % 2

        # Selection
        elif input_handler.is_just_pressed("a"):
            selected = self.options[self.cursor_row][self.cursor_col]
            return selected

        return None

    def render(self, renderer, x: int, y: int):
        """
        Render battle menu at position.

        Args:
            renderer: Game renderer
            x: X position (left edge)
            y: Y position (top edge)
        """
        if not self.is_active:
            return

        # Menu dimensions (2x2 grid)
        option_width = 36
        option_height = 16
        padding = 4

        # Draw menu box border
        menu_width = option_width * 2 + padding * 3
        menu_height = option_height * 2 + padding * 3
        renderer.draw_rect(COLOR_BLACK, (x, y, menu_width, menu_height), 2)
        renderer.draw_rect(COLOR_WHITE, (x + 2, y + 2, menu_width - 4, menu_height - 4), 0)

        # Render each option
        for row in range(2):
            for col in range(2):
                option_x = x + padding + col * (option_width + padding)
                option_y = y + padding + row * (option_height + padding)

                # Draw cursor indicator if this is the selected option
                if row == self.cursor_row and col == self.cursor_col:
                    # Draw selection background
                    renderer.draw_rect(COLOR_BLACK, (option_x - 2, option_y - 2, option_width, option_height), 1)

                # Draw option text
                option_text = self.options[row][col]
                text_x = option_x + 4
                text_y = option_y + 4
                renderer.draw_text(option_text, text_x, text_y, COLOR_BLACK, 10)

    def activate(self):
        """Activate the menu."""
        self.is_active = True
        self.cursor_row = 0
        self.cursor_col = 0

    def deactivate(self):
        """Deactivate the menu."""
        self.is_active = False
