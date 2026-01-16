# ABOUTME: Tests battle party cancel behavior
# ABOUTME: Ensures canceling party screen returns to battle menu

from src.party.party import Party
from src.states.battle_state import BattleState
from tests.battle_test_helpers import make_pokemon


class StackGame:
    def __init__(self):
        self.renderer = None
        self.state_stack = []

    def push_state(self, state):
        self.state_stack.append(state)

    def pop_state(self):
        if self.state_stack:
            self.state_stack.pop()


class StubInput:
    def __init__(self, key: str):
        self._key = key

    def is_just_pressed(self, key: str) -> bool:
        return self._key == key


def test_battle_party_cancel_returns_to_menu():
    game = StackGame()
    player = make_pokemon("Player", moves=["tackle"])
    enemy = make_pokemon("Enemy", moves=["tackle"])
    battle = BattleState(game, player, enemy)
    battle.party = Party()
    battle.party.add(player)
    battle.phase = "battle_menu"
    battle.battle_menu.activate()
    game.push_state(battle)

    battle._handle_battle_menu_selection("PKM")

    party_state = game.state_stack[-1]
    party_state.handle_input(StubInput("b"))

    assert game.state_stack[-1] is battle
    assert battle.phase == "battle_menu"
    assert battle.battle_menu.is_active is True
