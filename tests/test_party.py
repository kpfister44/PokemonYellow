# ABOUTME: Tests for party management system
# ABOUTME: Validates party operations (add, remove, reorder, limits)

import pytest
from src.party.party import Party
from src.battle.pokemon import Pokemon
from src.battle.species_loader import SpeciesLoader


def test_party_initializes_empty():
    """Party should initialize with no Pokemon."""
    party = Party()
    assert len(party.pokemon) == 0
    assert party.size() == 0


def test_party_add_pokemon():
    """Should add Pokemon to party."""
    party = Party()
    species_loader = SpeciesLoader()
    pikachu_species = species_loader.get_species("pikachu")
    pikachu = Pokemon(pikachu_species, 5)

    party.add(pikachu)

    assert party.size() == 1
    assert party.pokemon[0] == pikachu


def test_party_max_size_is_six():
    """Party should not exceed 6 Pokemon."""
    party = Party()
    species_loader = SpeciesLoader()
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


def test_party_get_active_pokemon():
    """First Pokemon in party is active."""
    party = Party()
    species_loader = SpeciesLoader()
    pikachu_species = species_loader.get_species("pikachu")
    pikachu = Pokemon(pikachu_species, 5)

    party.add(pikachu)

    assert party.get_active() == pikachu


def test_party_remove_pokemon():
    """Should remove Pokemon from party."""
    party = Party()
    species_loader = SpeciesLoader()
    pikachu_species = species_loader.get_species("pikachu")
    pikachu = Pokemon(pikachu_species, 5)

    party.add(pikachu)
    party.remove(0)

    assert party.size() == 0


def test_party_swap_pokemon():
    """Should swap positions of two Pokemon."""
    party = Party()
    species_loader = SpeciesLoader()
    pikachu_species = species_loader.get_species("pikachu")
    rattata_species = species_loader.get_species("rattata")

    pikachu = Pokemon(pikachu_species, 5)
    rattata = Pokemon(rattata_species, 3)

    party.add(pikachu)
    party.add(rattata)

    party.swap(0, 1)

    assert party.pokemon[0] == rattata
    assert party.pokemon[1] == pikachu
