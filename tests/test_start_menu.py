# ABOUTME: Tests for start menu UI component
# ABOUTME: Validates menu navigation and selection

import pytest
from src.ui.start_menu import StartMenu


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
