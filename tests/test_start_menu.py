# ABOUTME: Tests for start menu UI component and state
# ABOUTME: Validates menu navigation, selection, and state transitions

import pytest
from unittest.mock import Mock, MagicMock
from src.ui.start_menu import StartMenu
from src.states.start_menu_state import StartMenuState


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


# StartMenuState tests

def test_start_menu_state_initializes():
    """StartMenuState should initialize with game and previous state."""
    mock_game = Mock()
    mock_previous_state = Mock()

    state = StartMenuState(mock_game, mock_previous_state)

    assert state.game == mock_game
    assert state.previous_state == mock_previous_state
    assert state.menu is not None
    assert isinstance(state.menu, StartMenu)


def test_start_menu_state_handles_down_input():
    """Should move cursor down when down is pressed."""
    mock_game = Mock()
    mock_previous_state = Mock()
    mock_input = Mock()
    mock_input.is_just_pressed = Mock(side_effect=lambda key: key == "down")

    state = StartMenuState(mock_game, mock_previous_state)
    initial_cursor = state.menu.cursor_index

    state.handle_input(mock_input)

    assert state.menu.cursor_index == initial_cursor + 1


def test_start_menu_state_handles_up_input():
    """Should move cursor up when up is pressed."""
    mock_game = Mock()
    mock_previous_state = Mock()
    mock_input = Mock()
    mock_input.is_just_pressed = Mock(side_effect=lambda key: key == "up")

    state = StartMenuState(mock_game, mock_previous_state)
    state.menu.cursor_index = 3  # Start at middle

    state.handle_input(mock_input)

    assert state.menu.cursor_index == 2


def test_start_menu_state_handles_b_to_exit():
    """Should pop state when B is pressed."""
    mock_game = Mock()
    mock_previous_state = Mock()
    mock_input = Mock()
    mock_input.is_just_pressed = Mock(side_effect=lambda key: key == "b")

    state = StartMenuState(mock_game, mock_previous_state)

    state.handle_input(mock_input)

    mock_game.pop_state.assert_called_once()


def test_start_menu_state_handles_exit_selection():
    """Should pop state when EXIT is selected."""
    mock_game = Mock()
    mock_previous_state = Mock()
    mock_input = Mock()
    mock_input.is_just_pressed = Mock(side_effect=lambda key: key == "a")

    state = StartMenuState(mock_game, mock_previous_state)
    state.menu.cursor_index = 6  # EXIT option

    state.handle_input(mock_input)

    mock_game.pop_state.assert_called_once()


def test_start_menu_state_handles_pokemon_selection():
    """Should push PartyState when POKéMON is selected."""
    import sys
    from unittest.mock import patch

    mock_game = Mock()
    mock_previous_state = Mock()
    mock_previous_state.party = Mock()
    mock_input = Mock()
    mock_input.is_just_pressed = Mock(side_effect=lambda key: key == "a")

    state = StartMenuState(mock_game, mock_previous_state)
    state.menu.cursor_index = 1  # POKéMON option

    # Mock the PartyState import since it doesn't exist yet
    mock_party_state = Mock()
    with patch.dict(sys.modules, {'src.states.party_state': Mock(PartyState=mock_party_state)}):
        state.handle_input(mock_input)

    mock_game.push_state.assert_called_once()


def test_start_menu_state_handles_unimplemented_options():
    """Should handle unimplemented menu options gracefully."""
    mock_game = Mock()
    mock_previous_state = Mock()
    mock_input = Mock()
    mock_input.is_just_pressed = Mock(side_effect=lambda key: key == "a")

    state = StartMenuState(mock_game, mock_previous_state)

    # Test POKéDEX (unimplemented)
    state.menu.cursor_index = 0
    state.handle_input(mock_input)
    mock_game.push_state.assert_not_called()
    mock_game.pop_state.assert_not_called()

    # Test ITEM (unimplemented)
    state.menu.cursor_index = 2
    state.handle_input(mock_input)
    mock_game.push_state.assert_not_called()
    mock_game.pop_state.assert_not_called()

    # Test SAVE (unimplemented)
    state.menu.cursor_index = 4
    state.handle_input(mock_input)
    mock_game.push_state.assert_not_called()
    mock_game.pop_state.assert_not_called()

    # Test OPTION (unimplemented)
    state.menu.cursor_index = 5
    state.handle_input(mock_input)
    mock_game.push_state.assert_not_called()
    mock_game.pop_state.assert_not_called()


def test_start_menu_state_update_does_nothing():
    """Update method should do nothing (no state to update)."""
    mock_game = Mock()
    mock_previous_state = Mock()

    state = StartMenuState(mock_game, mock_previous_state)

    # Should not raise any exceptions
    state.update(0.016)


def test_start_menu_state_renders_previous_state():
    """Should render previous state before rendering menu."""
    mock_game = Mock()
    mock_previous_state = Mock()
    mock_renderer = Mock()

    state = StartMenuState(mock_game, mock_previous_state)

    state.render(mock_renderer)

    mock_previous_state.render.assert_called_once_with(mock_renderer)


def test_start_menu_state_renders_menu():
    """Should render menu after previous state."""
    mock_game = Mock()
    mock_previous_state = Mock()
    mock_renderer = Mock()

    state = StartMenuState(mock_game, mock_previous_state)
    state.menu.render = Mock()

    state.render(mock_renderer)

    state.menu.render.assert_called_once_with(mock_renderer)


def test_start_menu_state_renders_without_previous_state():
    """Should handle rendering when previous_state is None."""
    mock_game = Mock()
    mock_renderer = Mock()

    state = StartMenuState(mock_game, None)

    # Should not raise exception
    state.render(mock_renderer)
