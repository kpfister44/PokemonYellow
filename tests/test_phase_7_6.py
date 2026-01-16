# ABOUTME: Tests Gen 1 catch logic and battle catch flow sequencing
# ABOUTME: Verifies catch success/failure messaging and phase transitions

import random

from src.battle.pokemon import Pokemon
from src.battle.species import BaseStats, Species
from src.states.battle_state import BattleState


class DummyGame:
    def __init__(self):
        self.renderer = None
        self.popped = False

    def pop_state(self):
        self.popped = True


def make_species(name: str, capture_rate: int = 200) -> Species:
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
        capture_rate=capture_rate,
        base_happiness=70,
        gender_rate=-1,
        pokedex_entry="",
        evolution_chain={},
        level_up_moves=[],
        sprites=None,
    )


def make_pokemon(name: str, level: int = 5, capture_rate: int = 200) -> Pokemon:
    random.seed(0)
    return Pokemon(make_species(name, capture_rate=capture_rate), level)


def test_catch_calculator_success_and_failure(monkeypatch):
    from src.battle.catch_calculator import CatchCalculator
    from src.battle.status_effects import StatusCondition

    pokemon = make_pokemon("Target")
    pokemon.current_hp = max(1, pokemon.stats.hp // 2)
    pokemon.status = StatusCondition.SLEEP

    calc = CatchCalculator()

    monkeypatch.setattr(random, "randint", lambda _a, _b: 0)
    caught, shakes = calc.calculate_catch_chance(pokemon)
    assert caught is True
    assert shakes == 4

    monkeypatch.setattr(random, "randint", lambda _a, _b: 255)
    caught, shakes = calc.calculate_catch_chance(pokemon)
    assert caught is False
    assert shakes == 0


def test_battle_state_attempt_catch_success(monkeypatch):
    game = DummyGame()
    player = make_pokemon("Player")
    enemy = make_pokemon("Enemy")

    battle = BattleState(game, player, enemy)

    class StubCatchCalculator:
        def calculate_catch_chance(self, _pokemon, ball_bonus=1):
            return (True, 2)

    monkeypatch.setattr("src.states.battle_state.CatchCalculator", StubCatchCalculator)

    battle._attempt_catch_with_ball(
        "POKE BALL",
        1,
        False,
        "poke-ball",
        "assets/sprites/items/poke-ball.png"
    )

    assert battle.phase == "showing_message"
    assert "Used POKE BALL!" in battle.message


def test_battle_state_attempt_catch_failure(monkeypatch):
    game = DummyGame()
    player = make_pokemon("Player")
    enemy = make_pokemon("Enemy")

    battle = BattleState(game, player, enemy)

    class StubCatchCalculator:
        def calculate_catch_chance(self, _pokemon, ball_bonus=1):
            return (False, 1)

    monkeypatch.setattr("src.states.battle_state.CatchCalculator", StubCatchCalculator)

    battle._attempt_catch_with_ball(
        "POKE BALL",
        1,
        False,
        "poke-ball",
        "assets/sprites/items/poke-ball.png"
    )

    assert battle.phase == "showing_message"
    assert "Used POKE BALL!" in battle.message
