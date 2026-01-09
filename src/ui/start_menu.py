# ABOUTME: Start menu UI component for main game menu
# ABOUTME: Handles menu rendering and cursor navigation

import pygame
from src.engine.constants import GAME_WIDTH, GAME_HEIGHT


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
        menu_width = 80
        menu_height = 120
        menu_x = GAME_WIDTH - menu_width - 8
        menu_y = 8

        # Colors (Game Boy palette)
        border_color = (0, 0, 0)
        bg_color = (248, 248, 248)
        text_color = (0, 0, 0)

        # Draw menu background box
        renderer.draw_rect(border_color, (menu_x, menu_y, menu_width, menu_height), 2)
        renderer.draw_rect(bg_color, (menu_x + 2, menu_y + 2, menu_width - 4, menu_height - 4), 0)

        # Draw options
        text_x = menu_x + 8
        text_y = menu_y + 8
        line_height = 16

        for i, option in enumerate(self.options):
            y = text_y + (i * line_height)

            # Draw cursor
            if i == self.cursor_index:
                renderer.draw_text("▶", text_x - 10, y, text_color, 12)

            # Draw option text
            renderer.draw_text(option, text_x, y, text_color, 12)
