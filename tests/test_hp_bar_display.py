# ABOUTME: Tests HP bar display ticking logic for battle animations
# ABOUTME: Verifies bar unit conversion and tick timing rules

import math

from src.battle.hp_bar_display import HpBarDisplay


def test_hp_bar_display_converts_hp_to_units():
    display = HpBarDisplay(max_hp=19, current_hp=19, bar_width=48)

    assert display.hp_to_units(19) == 48
    assert display.hp_to_units(1) == math.floor(1 / 19 * 48)
    assert display.hp_to_units(0) == 0
    assert display.hp_to_units(10) == math.floor(10 / 19 * 48)


def test_hp_bar_display_ticks_faster_on_damage():
    display = HpBarDisplay(
        max_hp=100,
        current_hp=100,
        bar_width=48,
        damage_tick_seconds=0.02,
        heal_tick_seconds=0.05
    )

    changed = display.update(actual_hp=50, dt=0.02)
    assert changed is True
    assert display.display_units == 47

    display = HpBarDisplay(
        max_hp=100,
        current_hp=50,
        bar_width=48,
        damage_tick_seconds=0.02,
        heal_tick_seconds=0.05
    )

    changed = display.update(actual_hp=100, dt=0.02)
    assert changed is False
    assert display.display_units == display.hp_to_units(50)

    changed = display.update(actual_hp=100, dt=0.05)
    assert changed is True
    assert display.display_units == display.hp_to_units(50) + 1
