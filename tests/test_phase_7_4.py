# ABOUTME: Tests battle damage mechanics and multi-hit behavior
# ABOUTME: Verifies Gen 1 hit count and drain/heal logic

import random

import pytest

from src.battle.damage_calculator import DamageCalculator
from src.battle.move import MoveMeta
from src.battle.species import LevelUpMove
from src.states.battle_state import BattleState
from tests.battle_test_helpers import DummyGame, make_move, make_pokemon


class StubDamageCalculator:
    def __init__(self, damage: int, hit_count: int = 1):
        self._damage = damage
        self._hit_count = hit_count

    def check_accuracy(self, attacker, defender, move):
        return True

    def check_critical_hit(self, attacker, move):
        return False

    def calculate_damage(self, attacker, defender, move, is_critical=False):
        return self._damage

    def get_hit_count(self, move):
        return self._hit_count


def test_get_hit_count_fixed_two(monkeypatch):
    calc = DamageCalculator()
    move = make_move("double-kick", 30, MoveMeta(min_hits=2, max_hits=2))
    assert calc.get_hit_count(move) == 2


def test_get_hit_count_distribution(monkeypatch):
    calc = DamageCalculator()
    move = make_move("double-slap", 15, MoveMeta(min_hits=2, max_hits=5))

    monkeypatch.setattr(random, "randint", lambda _a, _b: 0)
    assert calc.get_hit_count(move) == 2

    monkeypatch.setattr(random, "randint", lambda _a, _b: 3)
    assert calc.get_hit_count(move) == 3

    monkeypatch.setattr(random, "randint", lambda _a, _b: 6)
    assert calc.get_hit_count(move) == 4

    monkeypatch.setattr(random, "randint", lambda _a, _b: 7)
    assert calc.get_hit_count(move) == 5


def test_multi_hit_applies_damage_each_hit():
    game = DummyGame()
    attacker = make_pokemon("Attacker")
    defender = make_pokemon("Defender")

    battle = BattleState(game, attacker, defender)
    battle.damage_calculator = StubDamageCalculator(damage=5, hit_count=2)

    move = make_move("double-kick", 30, MoveMeta(min_hits=2, max_hits=2))
    starting_hp = defender.current_hp

    battle._execute_attack(attacker, defender, move, is_player=True)

    assert defender.current_hp == starting_hp - 10
    assert "Hit 2 times!" in battle.message_queue


def test_drain_heals_attacker_based_on_damage():
    game = DummyGame()
    attacker = make_pokemon("Attacker")
    defender = make_pokemon("Defender")

    battle = BattleState(game, attacker, defender)
    battle.damage_calculator = StubDamageCalculator(damage=20, hit_count=1)

    attacker.current_hp = max(1, attacker.stats.hp - 15)
    move = make_move("absorb", 20, MoveMeta(drain=50))

    battle._execute_attack(attacker, defender, move, is_player=True)

    assert attacker.current_hp == min(attacker.stats.hp, attacker.stats.hp - 15 + 10)


def test_healing_move_restores_percent_of_max_hp():
    game = DummyGame()
    attacker = make_pokemon("Attacker")
    defender = make_pokemon("Defender")

    battle = BattleState(game, attacker, defender)
    battle.damage_calculator = StubDamageCalculator(damage=0, hit_count=1)

    attacker.current_hp = attacker.stats.hp // 2
    move = make_move("recover", None, MoveMeta(healing=50))

    battle._execute_attack(attacker, defender, move, is_player=True)

    assert attacker.current_hp == min(attacker.stats.hp, (attacker.stats.hp // 2) + (attacker.stats.hp // 2))


def test_flinch_blocks_defender_move_when_attacker_goes_first(monkeypatch):
    game = DummyGame()
    player = make_pokemon("Player")
    enemy = make_pokemon("Enemy")
    enemy.moves = ["enemy_move"]

    battle = BattleState(game, player, enemy)
    battle.damage_calculator = StubDamageCalculator(damage=10, hit_count=1)

    enemy_move = make_move("enemy_move", 30)

    class StubMoveLoader:
        def get_move(self, _move_id):
            return enemy_move

    battle.move_loader = StubMoveLoader()

    monkeypatch.setattr(random, "randint", lambda _a, _b: 1)
    player_move = make_move("flinch_move", 30, MoveMeta(flinch_chance=100), priority=1)

    player_start_hp = player.current_hp

    battle._execute_player_attack(player_move)

    assert player.current_hp == player_start_hp
