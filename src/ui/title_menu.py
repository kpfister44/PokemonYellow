# ABOUTME: Title menu UI component for the startup screen
# ABOUTME: Handles menu rendering and cursor navigation

from src.engine.constants import GAME_WIDTH


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
        menu_width = 96
        menu_height = 8 + len(self.options) * 16 + 8
        menu_x = GAME_WIDTH - menu_width - 8
        menu_y = 8

        border_color = (0, 0, 0)
        bg_color = (248, 248, 248)
        text_color = (0, 0, 0)
        disabled_color = (96, 96, 96)

        renderer.draw_rect(border_color, (menu_x, menu_y, menu_width, menu_height), 2)
        renderer.draw_rect(bg_color, (menu_x + 2, menu_y + 2, menu_width - 4, menu_height - 4), 0)

        text_x = menu_x + 8
        text_y = menu_y + 8
        line_height = 16

        for i, option in enumerate(self.options):
            y = text_y + (i * line_height)
            if i == self.cursor_index:
                renderer.draw_text("▶", text_x - 10, y, text_color, 12)
            color = disabled_color if option in self.disabled_options else text_color
            renderer.draw_text(option, text_x, y, color, 12)
