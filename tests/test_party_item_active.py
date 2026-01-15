# ABOUTME: Tests party item flow for active battle Pokemon
# ABOUTME: Ensures bench-only animation when active Pokemon is selected

from src.party.party import Party
from src.battle.pokemon import Pokemon
from src.battle.species_loader import SpeciesLoader
from src.states.party_state import PartyState
from src.items.item_effects import ItemUseResult


class FakeInput:
    def __init__(self, pressed: set[str]):
        self.pressed = pressed

    def is_just_pressed(self, key: str) -> bool:
        return key in self.pressed


class FakeGame:
    def __init__(self):
        self.state_stack = []
        self.pop_count = 0

    def push_state(self, state):
        self.state_stack.append(state)

    def pop_state(self):
        self.pop_count += 1
        if self.state_stack:
            self.state_stack.pop()


def build_pokemon(species_id: str, level: int = 5) -> Pokemon:
    species = SpeciesLoader().get_species(species_id)
    return Pokemon(species, level)


def test_item_use_on_active_pokemon_skips_party_animation():
    party = Party()
    active = build_pokemon("pikachu")
    bench = build_pokemon("rattata")
    party.add(active)
    party.add(bench)

    game = FakeGame()

    def item_use(_pokemon):
        return ItemUseResult(True, True, [])

    state = PartyState(
        game,
        party,
        mode="item",
        item_use=item_use,
        on_item_used=lambda _result: False,
        active_pokemon=active
    )
    game.state_stack.append(state)

    input_handler = FakeInput({"a"})
    state.handle_input(input_handler)

    assert state.animating_item is False
    assert game.pop_count == 1
