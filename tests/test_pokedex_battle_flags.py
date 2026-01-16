# ABOUTME: Tests for pokedex updates during battles
# ABOUTME: Validates seen/caught flags are updated when battling

from src.battle.pokemon import Pokemon
from src.battle.species import BaseStats, Species
from src.states.battle_state import BattleState


def make_species(name: str) -> Species:
    return Species(
        species_id=name.lower(),
        number=1,
        name=name,
        genus="",
        height=0,
        weight=0,
        types=["normal"],
        base_stats=BaseStats(hp=10, attack=10, defense=10, special=10, speed=10),
        base_experience=0,
        growth_rate="medium",
        capture_rate=255,
        base_happiness=70,
        gender_rate=-1,
        pokedex_entry="",
        evolution_chain={},
        level_up_moves=[],
        sprites=None,
    )


class DummyGame:
    pass


def test_battle_marks_seen_on_enemy_species():
    """Battle should mark enemy species as seen."""
    player = Pokemon(make_species("Player"), 5)
    enemy = Pokemon(make_species("Rattata"), 3)
    state = BattleState(DummyGame(), player, enemy)
    state.pokedex_seen = set()
    state.pokedex_caught = set()

    state._mark_seen()

    assert "rattata" in state.pokedex_seen


def test_battle_marks_caught_adds_seen():
    """Caught species should be marked as caught and seen."""
    player = Pokemon(make_species("Player"), 5)
    enemy = Pokemon(make_species("Rattata"), 3)
    state = BattleState(DummyGame(), player, enemy)
    state.pokedex_seen = set()
    state.pokedex_caught = set()

    state._mark_caught()

    assert "rattata" in state.pokedex_caught
    assert "rattata" in state.pokedex_seen
