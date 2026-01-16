# ABOUTME: Tests battle sequencing for attack animations and HP ticks
# ABOUTME: Ensures attack order waits for HP bar animations to finish

from src.battle.move import Move
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


class StubMoveLoader:
    def __init__(self, move: Move):
        self._move = move

    def get_move(self, _move_id: str) -> Move:
        return self._move


class StubInput:
    def __init__(self, pressed: bool):
        self._pressed = pressed

    def is_just_pressed(self, key: str) -> bool:
        return key == "a" and self._pressed


def test_enemy_attack_waits_for_player_hp_tick():
    game = DummyGame()
    player = make_pokemon("Player", moves=["mega-punch"])
    enemy = make_pokemon("Enemy")
    enemy.moves = ["enemy_move"]

    battle = BattleState(game, player, enemy)
    battle.damage_calculator = StubDamageCalculator(damage=5, hit_count=1)
    enemy_move = make_move("enemy_move", 40)
    battle.move_loader = StubMoveLoader(enemy_move)
    battle.attack_animation_duration = 0.0

    player_move = make_move("mega-punch", 80, priority=1)
    battle._execute_player_attack(player_move)

    assert battle.phase == "showing_message"
    assert "used" in battle.message

    battle.handle_input(StubInput(True))
    assert battle.phase == "attack_animation"
    assert enemy.current_hp == enemy.stats.hp

    battle.update(0.0)
    assert battle.phase == "hp_tick"
    assert enemy.current_hp == enemy.stats.hp - 5

    assert "Wild" not in battle.message

    while battle.enemy_hp_display.is_animating(enemy.current_hp):
        battle.update(1.0)

    assert battle.phase == "showing_message"
    assert "Wild" in battle.message


def test_multi_hit_ticks_each_hit():
    game = DummyGame()
    player = make_pokemon("Player", moves=["double-kick"])
    enemy = make_pokemon("Enemy")
    enemy.moves = ["enemy_move"]

    battle = BattleState(game, player, enemy)
    battle.damage_calculator = StubDamageCalculator(damage=5, hit_count=2)
    enemy_move = make_move("enemy_move", 40)
    battle.move_loader = StubMoveLoader(enemy_move)
    battle.attack_animation_duration = 0.0

    player_move = make_move("double-kick", 30, priority=1)
    battle._execute_player_attack(player_move)

    battle.handle_input(StubInput(True))
    battle.update(0.0)
    assert enemy.current_hp == enemy.stats.hp - 5

    while battle.enemy_hp_display.is_animating(enemy.current_hp):
        battle.update(1.0)

    assert enemy.current_hp == enemy.stats.hp - 10

    message_guard = 0
    while "Hit 2 times!" not in battle.message and message_guard < 50:
        if battle.phase == "showing_message":
            battle.handle_input(StubInput(True))
        else:
            battle.update(1.0)
        message_guard += 1

    assert "Hit 2 times!" in battle.message
    assert enemy.current_hp == enemy.stats.hp - 10
