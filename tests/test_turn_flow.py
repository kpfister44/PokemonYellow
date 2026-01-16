# ABOUTME: Tests battle flow transitions after message handling
# ABOUTME: Verifies battle state returns to menu after messages

from src.states.battle_state import BattleState
from tests.battle_test_helpers import DummyGame, make_pokemon


def test_advance_turn_returns_to_battle_menu_after_messages():
    game = DummyGame()
    player = make_pokemon("Player")
    enemy = make_pokemon("Enemy")
    battle = BattleState(game, player, enemy)

    battle.phase = "showing_message"
    battle.message = "Wild PIDGEY used\nTACKLE!"

    battle._advance_turn()

    assert battle.phase == "battle_menu"
    assert battle.battle_menu.is_active is True
    assert battle.awaiting_input is True
