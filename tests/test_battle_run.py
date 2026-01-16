# ABOUTME: Tests battle escape calculations for Gen 1 run mechanics
# ABOUTME: Verifies speed checks, attempt odds, and random threshold behavior

# ABOUTME: Tests Gen 1 run mechanics logic
# ABOUTME: Verifies escape odds based on speed and attempts

import random

from src.states.battle_state import BattleState
from tests.battle_test_helpers import DummyGame, make_pokemon


def test_escape_succeeds_when_speed_at_least_enemy():
    game = DummyGame()
    player = make_pokemon("Player", moves=["tackle"])
    enemy = make_pokemon("Enemy", moves=["tackle"])
    player.stats.speed = 20
    enemy.stats.speed = 10

    battle = BattleState(game, player, enemy)

    assert battle._attempt_escape() is True
    assert battle.escape_attempts == 1


def test_escape_uses_attempt_odds(monkeypatch):
    game = DummyGame()
    player = make_pokemon("Player", moves=["tackle"])
    enemy = make_pokemon("Enemy", moves=["tackle"])
    player.stats.speed = 10
    enemy.stats.speed = 40

    battle = BattleState(game, player, enemy)

    monkeypatch.setattr(random, "randint", lambda _a, _b: 255)
    assert battle._attempt_escape() is False
    assert battle.escape_attempts == 1

    monkeypatch.setattr(random, "randint", lambda _a, _b: 0)
    assert battle._attempt_escape() is True
    assert battle.escape_attempts == 2
