# ABOUTME: Tests party screen HP display ticking behavior
# ABOUTME: Ensures party HP display updates by bar units over time

from src.party.party import Party
from src.battle.pokemon import Pokemon
from src.battle.species_loader import SpeciesLoader
from src.ui.party_screen import PartyScreen


def build_pokemon(species_id: str, level: int = 5) -> Pokemon:
    species = SpeciesLoader().get_species(species_id)
    return Pokemon(species, level)


def test_party_screen_hp_ticks_on_damage():
    party = Party()
    pokemon = build_pokemon("pikachu")
    party.add(pokemon)

    screen = PartyScreen(party)
    start_units = screen.get_display_units(0)

    pokemon.current_hp = max(1, pokemon.current_hp - 5)
    screen.update(0.02)

    assert screen.get_display_units(0) == start_units - 1


def test_party_screen_hp_heal_ticks_slower():
    party = Party()
    pokemon = build_pokemon("pikachu")
    pokemon.current_hp = max(1, pokemon.current_hp - 10)
    party.add(pokemon)

    screen = PartyScreen(party)
    start_units = screen.get_display_units(0)

    pokemon.current_hp = pokemon.stats.hp
    screen.update(0.02)

    assert screen.get_display_units(0) == start_units
