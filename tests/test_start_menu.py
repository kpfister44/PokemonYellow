# ABOUTME: Tests for start menu UI component and state
# ABOUTME: Validates menu navigation, selection, and state transitions

from dataclasses import dataclass

from src.ui.start_menu import StartMenu
from src.engine import constants
from src.states.start_menu_state import StartMenuState
from src.party.party import Party
from src.items.bag import Bag


class FakeInput:
    def __init__(self, pressed: set[str]):
        self.pressed = pressed

    def is_just_pressed(self, key: str) -> bool:
        return key in self.pressed


class FakeGame:
    def __init__(self):
        self.state_stack = []
        self.pushed = []
        self.pop_count = 0

    def push_state(self, state):
        self.pushed.append(state)
        self.state_stack.append(state)

    def pop_state(self):
        self.pop_count += 1
        if self.state_stack:
            self.state_stack.pop()


class FakeRenderer:
    def __init__(self):
        self.rects = []

    def draw_rect(self, _color, _rect, _width):
        self.rects.append(_rect)

    def draw_text(self, _text, _x, _y, _color=None, _size=None, font_size=None):
        pass


@dataclass
class FakePreviousState:
    party: Party | None = None
    bag: Bag | None = None
    render_called: bool = False

    def render(self, renderer):
        self.render_called = True


def test_start_menu_initializes_with_options():
    """Start menu should have correct options."""
    menu = StartMenu()

    expected_options = [
        "POKéDEX",
        "POKéMON",
        "ITEM",
        "PLAYER",  # Placeholder for player name
        "SAVE",
        "OPTION",
        "EXIT"
    ]

    assert menu.options == expected_options
    assert menu.cursor_index == 0


def test_start_menu_cursor_navigation():
    """Should navigate cursor up and down."""
    menu = StartMenu()

    # Start at 0
    assert menu.cursor_index == 0

    # Move down
    menu.move_cursor(1)
    assert menu.cursor_index == 1

    # Move down to last
    for _ in range(5):
        menu.move_cursor(1)
    assert menu.cursor_index == 6

    # Wrap around to top
    menu.move_cursor(1)
    assert menu.cursor_index == 0

    # Move up wraps to bottom
    menu.move_cursor(-1)
    assert menu.cursor_index == 6


def test_start_menu_get_selection():
    """Should return current selection."""
    menu = StartMenu()

    assert menu.get_selection() == "POKéDEX"

    menu.move_cursor(1)
    assert menu.get_selection() == "POKéMON"

    menu.cursor_index = 6
    assert menu.get_selection() == "EXIT"


def test_start_menu_render_fits_screen():
    menu = StartMenu()
    renderer = FakeRenderer()

    menu.render(renderer)

    assert renderer.rects
    for rect in renderer.rects:
        x, y, width, height = rect
        assert x >= 0
        assert y >= 0
        assert x + width <= constants.GAME_WIDTH
        assert y + height <= constants.GAME_HEIGHT


# StartMenuState tests

def test_start_menu_state_initializes():
    """StartMenuState should initialize with game and previous state."""
    game = FakeGame()
    previous_state = FakePreviousState()

    state = StartMenuState(game, previous_state)

    assert state.game == game
    assert state.previous_state == previous_state
    assert state.menu is not None
    assert isinstance(state.menu, StartMenu)


def test_start_menu_state_handles_down_input():
    """Should move cursor down when down is pressed."""
    game = FakeGame()
    previous_state = FakePreviousState()
    fake_input = FakeInput({"down"})

    state = StartMenuState(game, previous_state)
    initial_cursor = state.menu.cursor_index

    state.handle_input(fake_input)

    assert state.menu.cursor_index == initial_cursor + 1


def test_start_menu_state_handles_up_input():
    """Should move cursor up when up is pressed."""
    game = FakeGame()
    previous_state = FakePreviousState()
    fake_input = FakeInput({"up"})

    state = StartMenuState(game, previous_state)
    state.menu.cursor_index = 3  # Start at middle

    state.handle_input(fake_input)

    assert state.menu.cursor_index == 2


def test_start_menu_state_handles_b_to_exit():
    """Should pop state when B is pressed."""
    game = FakeGame()
    previous_state = FakePreviousState()
    fake_input = FakeInput({"b"})

    state = StartMenuState(game, previous_state)

    state.handle_input(fake_input)

    assert game.pop_count == 1


def test_start_menu_state_handles_exit_selection():
    """Should pop state when EXIT is selected."""
    game = FakeGame()
    previous_state = FakePreviousState()
    fake_input = FakeInput({"a"})

    state = StartMenuState(game, previous_state)
    state.menu.cursor_index = 6  # EXIT option

    state.handle_input(fake_input)

    assert game.pop_count == 1


def test_start_menu_state_handles_pokemon_selection():
    """Should push PartyState when POKéMON is selected."""
    game = FakeGame()
    previous_state = FakePreviousState(party=Party())
    fake_input = FakeInput({"a"})

    state = StartMenuState(game, previous_state)
    state.menu.cursor_index = 1  # POKéMON option

    state.handle_input(fake_input)

    assert len(game.pushed) == 1


def test_start_menu_state_handles_unimplemented_options():
    """Should handle unimplemented menu options gracefully."""
    game = FakeGame()
    previous_state = FakePreviousState()
    fake_input = FakeInput({"a"})

    state = StartMenuState(game, previous_state)

    # Test POKéDEX
    state.menu.cursor_index = 0
    state.handle_input(fake_input)
    assert len(game.pushed) == 1
    assert game.pop_count == 0
    game.pushed.clear()

    # Test SAVE (unimplemented)
    state.menu.cursor_index = 4
    state.handle_input(fake_input)
    assert len(game.pushed) == 0
    assert game.pop_count == 0

    # Test OPTION (unimplemented)
    state.menu.cursor_index = 5
    state.handle_input(fake_input)
    assert len(game.pushed) == 0
    assert game.pop_count == 0


def test_start_menu_state_handles_item_selection():
    """Should push BagState when ITEM is selected and bag exists."""
    game = FakeGame()
    previous_state = FakePreviousState(party=Party(), bag=Bag())
    fake_input = FakeInput({"a"})

    state = StartMenuState(game, previous_state)
    state.menu.cursor_index = 2  # ITEM option

    state.handle_input(fake_input)

    assert len(game.pushed) == 1


def test_start_menu_state_update_does_nothing():
    """Update method should do nothing (no state to update)."""
    game = FakeGame()
    previous_state = FakePreviousState()

    state = StartMenuState(game, previous_state)

    # Should not raise any exceptions
    state.update(0.016)


def test_start_menu_state_renders_previous_state():
    """Should render previous state before rendering menu."""
    game = FakeGame()
    previous_state = FakePreviousState()
    renderer = FakeRenderer()

    state = StartMenuState(game, previous_state)

    state.render(renderer)

    assert previous_state.render_called is True


def test_start_menu_state_renders_menu():
    """Should render menu after previous state."""
    game = FakeGame()
    previous_state = FakePreviousState()
    renderer = FakeRenderer()

    state = StartMenuState(game, previous_state)
    render_called = {"called": False}
    def fake_render(_renderer):
        render_called["called"] = True
    state.menu.render = fake_render

    state.render(renderer)

    assert render_called["called"] is True


def test_start_menu_state_renders_without_previous_state():
    """Should handle rendering when previous_state is None."""
    game = FakeGame()
    renderer = FakeRenderer()

    state = StartMenuState(game, None)

    # Should not raise exception
    state.render(renderer)


def test_start_menu_state_handles_save_selection(monkeypatch):
    """Should save and show confirmation dialog when SAVE is selected."""
    game = FakeGame()

    class StubPlayer:
        def to_dict(self):
            return {"tile_x": 1, "tile_y": 2, "direction": "down"}

    @dataclass
    class FakeSaveState:
        party: Party
        bag: Bag
        player: StubPlayer
        map_path: str
        active_dialog: object | None = None
        defeated_trainers: set[str] = None
        collected_items: set[str] = None

        def __post_init__(self):
            if self.defeated_trainers is None:
                self.defeated_trainers = set()
            if self.collected_items is None:
                self.collected_items = set()

        def render(self, renderer):
            pass

    previous_state = FakeSaveState(
        party=Party(),
        bag=Bag(),
        player=StubPlayer(),
        map_path="assets/maps/pallet_town.tmx"
    )

    captured = {}

    def fake_write_save_data(save_data):
        captured["save_data"] = save_data

    monkeypatch.setattr("src.save.save_storage.write_save_data", fake_write_save_data)

    fake_input = FakeInput({"a"})
    state = StartMenuState(game, previous_state)
    state.menu.cursor_index = 4  # SAVE option

    state.handle_input(fake_input)

    assert "save_data" in captured
    assert previous_state.active_dialog is not None
    assert getattr(previous_state.active_dialog, "text", None) == "PLAYER saved the game."
