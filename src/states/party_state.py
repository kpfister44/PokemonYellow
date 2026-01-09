# ABOUTME: Party screen game state
# ABOUTME: Manages party list navigation and transitions to summary

import pygame
from src.states.base_state import BaseState
from src.ui.party_screen import PartyScreen
from src.party.party import Party


class PartyState(BaseState):
    """State for party screen."""

    def __init__(self, game, party: Party, mode: str = "view"):
        """
        Initialize party state.

        Args:
            game: Game instance
            party: Party to display
            mode: "view" (default) or "switch" (for battle switching)
        """
        super().__init__(game)
        self.party = party
        self.mode = mode
        self.screen = PartyScreen(party)

    def handle_input(self, input_handler):
        """Handle party screen input."""
        if input_handler.is_just_pressed("down"):
            self.screen.move_cursor(1)

        elif input_handler.is_just_pressed("up"):
            self.screen.move_cursor(-1)

        elif input_handler.is_just_pressed("a"):
            # Select Pokemon - open summary
            selected = self.screen.get_selected_pokemon()
            if selected:
                from src.states.summary_state import SummaryState
                summary_state = SummaryState(self.game, selected, self.party)
                self.game.push_state(summary_state)

        elif input_handler.is_just_pressed("b"):
            # Go back
            self.game.pop_state()

    def update(self, dt: float):
        """Update party state (nothing to update)."""
        pass

    def render(self, renderer):
        """
        Render party screen.

        Args:
            renderer: Renderer instance for drawing
        """
        self.screen.render(renderer)
