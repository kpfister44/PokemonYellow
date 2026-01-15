# ABOUTME: Tracks animated HP bar display values for battle UI
# ABOUTME: Converts HP to bar units and ticks toward targets over time

from dataclasses import dataclass
import math


@dataclass
class HpBarDisplay:
    max_hp: int
    current_hp: int
    bar_width: int
    damage_tick_seconds: float = 0.02
    heal_tick_seconds: float = 0.04

    def __post_init__(self):
        self.display_units = self.hp_to_units(self.current_hp)
        self.display_hp = self.current_hp
        self._timer = 0.0

    def hp_to_units(self, hp: int) -> int:
        if hp <= 0:
            return 0
        if self.max_hp <= 0:
            return 0
        units = math.floor(hp / self.max_hp * self.bar_width)
        return max(1, min(self.bar_width, units))

    def update(self, actual_hp: int, dt: float) -> bool:
        target_hp = max(0, min(self.max_hp, actual_hp))
        target_units = self.hp_to_units(target_hp)

        if target_units == self.display_units:
            self.display_hp = target_hp
            self._timer = 0.0
            return False

        self._timer += dt
        is_healing = target_units > self.display_units
        tick_seconds = self.heal_tick_seconds if is_healing else self.damage_tick_seconds

        if self._timer < tick_seconds:
            return False

        self._timer -= tick_seconds
        step = 1 if is_healing else -1
        self.display_units = max(0, min(self.bar_width, self.display_units + step))

        if self.display_units == target_units:
            self.display_hp = target_hp
        else:
            self.display_hp = self._hp_from_units(self.display_units)

        return True

    def is_animating(self, actual_hp: int) -> bool:
        target_units = self.hp_to_units(actual_hp)
        return target_units != self.display_units

    def _hp_from_units(self, units: int) -> int:
        if units <= 0 or self.max_hp <= 0:
            return 0
        hp = math.floor(units / self.bar_width * self.max_hp)
        return max(1, min(self.max_hp, hp))
