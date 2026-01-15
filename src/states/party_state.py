# ABOUTME: Party screen game state
# ABOUTME: Manages party list navigation and transitions to summary

import pygame
from typing import Callable, Optional
from src.states.base_state import BaseState
from src.ui.party_screen import PartyScreen
from src.party.party import Party
from src.battle.pokemon import Pokemon
from src.items.item_effects import ItemUseResult


class PartyState(BaseState):
    """State for party screen."""

    def __init__(
        self,
        game,
        party: Party,
        mode: str = "view",
        on_select: Optional[Callable] = None,
        on_cancel: Optional[Callable] = None,
        item_use: Optional[Callable] = None,
        on_item_used: Optional[Callable[[ItemUseResult], bool]] = None,
        active_pokemon: Optional[Pokemon] = None
    ):
        """
        Initialize party state.

        Args:
            game: Game instance
            party: Party to display
            mode: "view" (default), "switch" (battle switching),
                  or "forced_switch" (required after fainting)
        """
        super().__init__(game)
        self.party = party
        self.mode = mode  # Controls view vs. switching behavior
        self.screen = PartyScreen(party)
        self.on_select = on_select
        self.on_cancel = on_cancel
        self.item_use = item_use
        self.on_item_used = on_item_used
        self.active_pokemon = active_pokemon
        self.item_target_index = None
        self.item_result = None
        self.animating_item = False

    def handle_input(self, input_handler):
        """Handle party screen input."""
        if self.mode == "item" and self.animating_item:
            return

        if input_handler.is_just_pressed("down"):
            self.screen.move_cursor(1)

        elif input_handler.is_just_pressed("up"):
            self.screen.move_cursor(-1)

        elif input_handler.is_just_pressed("a"):
            selected = self.screen.get_selected_pokemon()

            if self.mode == "item":
                if selected:
                    if self.item_use:
                        result = self.item_use(selected)
                        self.item_result = result
                        self.item_target_index = self.screen.cursor_index
                        if result.success:
                            if self._should_animate_item(selected):
                                self.animating_item = True
                                if not self._is_item_animation_active(selected):
                                    self._finish_item_use()
                            else:
                                self._finish_item_use()
                        else:
                            self._finish_item_use()
                    else:
                        self.game.pop_state()
                        if self.on_select:
                            self.on_select(selected)
            elif self.mode in ["switch", "forced_switch"]:
                # Battle switching mode
                if selected and not selected.is_fainted():
                    # Return selected Pokemon to battle state
                    self.game.pop_state()  # Close party screen

                    # Notify battle state of switch
                    # Battle state will handle the switch
                    battle_state = self.game.state_stack[-1]
                    if hasattr(battle_state, "handle_switch"):
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
            if self.mode == "item":
                if not self.animating_item:
                    self.game.pop_state()
                    if self.on_cancel:
                        self.on_cancel()
            elif self.mode != "forced_switch":
                self.game.pop_state()

    def update(self, dt: float):
        """Update party state (nothing to update)."""
        self.screen.update(dt)
        if self.animating_item and self.item_target_index is not None:
            pokemon = self.party.pokemon[self.item_target_index]
            if not self._is_item_animation_active(pokemon):
                self._finish_item_use()

    def render(self, renderer) -> None:
        """
        Render party screen.

        Args:
            renderer: Renderer instance for drawing
        """
        self.screen.render(renderer)

    def _is_item_animation_active(self, pokemon) -> bool:
        if self.item_target_index is None:
            return False
        display = self.screen.hp_displays[self.item_target_index]
        return display.is_animating(pokemon.current_hp)

    def _should_animate_item(self, pokemon: Pokemon) -> bool:
        if self.active_pokemon is None:
            return True
        return pokemon is not self.active_pokemon

    def _finish_item_use(self) -> None:
        should_close_bag = False
        if self.on_item_used and self.item_result is not None:
            should_close_bag = bool(self.on_item_used(self.item_result))
        self.animating_item = False
        self.item_target_index = None
        self.item_result = None
        self.game.pop_state()
        if should_close_bag:
            self.game.pop_state()
