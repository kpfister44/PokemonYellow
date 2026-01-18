# ABOUTME: Move selection menu for choosing Pokemon moves in battle
# ABOUTME: Displays up to 4 moves with type, PP, and cursor navigation

from typing import Optional

from src.battle.move import Move
from src.engine import constants


class MoveMenu:
    """
    Move selection menu for battle.

    Displays:
    - Move name
    - Move type
    - Current PP / Max PP
    - Cursor for selection
    """

    def __init__(self, moves: list[Move], current_pp: dict[str, int]):
        """
        Initialize move menu.

        Args:
            moves: List of Move objects (up to 4)
            current_pp: Dictionary mapping move_id to current PP
        """
        self.moves = moves[:4]  # Max 4 moves in Gen 1
        self.current_pp = current_pp
        self.cursor_position = 0
        self.is_active = False

    def handle_input(self, input_handler) -> Optional[tuple[Optional[Move], bool]]:
        """
        Handle up/down navigation, A to select, B to cancel.

        Args:
            input_handler: Input handler with key state

        Returns:
            Tuple of (selected_move: Optional[Move], cancelled: bool)
            - (Move, False) when move is selected
            - (None, True) when menu is cancelled with B
            - (None, False) when no action taken
        """
        if not self.is_active or len(self.moves) == 0:
            return (None, False)

        # Navigation
        if input_handler.is_just_pressed("up"):
            self.cursor_position = (self.cursor_position - 1) % len(self.moves)
        elif input_handler.is_just_pressed("down"):
            self.cursor_position = (self.cursor_position + 1) % len(self.moves)

        # Selection
        elif input_handler.is_just_pressed("a"):
            selected_move = self.moves[self.cursor_position]
            # Check if move has PP remaining
            current = self.current_pp.get(selected_move.move_id, selected_move.pp)
            if current > 0:
                return (selected_move, False)
            # No PP remaining, can't select
            return (None, False)

        # Cancel
        elif input_handler.is_just_pressed("b"):
            return (None, True)

        return (None, False)

    def render(self, renderer, x: int, y: int):
        """
        Render move menu at position.

        Args:
            renderer: Game renderer
            x: X position (left edge)
            y: Y position (top edge)
        """
        if not self.is_active:
            return

        # Menu dimensions
        menu_width = 144 * constants.UI_SCALE
        menu_height = (8 + len(self.moves) * 12) * constants.UI_SCALE
        padding = 4 * constants.UI_SCALE

        # Draw menu box border
        border_width = 2 * constants.UI_SCALE
        inner_offset = 2 * constants.UI_SCALE
        renderer.draw_rect(constants.COLOR_BLACK, (x, y, menu_width, menu_height), border_width)
        renderer.draw_rect(
            constants.COLOR_WHITE,
            (x + inner_offset, y + inner_offset,
             menu_width - (inner_offset * 2), menu_height - (inner_offset * 2)),
            0
        )

        # Render each move
        for i, move in enumerate(self.moves):
            move_y = y + padding + i * (12 * constants.UI_SCALE)

            # Draw cursor indicator if this is the selected move
            cursor = ">" if i == self.cursor_position else " "
            renderer.draw_text(
                cursor,
                x + padding,
                move_y,
                constants.COLOR_BLACK,
                10 * constants.UI_SCALE
            )

            # Draw move name
            move_name = move.name.upper()[:12]  # Truncate long names
            renderer.draw_text(
                move_name,
                x + padding + (10 * constants.UI_SCALE),
                move_y,
                constants.COLOR_BLACK,
                10 * constants.UI_SCALE
            )

            # Draw PP (right-aligned)
            current = self.current_pp.get(move.move_id, move.pp)
            pp_text = f"PP {current:2}/{move.pp:2}"
            pp_x = x + menu_width - padding - (50 * constants.UI_SCALE)
            renderer.draw_text(
                pp_text,
                pp_x,
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
