# ABOUTME: Title menu UI component for the startup screen
# ABOUTME: Handles menu rendering and cursor navigation

import pygame

from src.engine import constants


class TitleMenu:
    """Title menu UI component."""

    def __init__(self, has_save: bool):
        """
        Initialize title menu.

        Args:
            has_save: Whether a save file exists for CONTINUE
        """
        self.options = ["CONTINUE", "NEW GAME", "OPTION"]
        self.disabled_options = set()
        if not has_save:
            self.disabled_options.add("CONTINUE")
        self.cursor_index = self._first_enabled_index()

    def _first_enabled_index(self) -> int:
        for index, option in enumerate(self.options):
            if option not in self.disabled_options:
                return index
        return 0

    def move_cursor(self, direction: int):
        """
        Move cursor up (-1) or down (1).

        Args:
            direction: -1 for up, 1 for down
        """
        if not self.options:
            return

        index = self.cursor_index
        for _ in range(len(self.options)):
            index = (index + direction) % len(self.options)
            if self.options[index] not in self.disabled_options:
                self.cursor_index = index
                break

    def get_selection(self) -> str:
        """Get currently selected option."""
        return self.options[self.cursor_index]

    def render(self, renderer):
        """
        Render the title menu.

        Args:
            renderer: Renderer instance for drawing
        """
        menu_width = 96 * constants.UI_SCALE
        menu_height = (8 + len(self.options) * 16 + 8) * constants.UI_SCALE
        menu_x = constants.GAME_WIDTH - menu_width - (8 * constants.UI_SCALE)
        menu_y = 8 * constants.UI_SCALE

        border_color = (0, 0, 0)
        bg_color = (248, 248, 248)
        text_color = (0, 0, 0)
        disabled_color = (96, 96, 96)

        border_width = 2 * constants.UI_SCALE
        inner_offset = 2 * constants.UI_SCALE
        renderer.draw_rect(border_color, (menu_x, menu_y, menu_width, menu_height), border_width)
        renderer.draw_rect(
            bg_color,
            (menu_x + inner_offset, menu_y + inner_offset,
             menu_width - (inner_offset * 2), menu_height - (inner_offset * 2)),
            0
        )

        text_x = menu_x + (8 * constants.UI_SCALE)
        text_y = menu_y + (8 * constants.UI_SCALE)
        line_height = 16 * constants.UI_SCALE

        for i, option in enumerate(self.options):
            y = text_y + (i * line_height)
            if i == self.cursor_index:
                points = [
                    (text_x - (10 * constants.UI_SCALE), y + (2 * constants.UI_SCALE)),
                    (text_x - (10 * constants.UI_SCALE), y + (10 * constants.UI_SCALE)),
                    (text_x - (4 * constants.UI_SCALE), y + (6 * constants.UI_SCALE))
                ]
                pygame.draw.polygon(renderer.game_surface, text_color, points)
            color = disabled_color if option in self.disabled_options else text_color
            renderer.draw_text(option, text_x, y, color, 12 * constants.UI_SCALE)
