# ABOUTME: Pokemon summary screen game state
# ABOUTME: Manages summary page navigation and Pokemon switching

import pygame
from src.states.base_state import BaseState
from src.ui.summary_screen import SummaryScreen
from src.party.party import Party
from src.battle.pokemon import Pokemon


class SummaryState(BaseState):
    """State for Pokemon summary screen."""

    def __init__(self, game, pokemon: Pokemon, party: Party):
        """
        Initialize summary state.

        Args:
            game: Game instance
            pokemon: Pokemon to display
            party: Party containing the Pokemon
        """
        super().__init__(game)
        self.screen = SummaryScreen(pokemon, party)

    def handle_input(self, input_handler):
        """Handle summary screen input."""
        if input_handler.is_just_pressed("left"):
            self.screen.change_page(-1)

        elif input_handler.is_just_pressed("right"):
            self.screen.change_page(1)

        elif input_handler.is_just_pressed("up"):
            self.screen.change_pokemon(-1)

        elif input_handler.is_just_pressed("down"):
            self.screen.change_pokemon(1)

        elif input_handler.is_just_pressed("b") or input_handler.is_just_pressed("a"):
            # Go back to party screen
            self.game.pop_state()

    def update(self, dt: float):
        """Update summary state (nothing to update)."""
        pass

    def render(self, renderer) -> None:
        """
        Render summary screen.

        Args:
            renderer: Renderer instance for drawing
        """
        self.screen.render(renderer)
