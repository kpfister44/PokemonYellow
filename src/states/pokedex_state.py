# ABOUTME: Pokedex state for list and entry navigation
# ABOUTME: Manages input and transitions between list and entry views

from src.states.base_state import BaseState
from src.ui.pokedex_screen import (
    FOCUS_LIST,
    FOCUS_MENU,
    PokedexScreen
)
from src.battle.species_loader import SpeciesLoader
from src.ui.dialog_box import DialogBox


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
        self.active_dialog = None

    def handle_input(self, input_handler):
        if self.active_dialog:
            if input_handler.is_just_pressed("a") or input_handler.is_just_pressed("b"):
                self.active_dialog.close()
                self.active_dialog = None
            return

        if self.screen.mode == "entry":
            if input_handler.is_just_pressed("a"):
                if self.screen.can_advance_page():
                    self.screen.advance_page()
                else:
                    self.screen.close_entry()
                    self.screen.set_focus(FOCUS_LIST)
            elif input_handler.is_just_pressed("b"):
                if self.screen.can_go_back_page():
                    self.screen.go_back_page()
                else:
                    self.screen.close_entry()
                    self.screen.set_focus(FOCUS_LIST)
            return

        if input_handler.is_just_pressed("down"):
            self.screen.move_cursor(1)
        elif input_handler.is_just_pressed("up"):
            self.screen.move_cursor(-1)
        elif input_handler.is_just_pressed("right"):
            self.screen.set_focus(FOCUS_MENU)
        elif input_handler.is_just_pressed("left"):
            self.screen.set_focus(FOCUS_LIST)
        elif input_handler.is_just_pressed("a"):
            if self.screen.focus == FOCUS_MENU:
                self._handle_menu_action(self.screen.get_selected_menu_option())
            else:
                self.screen.open_entry()
        elif input_handler.is_just_pressed("b"):
            if self.screen.focus == FOCUS_MENU:
                self.screen.set_focus(FOCUS_LIST)
            else:
                self.game.pop_state()

    def update(self, dt: float):
        pass

    def render(self, renderer):
        self.screen.render(renderer)
        if self.active_dialog:
            self.active_dialog.render(renderer)

    def _handle_menu_action(self, option: str) -> None:
        if option == "INFO":
            self.screen.open_entry()
            return
        if option == "QUIT":
            self.game.pop_state()
            return
        self.active_dialog = DialogBox("Not implemented.")
