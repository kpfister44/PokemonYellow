# ABOUTME: Shared helpers for battle state tests
# ABOUTME: Provides dummy game, species, pokemon, and move builders

import random

from src.battle.move import Move, MoveMeta
from src.battle.pokemon import Pokemon
from src.battle.species import BaseStats, Species


class DummyGame:
    def __init__(self):
        self.renderer = None
        self.popped = False

    def pop_state(self):
        self.popped = True


def make_species(name: str) -> Species:
    return Species(
        species_id=name.lower(),
        number=999,
        name=name,
        genus="",
        height=0,
        weight=0,
        types=["normal"],
        base_stats=BaseStats(hp=50, attack=50, defense=50, special=50, speed=50),
        base_experience=100,
        growth_rate="medium",
        capture_rate=255,
        base_happiness=70,
        gender_rate=-1,
        pokedex_entry="",
        evolution_chain={},
        level_up_moves=[],
        sprites=None,
    )


def make_pokemon(name: str, level: int = 5, moves: list[str] | None = None) -> Pokemon:
    random.seed(0)
    pokemon = Pokemon(make_species(name), level)
    if moves:
        pokemon.moves = moves
        pokemon.move_pp = {move_id: (10, 10) for move_id in moves}
    return pokemon


def make_move(move_id: str, power: int | None, meta: MoveMeta | None = None, priority: int = 0) -> Move:
    return Move(
        move_id=move_id,
        id_number=1,
        name=move_id,
        type="normal",
        power=power,
        accuracy=100,
        pp=35,
        category="physical",
        priority=priority,
        effect_chance=None,
        description="",
        meta=meta,
        stat_changes=[],
    )
