# ABOUTME: Tests for party management system
# ABOUTME: Validates party operations (add, remove, reorder, limits)

import pytest
from src.party.party import Party
from src.battle.pokemon import Pokemon
from src.battle.species_loader import SpeciesLoader


@pytest.fixture
def species_loader():
    """Fixture to provide SpeciesLoader instance."""
    return SpeciesLoader()


def test_party_initializes_empty():
    """Party should initialize with no Pokemon."""
    party = Party()
    assert party.size() == 0


def test_party_add_pokemon(species_loader):
    """Should add Pokemon to party."""
    party = Party()
    pikachu_species = species_loader.get_species("pikachu")
    pikachu = Pokemon(pikachu_species, 5)

    party.add(pikachu)

    assert party.size() == 1
    assert party.pokemon[0] == pikachu


def test_party_max_size_is_six(species_loader):
    """Party should not exceed 6 Pokemon."""
    party = Party()
    pikachu_species = species_loader.get_species("pikachu")

    # Add 6 Pokemon
    for i in range(6):
        party.add(Pokemon(pikachu_species, 5))

    assert party.size() == 6
    assert party.is_full()

    # Try to add 7th
    result = party.add(Pokemon(pikachu_species, 5))
    assert result is False
    assert party.size() == 6


def test_party_get_active_pokemon(species_loader):
    """First Pokemon in party is active."""
    party = Party()
    pikachu_species = species_loader.get_species("pikachu")
    pikachu = Pokemon(pikachu_species, 5)

    party.add(pikachu)

    assert party.get_active() == pikachu


def test_party_remove_pokemon(species_loader):
    """Should remove Pokemon from party."""
    party = Party()
    pikachu_species = species_loader.get_species("pikachu")
    pikachu = Pokemon(pikachu_species, 5)

    party.add(pikachu)
    party.remove(0)

    assert party.size() == 0


def test_party_swap_pokemon(species_loader):
    """Should swap positions of two Pokemon."""
    party = Party()
    pikachu_species = species_loader.get_species("pikachu")
    rattata_species = species_loader.get_species("rattata")

    pikachu = Pokemon(pikachu_species, 5)
    rattata = Pokemon(rattata_species, 3)

    party.add(pikachu)
    party.add(rattata)

    party.swap(0, 1)

    assert party.pokemon[0] == rattata
    assert party.pokemon[1] == pikachu


def test_remove_with_invalid_index_returns_none(species_loader):
    """Should return None when removing with invalid index."""
    party = Party()
    pikachu_species = species_loader.get_species("pikachu")
    pikachu = Pokemon(pikachu_species, 5)

    party.add(pikachu)

    # Test negative index
    assert party.remove(-1) is None
    assert party.size() == 1

    # Test out of bounds index
    assert party.remove(10) is None
    assert party.size() == 1


def test_swap_with_invalid_indices_returns_false(species_loader):
    """Should return False when swapping with invalid indices."""
    party = Party()
    pikachu_species = species_loader.get_species("pikachu")
    rattata_species = species_loader.get_species("rattata")

    pikachu = Pokemon(pikachu_species, 5)
    rattata = Pokemon(rattata_species, 3)

    party.add(pikachu)
    party.add(rattata)

    # Test negative index
    assert party.swap(-1, 0) is False
    assert party.pokemon[0] == pikachu

    # Test out of bounds index
    assert party.swap(0, 10) is False
    assert party.pokemon[0] == pikachu

    # Test both invalid
    assert party.swap(-1, 10) is False
    assert party.pokemon[0] == pikachu


def test_get_active_when_party_empty_returns_none():
    """Should return None when party is empty."""
    party = Party()
    assert party.get_active() is None


def test_get_active_when_all_fainted_returns_none(species_loader):
    """Should return None when all Pokemon are fainted."""
    party = Party()
    pikachu_species = species_loader.get_species("pikachu")
    rattata_species = species_loader.get_species("rattata")

    pikachu = Pokemon(pikachu_species, 5)
    rattata = Pokemon(rattata_species, 3)

    # Faint both Pokemon
    pikachu.current_hp = 0
    rattata.current_hp = 0

    party.add(pikachu)
    party.add(rattata)

    assert party.get_active() is None


def test_get_all_alive_filters_fainted_pokemon(species_loader):
    """Should only return non-fainted Pokemon."""
    party = Party()
    pikachu_species = species_loader.get_species("pikachu")
    rattata_species = species_loader.get_species("rattata")
    pidgey_species = species_loader.get_species("pidgey")

    pikachu = Pokemon(pikachu_species, 5)
    rattata = Pokemon(rattata_species, 3)
    pidgey = Pokemon(pidgey_species, 4)

    # Faint rattata
    rattata.current_hp = 0

    party.add(pikachu)
    party.add(rattata)
    party.add(pidgey)

    alive = party.get_all_alive()
    assert len(alive) == 2
    assert pikachu in alive
    assert rattata not in alive
    assert pidgey in alive


def test_has_alive_pokemon_with_all_fainted(species_loader):
    """Should return False when all Pokemon are fainted."""
    party = Party()
    pikachu_species = species_loader.get_species("pikachu")
    rattata_species = species_loader.get_species("rattata")

    pikachu = Pokemon(pikachu_species, 5)
    rattata = Pokemon(rattata_species, 3)

    # Faint both Pokemon
    pikachu.current_hp = 0
    rattata.current_hp = 0

    party.add(pikachu)
    party.add(rattata)

    assert party.has_alive_pokemon() is False


def test_has_alive_pokemon_with_some_alive(species_loader):
    """Should return True when at least one Pokemon is alive."""
    party = Party()
    pikachu_species = species_loader.get_species("pikachu")
    rattata_species = species_loader.get_species("rattata")

    pikachu = Pokemon(pikachu_species, 5)
    rattata = Pokemon(rattata_species, 3)

    # Faint only rattata
    rattata.current_hp = 0

    party.add(pikachu)
    party.add(rattata)

    assert party.has_alive_pokemon() is True
