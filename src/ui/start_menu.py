# ABOUTME: Start menu UI component for main game menu
# ABOUTME: Handles menu rendering and cursor navigation

import pygame

from src.engine import constants


class StartMenu:
    """Main start menu UI component."""

    def __init__(self, player_name: str = "PLAYER"):
        """
        Initialize start menu.

        Args:
            player_name: Player's name to display
        """
        self.options = [
            "POKéDEX",
            "POKéMON",
            "ITEM",
            player_name,
            "SAVE",
            "OPTION",
            "EXIT"
        ]
        self.cursor_index = 0

    def move_cursor(self, direction: int):
        """
        Move cursor up (-1) or down (1).

        Args:
            direction: -1 for up, 1 for down
        """
        self.cursor_index = (self.cursor_index + direction) % len(self.options)

    def get_selection(self) -> str:
        """Get currently selected option."""
        return self.options[self.cursor_index]

    def render(self, renderer):
        """
        Render the start menu.

        Args:
            renderer: Renderer instance for drawing
        """
        # Menu box dimensions (right side of screen)
        menu_width = 80 * constants.UI_SCALE
        menu_height = 120 * constants.UI_SCALE
        menu_x = constants.GAME_WIDTH - menu_width - (8 * constants.UI_SCALE)
        menu_y = 8 * constants.UI_SCALE

        # Colors (Game Boy palette)
        border_color = (0, 0, 0)
        bg_color = (248, 248, 248)
        text_color = (0, 0, 0)

        # Draw menu background box
        border_width = 2 * constants.UI_SCALE
        inner_offset = 2 * constants.UI_SCALE
        renderer.draw_rect(border_color, (menu_x, menu_y, menu_width, menu_height), border_width)
        renderer.draw_rect(
            bg_color,
            (menu_x + inner_offset, menu_y + inner_offset,
             menu_width - (inner_offset * 2), menu_height - (inner_offset * 2)),
            0
        )

        # Draw options
        text_x = menu_x + (8 * constants.UI_SCALE)
        text_y = menu_y + (8 * constants.UI_SCALE)
        line_height = 16 * constants.UI_SCALE

        for i, option in enumerate(self.options):
            y = text_y + (i * line_height)

            # Draw cursor
            if i == self.cursor_index:
                renderer.draw_text(
                    "▶",
                    text_x - (10 * constants.UI_SCALE),
                    y,
                    text_color,
                    12 * constants.UI_SCALE
                )

            # Draw option text
            renderer.draw_text(option, text_x, y, text_color, 12 * constants.UI_SCALE)
