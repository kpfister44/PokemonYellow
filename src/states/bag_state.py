# ABOUTME: Bag state for using items in overworld or battle
# ABOUTME: Handles item selection, usage, and target selection

from typing import Callable, Optional
from src.states.base_state import BaseState
from src.ui.bag_screen import BagScreen
from src.items.item_loader import ItemLoader
from src.items.item_effects import ItemEffects, ItemUseContext, ItemUseResult
from src.items.bag import Bag
from src.party.party import Party
from src.battle.pokemon import Pokemon


class BagState(BaseState):
    """State for item bag usage."""

    def __init__(
        self,
        game,
        bag: Bag,
        party: Party,
        mode: str,
        active_pokemon: Optional[Pokemon] = None,
        is_trainer_battle: bool = False,
        on_item_used: Optional[Callable[[ItemUseResult], None]] = None
    ):
        super().__init__(game)
        self.bag = bag
        self.party = party
        self.mode = mode
        self.active_pokemon = active_pokemon
        self.is_trainer_battle = is_trainer_battle
        self.on_item_used = on_item_used

        self.item_loader = ItemLoader()
        self.item_effects = ItemEffects(self.item_loader)

        entry_filter = None
        if self.mode == "battle":
            entry_filter = lambda item: item.usable_in_battle

        self.screen = BagScreen(self.bag, self.item_loader, entry_filter=entry_filter)

    def handle_input(self, input_handler):
        if input_handler.is_just_pressed("down"):
            self.screen.move_cursor(1)
        elif input_handler.is_just_pressed("up"):
            self.screen.move_cursor(-1)
        elif input_handler.is_just_pressed("a"):
            self._handle_item_selection()
        elif input_handler.is_just_pressed("b"):
            self.game.pop_state()

    def _handle_item_selection(self) -> None:
        entry = self.screen.get_selected_entry()
        if not entry:
            return

        item_id = entry.item_id
        if self.item_effects.requires_target(item_id):
            from src.states.party_state import PartyState
            party_state = PartyState(
                self.game,
                self.party,
                mode="item",
                item_use=lambda pokemon: self._apply_item(item_id, pokemon),
                on_item_used=lambda result: self._handle_item_result(item_id, result),
                on_cancel=self._handle_target_cancelled,
                active_pokemon=self.active_pokemon if self.mode == "battle" else None
            )
            self.game.push_state(party_state)
            return

        result = self._apply_item(item_id, None)
        self._handle_item_result(item_id, result)

    def _handle_target_cancelled(self) -> None:
        pass

    def _apply_item(self, item_id: str, target: Optional[Pokemon]) -> ItemUseResult:
        context = ItemUseContext(
            mode=self.mode,
            is_trainer_battle=self.is_trainer_battle,
            active_pokemon=self.active_pokemon
        )
        return self.item_effects.use_item(item_id, target, context)

    def _handle_item_result(self, item_id: str, result: ItemUseResult) -> bool:
        if result.success and result.consumed:
            self.bag.remove_item(item_id)

        if result.messages:
            self.screen.set_message(result.messages[0])

        if self.mode == "battle" and result.success:
            if self.on_item_used:
                self.on_item_used(result)
            if self.game.state_stack and self.game.state_stack[-1] is self:
                self.game.pop_state()
            return True

        return False

    def update(self, dt: float):
        pass

    def render(self, renderer) -> None:
        self.screen.render(renderer)
