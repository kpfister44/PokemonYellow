# ABOUTME: Tests experience gain, level-up, and move learning logic
# ABOUTME: Covers Gen 1 move learning rules and EXP split behavior

import random

from src.battle.experience_calculator import ExperienceCalculator
from src.battle.pokemon import Pokemon
from src.battle.species import BaseStats, LevelUpMove, Species
from src.states.battle_state import BattleState


class DummyGame:
    def __init__(self):
        self.renderer = None
        self.popped = False

    def pop_state(self):
        self.popped = True


def make_species(name: str, learnset: list[LevelUpMove]) -> Species:
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
        level_up_moves=learnset,
        sprites=None,
    )


def make_pokemon(name: str, level: int, learnset: list[LevelUpMove]) -> Pokemon:
    random.seed(0)
    return Pokemon(make_species(name, learnset), level)


def test_initial_moves_use_last_four_from_learnset():
    learnset = [
        LevelUpMove(level=1, move="tackle"),
        LevelUpMove(level=2, move="growl"),
        LevelUpMove(level=3, move="tail-whip"),
        LevelUpMove(level=4, move="quick-attack"),
        LevelUpMove(level=5, move="thunder-shock"),
    ]
    pokemon = make_pokemon("Pika", 5, learnset)

    assert pokemon.moves == ["growl", "tail-whip", "quick-attack", "thunder-shock"]


def test_learn_move_with_open_slot_adds_move_and_pp():
    learnset = [
        LevelUpMove(level=1, move="tackle"),
        LevelUpMove(level=2, move="growl"),
        LevelUpMove(level=3, move="tail-whip"),
    ]
    pokemon = make_pokemon("Pika", 3, learnset)

    status = pokemon.try_learn_move("quick-attack")

    assert status == "learned"
    assert "quick-attack" in pokemon.moves
    current_pp, max_pp = pokemon.get_move_pp("quick-attack")
    assert current_pp == max_pp
    assert max_pp > 0


def test_learn_move_requires_replacement_when_full():
    learnset = [
        LevelUpMove(level=1, move="tackle"),
        LevelUpMove(level=2, move="growl"),
        LevelUpMove(level=3, move="tail-whip"),
        LevelUpMove(level=4, move="quick-attack"),
    ]
    pokemon = make_pokemon("Pika", 4, learnset)

    status = pokemon.try_learn_move("thunder-shock")

    assert status == "needs_replacement"
    assert "thunder-shock" not in pokemon.moves

    replaced = pokemon.replace_move("growl", "thunder-shock")

    assert replaced is True
    assert pokemon.moves == ["tackle", "thunder-shock", "tail-whip", "quick-attack"]


def test_skip_move_learning_does_not_change_moves():
    learnset = [
        LevelUpMove(level=1, move="tackle"),
        LevelUpMove(level=2, move="growl"),
        LevelUpMove(level=3, move="tail-whip"),
        LevelUpMove(level=4, move="quick-attack"),
    ]
    pokemon = make_pokemon("Pika", 4, learnset)

    status = pokemon.try_learn_move("thunder-shock")

    assert status == "needs_replacement"
    assert pokemon.moves == ["tackle", "growl", "tail-whip", "quick-attack"]


def test_learn_move_already_known_returns_status():
    learnset = [
        LevelUpMove(level=1, move="tackle"),
        LevelUpMove(level=2, move="growl"),
    ]
    pokemon = make_pokemon("Pika", 2, learnset)

    status = pokemon.try_learn_move("tackle")

    assert status == "already_known"


def test_experience_gain_supports_multiple_level_ups():
    learnset = [LevelUpMove(level=1, move="tackle")]
    pokemon = make_pokemon("Pika", 3, learnset)
    calc = ExperienceCalculator()

    exp_for_level_5 = calc.get_exp_for_level(pokemon.species.growth_rate, 5)
    levels = pokemon.gain_experience(exp_for_level_5 - pokemon.experience)

    assert levels == [4, 5]
    assert pokemon.level == 5


def test_exp_split_excludes_fainted_participants():
    learnset = [LevelUpMove(level=1, move="tackle")]
    game = DummyGame()
    player = make_pokemon("Player", 5, learnset)
    ally = make_pokemon("Ally", 5, learnset)
    enemy = make_pokemon("Enemy", 5, learnset)

    battle = BattleState(game, player, enemy)
    battle.participants = [player, ally]
    ally.take_damage(ally.current_hp)

    eligible = battle._eligible_exp_participants()

    assert eligible == [player]
