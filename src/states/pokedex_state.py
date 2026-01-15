# ABOUTME: Pokedex state for list and entry navigation
# ABOUTME: Manages input and transitions between list and entry views

from src.states.base_state import BaseState
from src.ui.pokedex_screen import PokedexScreen
from src.battle.species_loader import SpeciesLoader


class PokedexState(BaseState):
    """State for the Pokedex screens."""

    def __init__(self, game, previous_state):
        super().__init__(game)
        self.previous_state = previous_state
        species_loader = SpeciesLoader()
        pokedex_seen = getattr(previous_state, "pokedex_seen", set())
        pokedex_caught = getattr(previous_state, "pokedex_caught", set())
        self.screen = PokedexScreen(
            species_loader.get_all_species(),
            pokedex_seen,
            pokedex_caught
        )

    def handle_input(self, input_handler):
        if self.screen.mode == "entry":
            if input_handler.is_just_pressed("b") or input_handler.is_just_pressed("a"):
                self.screen.close_entry()
            return

        if input_handler.is_just_pressed("down"):
            self.screen.move_cursor(1)
        elif input_handler.is_just_pressed("up"):
            self.screen.move_cursor(-1)
        elif input_handler.is_just_pressed("a"):
            self.screen.open_entry()
        elif input_handler.is_just_pressed("b"):
            self.game.pop_state()

    def update(self, dt: float):
        pass

    def render(self, renderer):
        self.screen.render(renderer)
