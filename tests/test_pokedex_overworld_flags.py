# ABOUTME: Tests for pokedex flags in overworld state
# ABOUTME: Ensures party Pokemon are recorded as seen and caught

from src.battle.pokemon import Pokemon
from src.battle.species_loader import SpeciesLoader
from src.items.bag import Bag
from src.party.party import Party
from src.states.overworld_state import OverworldState


class DummyGame:
    pass


def test_party_pokemon_marked_seen_and_caught():
    """Party Pokemon should be added to pokedex flags on load."""
    species_loader = SpeciesLoader()
    party = Party()
    party.add(Pokemon(species_loader.get_species("pikachu"), 5))

    state = OverworldState(
        DummyGame(),
        "data/maps/pallet_town.json",
        party=party,
        bag=Bag(),
        pokedex_seen=set(),
        pokedex_caught=set()
    )

    assert "pikachu" in state.pokedex_seen
    assert "pikachu" in state.pokedex_caught
