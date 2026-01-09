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


def make_species(name: str) -> Species:
    return Species(
        species_id=name.lower(),
        number=999,
        name=name,
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
