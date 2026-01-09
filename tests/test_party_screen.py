# ABOUTME: Tests for party screen UI component and state
# ABOUTME: Validates party list rendering, navigation, and state transitions

import pytest
from unittest.mock import Mock
from src.ui.party_screen import PartyScreen
from src.states.party_state import PartyState
from src.party.party import Party
from src.battle.pokemon import Pokemon
from src.battle.species_loader import SpeciesLoader


@pytest.fixture
def species_loader():
    """Fixture for SpeciesLoader."""
    return SpeciesLoader()


def test_party_screen_initializes(species_loader):
    """Party screen should initialize with party."""
    party = Party()
    screen = PartyScreen(party)

    assert screen.party == party
    assert screen.cursor_index == 0


def test_party_screen_cursor_navigation(species_loader):
    """Should navigate cursor through party."""
    party = Party()

    # Add 3 Pokemon
    for species_id in ["pikachu", "rattata", "squirtle"]:
        species = species_loader.get_species(species_id)
        party.add(Pokemon(species, 5))

    screen = PartyScreen(party)

    # Navigate down
    screen.move_cursor(1)
    assert screen.cursor_index == 1

    screen.move_cursor(1)
    assert screen.cursor_index == 2

    # At last Pokemon, wrap to first
    screen.move_cursor(1)
    assert screen.cursor_index == 0

    # Navigate up wraps to last
    screen.move_cursor(-1)
    assert screen.cursor_index == 2


def test_party_screen_get_selected_pokemon(species_loader):
    """Should return selected Pokemon."""
    party = Party()
    pikachu_species = species_loader.get_species("pikachu")
    pikachu = Pokemon(pikachu_species, 5)

    party.add(pikachu)
    screen = PartyScreen(party)

    assert screen.get_selected_pokemon() == pikachu


def test_party_screen_empty_party_navigation():
    """Should handle navigation with empty party."""
    party = Party()
    screen = PartyScreen(party)

    # Cursor should stay at 0 with empty party
    assert screen.cursor_index == 0

    screen.move_cursor(1)
    assert screen.cursor_index == 0

    screen.move_cursor(-1)
    assert screen.cursor_index == 0


def test_party_screen_empty_party_selection():
    """Should return None for empty party selection."""
    party = Party()
    screen = PartyScreen(party)

    assert screen.get_selected_pokemon() is None


# PartyState tests

def test_party_state_initializes(species_loader):
    """PartyState should initialize with game and party."""
    mock_game = Mock()
    party = Party()

    state = PartyState(mock_game, party)

    assert state.game == mock_game
    assert state.party == party
    assert state.mode == "view"
    assert state.screen is not None
    assert isinstance(state.screen, PartyScreen)


def test_party_state_initializes_with_mode(species_loader):
    """PartyState should accept mode parameter."""
    mock_game = Mock()
    party = Party()

    state = PartyState(mock_game, party, mode="switch")

    assert state.mode == "switch"


def test_party_state_handles_down_input(species_loader):
    """Should move cursor down when down is pressed."""
    mock_game = Mock()
    party = Party()

    # Add Pokemon so cursor can move
    for species_id in ["pikachu", "rattata"]:
        species = species_loader.get_species(species_id)
        party.add(Pokemon(species, 5))

    mock_input = Mock()
    mock_input.is_just_pressed = Mock(side_effect=lambda key: key == "down")

    state = PartyState(mock_game, party)
    initial_cursor = state.screen.cursor_index

    state.handle_input(mock_input)

    assert state.screen.cursor_index == initial_cursor + 1


def test_party_state_handles_up_input(species_loader):
    """Should move cursor up when up is pressed."""
    mock_game = Mock()
    party = Party()

    # Add Pokemon
    for species_id in ["pikachu", "rattata", "squirtle"]:
        species = species_loader.get_species(species_id)
        party.add(Pokemon(species, 5))

    mock_input = Mock()
    mock_input.is_just_pressed = Mock(side_effect=lambda key: key == "up")

    state = PartyState(mock_game, party)
    state.screen.cursor_index = 1  # Start at middle

    state.handle_input(mock_input)

    assert state.screen.cursor_index == 0


def test_party_state_handles_b_to_exit(species_loader):
    """Should pop state when B is pressed."""
    mock_game = Mock()
    party = Party()
    mock_input = Mock()
    mock_input.is_just_pressed = Mock(side_effect=lambda key: key == "b")

    state = PartyState(mock_game, party)

    state.handle_input(mock_input)

    mock_game.pop_state.assert_called_once()


def test_party_state_handles_a_with_no_selection(species_loader):
    """Should handle A press with no Pokemon selected."""
    mock_game = Mock()
    party = Party()  # Empty party
    mock_input = Mock()
    mock_input.is_just_pressed = Mock(side_effect=lambda key: key == "a")

    state = PartyState(mock_game, party)

    state.handle_input(mock_input)

    # Should not crash, should not push any state
    mock_game.push_state.assert_not_called()


def test_party_state_handles_a_with_selection_no_summary_state(species_loader):
    """Should handle A press gracefully when SummaryState not implemented."""
    mock_game = Mock()
    party = Party()

    # Add a Pokemon
    pikachu_species = species_loader.get_species("pikachu")
    party.add(Pokemon(pikachu_species, 5))

    mock_input = Mock()
    mock_input.is_just_pressed = Mock(side_effect=lambda key: key == "a")

    state = PartyState(mock_game, party)

    # Should not crash even though SummaryState doesn't exist
    state.handle_input(mock_input)

    # SummaryState doesn't exist, so push_state should not be called
    mock_game.push_state.assert_not_called()


def test_party_state_update_does_nothing(species_loader):
    """Update method should do nothing."""
    mock_game = Mock()
    party = Party()

    state = PartyState(mock_game, party)

    # Should not raise any exceptions
    state.update(0.016)


def test_party_state_renders_screen(species_loader):
    """Should render party screen."""
    mock_game = Mock()
    party = Party()
    mock_renderer = Mock()

    state = PartyState(mock_game, party)
    state.screen.render = Mock()

    state.render(mock_renderer)

    state.screen.render.assert_called_once_with(mock_renderer)


def test_party_state_handles_empty_party_input(species_loader):
    """Should handle all inputs with empty party."""
    mock_game = Mock()
    party = Party()  # Empty party

    state = PartyState(mock_game, party)

    # Test down
    mock_input = Mock()
    mock_input.is_just_pressed = Mock(side_effect=lambda key: key == "down")
    state.handle_input(mock_input)
    assert state.screen.cursor_index == 0

    # Test up
    mock_input.is_just_pressed = Mock(side_effect=lambda key: key == "up")
    state.handle_input(mock_input)
    assert state.screen.cursor_index == 0

    # Test A
    mock_input.is_just_pressed = Mock(side_effect=lambda key: key == "a")
    state.handle_input(mock_input)
    mock_game.push_state.assert_not_called()

    # Test B
    mock_input.is_just_pressed = Mock(side_effect=lambda key: key == "b")
    state.handle_input(mock_input)
    mock_game.pop_state.assert_called_once()
