# ABOUTME: Start menu game state
# ABOUTME: Manages start menu navigation and transitions to other states

import pygame
from src.states.base_state import BaseState
from src.ui.start_menu import StartMenu


class StartMenuState(BaseState):
    """State for main start menu."""

    def __init__(self, game, previous_state):
        """
        Initialize start menu state.

        Args:
            game: Game instance
            previous_state: State to return to (usually OverworldState)
        """
        super().__init__(game)
        self.previous_state = previous_state
        self.menu = StartMenu(player_name="PLAYER")  # TODO: Get from player data

    def handle_input(self, input_handler):
        """Handle menu input."""
        if input_handler.is_just_pressed("down"):
            self.menu.move_cursor(1)

        elif input_handler.is_just_pressed("up"):
            self.menu.move_cursor(-1)

        elif input_handler.is_just_pressed("a"):
            # Handle selection
            selection = self.menu.get_selection()
            self._handle_selection(selection)

        elif input_handler.is_just_pressed("b"):
            # Close menu (return to previous state)
            self.game.pop_state()

    def _handle_selection(self, selection: str):
        """
        Handle menu selection.

        Args:
            selection: Selected menu option
        """
        if selection == "POKéMON":
            from src.states.party_state import PartyState
            party_state = PartyState(self.game, self.previous_state.party)
            self.game.push_state(party_state)

        elif selection == "EXIT":
            # Close menu
            self.game.pop_state()

        elif selection == "POKéDEX":
            # TODO: Implement in future phase
            pass

        elif selection == "ITEM":
            if hasattr(self.previous_state, "bag") and hasattr(self.previous_state, "party"):
                from src.states.bag_state import BagState
                bag_state = BagState(
                    self.game,
                    self.previous_state.bag,
                    self.previous_state.party,
                    mode="overworld"
                )
                self.game.push_state(bag_state)

        elif selection == "SAVE":
            if not self.previous_state:
                return
            required = ("player", "map_path", "party", "bag")
            if not all(hasattr(self.previous_state, name) for name in required):
                return
            from src.save.save_data import SaveData
            from src.save.save_storage import write_save_data
            player_data = self.previous_state.player.to_dict()
            save_data = SaveData(
                player_name="PLAYER",
                player_direction=player_data["direction"],
                map_path=self.previous_state.map_path,
                player_x=player_data["tile_x"],
                player_y=player_data["tile_y"],
                party=self.previous_state.party,
                bag=self.previous_state.bag,
                defeated_trainers=getattr(self.previous_state, "defeated_trainers", set()),
                collected_items=getattr(self.previous_state, "collected_items", set())
            )
            write_save_data(save_data)

        elif selection == "OPTION":
            # TODO: Implement in future phase
            pass

    def update(self, dt: float):
        """Update menu state (nothing to update)."""
        pass

    def render(self, renderer):
        """
        Render start menu over previous state.

        Args:
            renderer: Renderer instance
        """
        # Render previous state (overworld) first
        if self.previous_state:
            self.previous_state.render(renderer)

        # Render menu on top
        self.menu.render(renderer)
