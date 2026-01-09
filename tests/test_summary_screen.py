# ABOUTME: Tests for summary screen UI component and state
# ABOUTME: Validates Pokemon summary pages, navigation, and state transitions

import pytest
from unittest.mock import Mock
from src.ui.summary_screen import SummaryScreen
from src.states.summary_state import SummaryState
from src.party.party import Party
from src.battle.pokemon import Pokemon
from src.battle.species_loader import SpeciesLoader


@pytest.fixture
def species_loader():
    """Fixture for SpeciesLoader."""
    return SpeciesLoader()


@pytest.fixture
def pikachu(species_loader):
    """Fixture for a test Pikachu."""
    species = species_loader.get_species("pikachu")
    return Pokemon(species, 25)


@pytest.fixture
def party_with_pokemon(species_loader):
    """Fixture for a party with multiple Pokemon."""
    party = Party()
    for species_id, level in [("pikachu", 25), ("rattata", 10), ("squirtle", 15)]:
        species = species_loader.get_species(species_id)
        party.add(Pokemon(species, level))
    return party


# SummaryScreen tests

def test_summary_screen_initializes(pikachu, party_with_pokemon):
    """Summary screen should initialize with Pokemon and party."""
    screen = SummaryScreen(pikachu, party_with_pokemon)

    assert screen.pokemon == pikachu
    assert screen.party == party_with_pokemon
    assert screen.current_page == 0  # INFO page
    assert screen.pokemon_index == 0  # First Pokemon in party


def test_summary_screen_change_page_forward(pikachu, party_with_pokemon):
    """Should change from INFO to MOVES page."""
    screen = SummaryScreen(pikachu, party_with_pokemon)

    screen.change_page(1)

    assert screen.current_page == 1  # MOVES page


def test_summary_screen_change_page_backward(pikachu, party_with_pokemon):
    """Should change from MOVES to INFO page."""
    screen = SummaryScreen(pikachu, party_with_pokemon)
    screen.current_page = 1  # Start at MOVES

    screen.change_page(-1)

    assert screen.current_page == 0  # INFO page


def test_summary_screen_change_page_wraps_forward(pikachu, party_with_pokemon):
    """Should wrap from MOVES page back to INFO page."""
    screen = SummaryScreen(pikachu, party_with_pokemon)
    screen.current_page = 1  # Start at MOVES

    screen.change_page(1)

    assert screen.current_page == 0  # Wraps to INFO


def test_summary_screen_change_page_wraps_backward(pikachu, party_with_pokemon):
    """Should wrap from INFO page to MOVES page."""
    screen = SummaryScreen(pikachu, party_with_pokemon)

    screen.change_page(-1)

    assert screen.current_page == 1  # Wraps to MOVES


def test_summary_screen_change_pokemon_forward(pikachu, party_with_pokemon):
    """Should switch to next Pokemon in party."""
    screen = SummaryScreen(pikachu, party_with_pokemon)

    screen.change_pokemon(1)

    assert screen.pokemon_index == 1
    assert screen.pokemon == party_with_pokemon.pokemon[1]


def test_summary_screen_change_pokemon_backward(party_with_pokemon):
    """Should switch to previous Pokemon in party."""
    second_pokemon = party_with_pokemon.pokemon[1]
    screen = SummaryScreen(second_pokemon, party_with_pokemon)
    screen.pokemon_index = 1  # Start at second

    screen.change_pokemon(-1)

    assert screen.pokemon_index == 0
    assert screen.pokemon == party_with_pokemon.pokemon[0]


def test_summary_screen_change_pokemon_wraps_forward(party_with_pokemon):
    """Should wrap from last Pokemon to first."""
    last_pokemon = party_with_pokemon.pokemon[2]
    screen = SummaryScreen(last_pokemon, party_with_pokemon)
    screen.pokemon_index = 2  # Start at last

    screen.change_pokemon(1)

    assert screen.pokemon_index == 0
    assert screen.pokemon == party_with_pokemon.pokemon[0]


def test_summary_screen_change_pokemon_wraps_backward(pikachu, party_with_pokemon):
    """Should wrap from first Pokemon to last."""
    screen = SummaryScreen(pikachu, party_with_pokemon)

    screen.change_pokemon(-1)

    assert screen.pokemon_index == 2
    assert screen.pokemon == party_with_pokemon.pokemon[2]


def test_summary_screen_single_pokemon_navigation(species_loader):
    """Should handle navigation with single Pokemon in party."""
    party = Party()
    pikachu_species = species_loader.get_species("pikachu")
    pikachu = Pokemon(pikachu_species, 25)
    party.add(pikachu)

    screen = SummaryScreen(pikachu, party)

    # Should wrap to same Pokemon
    screen.change_pokemon(1)
    assert screen.pokemon_index == 0
    assert screen.pokemon == pikachu

    screen.change_pokemon(-1)
    assert screen.pokemon_index == 0
    assert screen.pokemon == pikachu


def test_summary_screen_renders_info_page(pikachu, party_with_pokemon):
    """Should render INFO page without errors."""
    screen = SummaryScreen(pikachu, party_with_pokemon)
    mock_renderer = Mock()

    # Should not raise any exceptions
    screen.render(mock_renderer)


def test_summary_screen_renders_moves_page(pikachu, party_with_pokemon):
    """Should render MOVES page without errors."""
    screen = SummaryScreen(pikachu, party_with_pokemon)
    screen.current_page = 1  # MOVES page
    mock_renderer = Mock()

    # Should not raise any exceptions
    screen.render(mock_renderer)


# SummaryState tests

def test_summary_state_initializes(pikachu, party_with_pokemon):
    """SummaryState should initialize with game, Pokemon, and party."""
    mock_game = Mock()

    state = SummaryState(mock_game, pikachu, party_with_pokemon)

    assert state.game == mock_game
    assert state.screen is not None
    assert isinstance(state.screen, SummaryScreen)
    assert state.screen.pokemon == pikachu
    assert state.screen.party == party_with_pokemon


def test_summary_state_handles_left_input(pikachu, party_with_pokemon):
    """Should change page backward when left is pressed."""
    mock_game = Mock()
    mock_input = Mock()
    mock_input.is_just_pressed = Mock(side_effect=lambda key: key == "left")

    state = SummaryState(mock_game, pikachu, party_with_pokemon)
    state.screen.current_page = 1  # Start at MOVES

    state.handle_input(mock_input)

    assert state.screen.current_page == 0  # Changed to INFO


def test_summary_state_handles_right_input(pikachu, party_with_pokemon):
    """Should change page forward when right is pressed."""
    mock_game = Mock()
    mock_input = Mock()
    mock_input.is_just_pressed = Mock(side_effect=lambda key: key == "right")

    state = SummaryState(mock_game, pikachu, party_with_pokemon)

    state.handle_input(mock_input)

    assert state.screen.current_page == 1  # Changed to MOVES


def test_summary_state_handles_up_input(party_with_pokemon):
    """Should switch to previous Pokemon when up is pressed."""
    mock_game = Mock()
    mock_input = Mock()
    mock_input.is_just_pressed = Mock(side_effect=lambda key: key == "up")

    second_pokemon = party_with_pokemon.pokemon[1]
    state = SummaryState(mock_game, second_pokemon, party_with_pokemon)
    state.screen.pokemon_index = 1

    state.handle_input(mock_input)

    assert state.screen.pokemon_index == 0


def test_summary_state_handles_down_input(pikachu, party_with_pokemon):
    """Should switch to next Pokemon when down is pressed."""
    mock_game = Mock()
    mock_input = Mock()
    mock_input.is_just_pressed = Mock(side_effect=lambda key: key == "down")

    state = SummaryState(mock_game, pikachu, party_with_pokemon)

    state.handle_input(mock_input)

    assert state.screen.pokemon_index == 1


def test_summary_state_handles_b_to_exit(pikachu, party_with_pokemon):
    """Should pop state when B is pressed."""
    mock_game = Mock()
    mock_input = Mock()
    mock_input.is_just_pressed = Mock(side_effect=lambda key: key == "b")

    state = SummaryState(mock_game, pikachu, party_with_pokemon)

    state.handle_input(mock_input)

    mock_game.pop_state.assert_called_once()


def test_summary_state_handles_a_to_exit(pikachu, party_with_pokemon):
    """Should pop state when A is pressed."""
    mock_game = Mock()
    mock_input = Mock()
    mock_input.is_just_pressed = Mock(side_effect=lambda key: key == "a")

    state = SummaryState(mock_game, pikachu, party_with_pokemon)

    state.handle_input(mock_input)

    mock_game.pop_state.assert_called_once()


def test_summary_state_update_does_nothing(pikachu, party_with_pokemon):
    """Update method should do nothing."""
    mock_game = Mock()

    state = SummaryState(mock_game, pikachu, party_with_pokemon)

    # Should not raise any exceptions
    state.update(0.016)


def test_summary_state_renders_screen(pikachu, party_with_pokemon):
    """Should render summary screen."""
    mock_game = Mock()
    mock_renderer = Mock()

    state = SummaryState(mock_game, pikachu, party_with_pokemon)
    state.screen.render = Mock()

    state.render(mock_renderer)

    state.screen.render.assert_called_once_with(mock_renderer)
