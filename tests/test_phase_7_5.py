import random

import pytest

from src.battle.pokemon import Pokemon
from src.battle.species import BaseStats, LevelUpMove, Species
from src.states.battle_state import BattleState


class DummyGame:
    def __init__(self):
        self.renderer = None
        self.popped = False

    def pop_state(self):
        self.popped = True


def make_species(name: str, growth_rate: str = "medium") -> Species:
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
        growth_rate=growth_rate,
        capture_rate=255,
        base_happiness=70,
        gender_rate=-1,
        pokedex_entry="",
        evolution_chain={},
        level_up_moves=[],
        sprites=None,
    )


def make_pokemon(name: str, level: int = 5, growth_rate: str = "medium") -> Pokemon:
    random.seed(0)
    return Pokemon(make_species(name, growth_rate=growth_rate), level)


def test_experience_calculator_gain_and_level_curve():
    from src.battle.experience_calculator import ExperienceCalculator

    calc = ExperienceCalculator()
    defeated = make_pokemon("Defeated", level=5)

    assert calc.calculate_exp_gain(defeated, is_wild=True, participated=1) == int((100 * 5 / 7) * 1.0)
    assert calc.calculate_exp_gain(defeated, is_wild=False, participated=1) == int((100 * 5 / 7) * 1.5)
    assert calc.get_exp_for_level("fast", 10) == int((4 * 10 ** 3) / 5)
    assert calc.get_exp_for_level("medium", 10) == 10 ** 3
    assert calc.get_exp_for_level("medium-slow", 10) == int((6 * 10 ** 3 / 5) - (15 * 10 ** 2) + (100 * 10) - 140)
    assert calc.get_exp_for_level("slow", 10) == int((5 * 10 ** 3) / 4)


def test_pokemon_experience_and_level_up_flow():
    from src.battle.experience_calculator import ExperienceCalculator

    pokemon = make_pokemon("Pika", level=4)
    calc = ExperienceCalculator()

    current_exp = calc.get_exp_for_level(pokemon.species.growth_rate, pokemon.level)
    next_exp = calc.get_exp_for_level(pokemon.species.growth_rate, pokemon.level + 1)

    assert pokemon.experience == current_exp
    assert pokemon.exp_to_next_level == next_exp

    assert pokemon.gain_experience(next_exp - current_exp - 1) == []
    assert pokemon.gain_experience(1) == [5]

    old_stats = pokemon.stats
    old_hp = pokemon.current_hp
    old_max = old_stats.hp

    assert pokemon.level == 5
    assert pokemon.stats.hp >= old_stats.hp
    assert pokemon.current_hp == old_hp + (pokemon.stats.hp - old_max)


def test_battle_state_victory_and_level_up_sequence():
    from src.battle.experience_calculator import ExperienceCalculator

    game = DummyGame()
    player = make_pokemon("Player", level=4)
    enemy = make_pokemon("Enemy", level=4)

    battle = BattleState(game, player, enemy)

    calc = ExperienceCalculator()
    current_exp = calc.get_exp_for_level(player.species.growth_rate, player.level)
    next_exp = calc.get_exp_for_level(player.species.growth_rate, player.level + 1)
    player.experience = next_exp - 1

    battle._handle_victory()

    assert battle.exp_flow_active is True
    assert battle.phase == "showing_message"
    assert "gained" in battle.message

    battle._show_next_message()
    battle._show_next_message()

    assert player.level == 5
