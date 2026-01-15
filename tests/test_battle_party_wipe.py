# ABOUTME: Tests for battle state party wipe and forced switch handling
# ABOUTME: Ensures fainted player Pokemon triggers forced switch or blackout

import random

from src.battle.pokemon import Pokemon
from src.battle.species import BaseStats, Species
from src.party.party import Party
from src.states.battle_state import BattleState
from src.states.party_state import PartyState


class DummyGame:
    def __init__(self):
        self.renderer = None
        self.state_stack = []

    def push_state(self, state):
        self.state_stack.append(state)

    def pop_state(self):
        if self.state_stack:
            self.state_stack.pop()


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


def make_pokemon(name: str, level: int = 5) -> Pokemon:
    random.seed(0)
    return Pokemon(make_species(name), level)


def test_player_faint_triggers_forced_switch_when_party_alive():
    game = DummyGame()
    player = make_pokemon("Player")
    enemy = make_pokemon("Enemy")
    party = Party()
    backup = make_pokemon("Backup")

    player.current_hp = 0
    party.add(player)
    party.add(backup)

    battle = BattleState(game, player, enemy)
    battle.party = party

    battle._advance_turn()

    assert battle.message == "PLAYER\nfainted!"
    assert battle.message_queue == ["Choose next POK\u00e9MON!"]
    assert isinstance(game.state_stack[-1], PartyState)
    assert game.state_stack[-1].mode == "forced_switch"


def test_player_faint_triggers_blackout_when_party_wiped():
    game = DummyGame()
    player = make_pokemon("Player")
    enemy = make_pokemon("Enemy")
    party = Party()

    player.current_hp = 0
    party.add(player)

    battle = BattleState(game, player, enemy)
    battle.party = party

    battle._advance_turn()

    assert battle.message == "PLAYER\nfainted!"
    assert battle.message_queue == ["You have no more\nPOK\u00e9MON!", "You blacked out!"]
    assert battle.phase == "end"
