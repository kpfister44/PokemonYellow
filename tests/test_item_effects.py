# ABOUTME: Tests item effect application for supported items
# ABOUTME: Validates healing, status cure, and revive behavior

from src.battle.pokemon import Pokemon
from src.battle.species_loader import SpeciesLoader
from src.battle.status_effects import StatusCondition
from src.items.item_effects import ItemEffects, ItemUseContext


def build_pokemon() -> Pokemon:
    species = SpeciesLoader().get_species("pikachu")
    return Pokemon(species, 5)


def test_potion_heals_in_overworld():
    pokemon = build_pokemon()
    pokemon.current_hp = max(1, pokemon.current_hp - 30)
    start_hp = pokemon.current_hp

    effects = ItemEffects()
    result = effects.use_item("potion", pokemon, ItemUseContext(mode="overworld"))

    assert result.success is True
    assert result.consumed is True
    assert pokemon.current_hp == min(pokemon.stats.hp, start_hp + 20)


def test_antidote_cures_poison():
    pokemon = build_pokemon()
    pokemon.status = StatusCondition.POISON

    effects = ItemEffects()
    result = effects.use_item("antidote", pokemon, ItemUseContext(mode="overworld"))

    assert result.success is True
    assert result.consumed is True
    assert pokemon.status is None


def test_revive_requires_fainted_target():
    pokemon = build_pokemon()
    pokemon.current_hp = 0

    effects = ItemEffects()
    result = effects.use_item("revive", pokemon, ItemUseContext(mode="overworld"))

    assert result.success is True
    assert result.consumed is True
    assert pokemon.current_hp == max(1, pokemon.stats.hp // 2)


def test_revive_fails_on_healthy_target():
    pokemon = build_pokemon()

    effects = ItemEffects()
    result = effects.use_item("revive", pokemon, ItemUseContext(mode="overworld"))

    assert result.success is False
    assert result.consumed is False
