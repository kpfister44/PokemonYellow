# ABOUTME: Tests for party screen UI component
# ABOUTME: Validates party list rendering and navigation

import pytest
from src.ui.party_screen import PartyScreen
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
