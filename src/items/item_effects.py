# ABOUTME: Applies supported item effects in overworld and battle
# ABOUTME: Encapsulates Gen 1 item usage rules and results

from dataclasses import dataclass
from typing import Optional

from src.battle.pokemon import Pokemon
from src.battle.status_effects import StatusCondition
from src.items.item_loader import ItemLoader


@dataclass
class ItemUseContext:
    """Context for item usage."""
    mode: str  # "overworld" or "battle"
    is_trainer_battle: bool = False
    active_pokemon: Optional[Pokemon] = None


@dataclass
class ItemUseResult:
    """Result of applying an item effect."""
    success: bool
    consumed: bool
    messages: list[str]
    action: Optional[dict] = None


class ItemEffects:
    """Applies supported item effects."""

    def __init__(self, item_loader: Optional[ItemLoader] = None):
        self.item_loader = item_loader or ItemLoader()

    def use_item(self, item_id: str, target: Optional[Pokemon], context: ItemUseContext) -> ItemUseResult:
        item = self.item_loader.get_item(item_id)

        if context.mode == "battle" and not item.usable_in_battle:
            return ItemUseResult(False, False, ["Can't use that here."])

        if context.mode == "overworld" and not item.usable_in_overworld:
            return ItemUseResult(False, False, ["Can't use that here."])

        if item_id in BALL_BONUSES:
            return self._use_ball(item, context)

        if item_id in HP_HEAL_ITEMS:
            return self._use_hp_item(item, target)

        if item_id == FULL_RESTORE_ITEM:
            return self._use_full_restore(item, target)

        if item_id in STATUS_CURE_ITEMS:
            return self._use_status_cure(item, target)

        if item_id in REVIVE_ITEMS:
            return self._use_revive(item, target)

        if item_id in STAT_STAGE_ITEMS:
            return self._use_stat_stage_item(item, context, target)

        return ItemUseResult(False, False, ["Can't use that here."])

    def requires_target(self, item_id: str) -> bool:
        """Check if the item requires a Pokemon target."""
        return (
            item_id in HP_HEAL_ITEMS
            or item_id in STATUS_CURE_ITEMS
            or item_id in REVIVE_ITEMS
            or item_id == FULL_RESTORE_ITEM
        )

    def _use_hp_item(self, item, target: Optional[Pokemon]) -> ItemUseResult:
        if not target or target.is_fainted():
            return ItemUseResult(False, False, ["It won't have any effect."])

        amount = HP_HEAL_ITEMS[item.item_id]
        if amount == "full":
            healed = target.restore_full_hp()
        else:
            healed = target.heal(amount)

        if healed == 0:
            return ItemUseResult(False, False, ["It won't have any effect."])

        return ItemUseResult(True, item.consumable, ["HP was restored."])

    def _use_full_restore(self, item, target: Optional[Pokemon]) -> ItemUseResult:
        if not target or target.is_fainted():
            return ItemUseResult(False, False, ["It won't have any effect."])

        healed = target.restore_full_hp()
        cured = target.clear_status()

        if healed == 0 and not cured:
            return ItemUseResult(False, False, ["It won't have any effect."])

        return ItemUseResult(True, item.consumable, ["HP was restored."])

    def _use_status_cure(self, item, target: Optional[Pokemon]) -> ItemUseResult:
        if not target or target.is_fainted():
            return ItemUseResult(False, False, ["It won't have any effect."])

        cures = STATUS_CURE_ITEMS[item.item_id]
        if target.status not in cures:
            return ItemUseResult(False, False, ["It won't have any effect."])

        target.clear_status()
        return ItemUseResult(True, item.consumable, ["Status healed."])

    def _use_revive(self, item, target: Optional[Pokemon]) -> ItemUseResult:
        if not target or not target.is_fainted():
            return ItemUseResult(False, False, ["It won't have any effect."])

        restore = REVIVE_ITEMS[item.item_id]
        if restore == "full":
            target.current_hp = target.stats.hp
        else:
            target.current_hp = max(1, target.stats.hp // 2)

        return ItemUseResult(True, item.consumable, ["HP was restored."])

    def _use_stat_stage_item(self, item, context: ItemUseContext, target: Optional[Pokemon]) -> ItemUseResult:
        pokemon = target or context.active_pokemon
        if not pokemon or pokemon.is_fainted():
            return ItemUseResult(False, False, ["It won't have any effect."])

        stat_name, change = STAT_STAGE_ITEMS[item.item_id]
        changed, message = pokemon.apply_stat_change(stat_name, change)
        if not changed:
            return ItemUseResult(False, False, [f"It {message}."])

        return ItemUseResult(True, item.consumable, [f"{pokemon.species.name.upper()}'s {stat_name.upper()} {message}!"])

    def _use_ball(self, item, context: ItemUseContext) -> ItemUseResult:
        if context.mode != "battle":
            return ItemUseResult(False, False, ["Can't use that here."])

        if context.is_trainer_battle:
            return ItemUseResult(False, False, ["Can't use that here."])

        bonus = BALL_BONUSES[item.item_id]
        action = {
            "type": "catch",
            "ball_bonus": bonus,
            "ball_name": item.name,
            "force_catch": item.item_id == "master-ball",
            "ball_item_id": item.item_id,
            "ball_sprite": item.sprite
        }
        return ItemUseResult(True, item.consumable, ["Used the ball!"], action=action)


HP_HEAL_ITEMS = {
    "potion": 20,
    "super-potion": 50,
    "hyper-potion": 200,
    "max-potion": "full",
    "fresh-water": 50,
    "soda-pop": 60,
    "lemonade": 80
}

FULL_RESTORE_ITEM = "full-restore"

STATUS_CURE_ITEMS = {
    "antidote": {StatusCondition.POISON, StatusCondition.BADLY_POISON},
    "burn-heal": {StatusCondition.BURN},
    "ice-heal": {StatusCondition.FREEZE},
    "awakening": {StatusCondition.SLEEP},
    "paralyze-heal": {StatusCondition.PARALYSIS},
    "full-heal": {
        StatusCondition.PARALYSIS,
        StatusCondition.BURN,
        StatusCondition.FREEZE,
        StatusCondition.POISON,
        StatusCondition.BADLY_POISON,
        StatusCondition.SLEEP
    }
}

REVIVE_ITEMS = {
    "revive": "half",
    "max-revive": "full"
}

STAT_STAGE_ITEMS = {
    "x-attack": ("attack", 1),
    "x-defense": ("defense", 1),
    "x-speed": ("speed", 1),
    "x-sp-atk": ("special", 1)
}

BALL_BONUSES = {
    "poke-ball": 1,
    "great-ball": 1.5,
    "ultra-ball": 2,
    "safari-ball": 1.5,
    "master-ball": 1
}
