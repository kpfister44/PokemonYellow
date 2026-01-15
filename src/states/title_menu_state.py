# ABOUTME: Title menu state for game startup flow
# ABOUTME: Manages Continue/New Game selection and transitions

from src.engine import constants
from src.states.base_state import BaseState
from src.states.overworld_state import OverworldState
from src.ui.title_menu import TitleMenu
from src.save.save_storage import load_save_data, save_exists
from src.battle.species_loader import SpeciesLoader


class TitleMenuState(BaseState):
    """State for the title menu."""

    def __init__(self, game):
        """
        Initialize title menu state.

        Args:
            game: Game instance
        """
        super().__init__(game)
        self.menu = TitleMenu(has_save=save_exists())

    def handle_input(self, input_handler):
        """Handle menu input."""
        if input_handler.is_just_pressed("down"):
            self.menu.move_cursor(1)
        elif input_handler.is_just_pressed("up"):
            self.menu.move_cursor(-1)
        elif input_handler.is_just_pressed("a"):
            selection = self.menu.get_selection()
            self._handle_selection(selection)

    def _handle_selection(self, selection: str):
        """Handle menu selection."""
        if selection == "CONTINUE":
            if not save_exists():
                return
            species_loader = SpeciesLoader()
            save_data = load_save_data(None, species_loader)
            overworld = OverworldState(
                self.game,
                save_data.map_path,
                player_start_x=save_data.player_x,
                player_start_y=save_data.player_y,
                party=save_data.party,
                bag=save_data.bag,
                collected_items=save_data.collected_items,
                defeated_trainers=save_data.defeated_trainers,
                player_direction=save_data.player_direction,
                pokedex_seen=save_data.get_pokedex_seen(),
                pokedex_caught=save_data.get_pokedex_caught()
            )
            self.game.change_state(overworld)

        elif selection == "NEW GAME":
            overworld = OverworldState(
                self.game,
                "data/maps/pallet_town.json",
                player_start_x=8,
                player_start_y=13,
                pokedex_seen={"pikachu"},
                pokedex_caught={"pikachu"}
            )
            self.game.change_state(overworld)

        elif selection == "OPTION":
            pass

    def update(self, dt: float):
        """Update title menu state."""
        pass

    def render(self, renderer):
        """Render title menu."""
        renderer.clear(constants.COLOR_BLACK)
        self.menu.render(renderer)
