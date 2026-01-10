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
                  Note: mode will be used in Tasks 8-9 for switch logic
        """
        super().__init__(game)
        self.party = party
        self.mode = mode  # Will be used in Tasks 8-9
        self.screen = PartyScreen(party)

    def handle_input(self, input_handler):
        """Handle party screen input."""
        if input_handler.is_just_pressed("down"):
            self.screen.move_cursor(1)

        elif input_handler.is_just_pressed("up"):
            self.screen.move_cursor(-1)

        elif input_handler.is_just_pressed("a"):
            selected = self.screen.get_selected_pokemon()

            if self.mode == "switch":
                # Battle switching mode
                if selected and not selected.is_fainted():
                    # Return selected Pokemon to battle state
                    self.game.pop_state()  # Close party screen

                    # Notify battle state of switch
                    # Battle state will handle the switch
                    from src.states.battle_state import BattleState
                    battle_state = self.game.state_stack[-1]
                    if isinstance(battle_state, BattleState):
                        battle_state.handle_switch(selected)
                else:
                    # Can't switch to fainted Pokemon
                    # TODO: Show error message
                    pass
            else:
                # View mode - open summary
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

    def render(self, renderer) -> None:
        """
        Render party screen.

        Args:
            renderer: Renderer instance for drawing
        """
        self.screen.render(renderer)
