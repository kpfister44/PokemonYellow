import random

from src.battle.pokemon import Pokemon
from src.battle.species import BaseStats, Species
from src.overworld.npc import NPC
from src.states.battle_state import BattleState
from src.states.overworld_state import OverworldState


class DummyGame:
    def __init__(self):
        self.renderer = None
        self.pushed_state = None

    def push_state(self, state):
        self.pushed_state = state


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


def test_trainer_builds_party_from_team():
    from src.battle.trainer import Trainer

    trainer = Trainer(
        name="Timmy",
        trainer_class="Youngster",
        team=[
            {"species_id": "rattata", "level": 3},
            {"species_id": "rattata", "level": 4},
        ],
        prize_money=60,
    )

    class StubSpeciesLoader:
        def get_species(self, _species_id):
            return make_species("Rattata")

    party = trainer.get_party(StubSpeciesLoader())

    assert len(party) == 2
    assert party[0].level == 3
    assert party[1].level == 4


def test_npc_trainer_fields_initialized():
    npc = NPC(
        "trainer_1",
        1,
        2,
        direction="down",
        dialog_text="Let's battle!",
        is_trainer=True,
        trainer_data={"name": "Timmy"},
    )

    assert npc.is_trainer is True
    assert npc.trainer_data == {"name": "Timmy"}
    assert npc.defeated is False


def test_battle_state_trainer_cannot_run():
    game = DummyGame()
    player = make_pokemon("Player")
    enemy = make_pokemon("Enemy")

    class StubTrainer:
        name = "Timmy"
        trainer_class = "Youngster"

    battle = BattleState(
        game,
        player,
        enemy,
        is_trainer_battle=True,
        trainer=StubTrainer(),
        trainer_pokemon_remaining=[],
    )

    battle._handle_battle_menu_selection("RUN")

    assert "Can't run" in battle.message
    assert battle.phase == "battle_menu"
    assert battle.awaiting_input is True


def test_trainer_victory_sends_next_pokemon():
    game = DummyGame()
    player = make_pokemon("Player")
    enemy = make_pokemon("Enemy")
    next_mon = make_pokemon("NextMon")

    class StubTrainer:
        name = "Timmy"
        trainer_class = "Youngster"

    battle = BattleState(
        game,
        player,
        enemy,
        is_trainer_battle=True,
        trainer=StubTrainer(),
        trainer_pokemon_remaining=[next_mon],
    )

    battle._handle_victory()

    assert battle.enemy_pokemon == next_mon
    assert battle.phase == "battle_menu"


def test_overworld_starts_trainer_battle(monkeypatch):
    game = DummyGame()
    state = OverworldState(game, "data/maps/route_1.json")

    npc = NPC(
        "trainer_1",
        1,
        2,
        direction="down",
        dialog_text="Let's battle!",
        is_trainer=True,
        trainer_data={
            "name": "Timmy",
            "class": "Youngster",
            "team": [{"species_id": "rattata", "level": 3}],
            "prize_money": 60,
        },
    )

    class StubSpeciesLoader:
        def get_species(self, _species_id):
            return make_species("Rattata")

    class StubBattleState:
        def __init__(self, *args, **kwargs):
            pass

    monkeypatch.setattr("src.states.overworld_state.SpeciesLoader", StubSpeciesLoader)
    monkeypatch.setattr("src.states.overworld_state.BattleState", StubBattleState)

    state._start_trainer_battle(npc)

    assert npc.defeated is True
    assert game.pushed_state is not None
