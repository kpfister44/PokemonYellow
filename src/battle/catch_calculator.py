# ABOUTME: Pokemon catching calculation for wild battles
# ABOUTME: Implements Gen 1 catch rate formula with status modifiers

import random

from src.battle.pokemon import Pokemon
from src.battle.status_effects import StatusCondition


class CatchCalculator:
    """Gen 1 catch rate formula."""

    def calculate_catch_chance(self, pokemon: Pokemon, ball_bonus: int = 1) -> tuple[bool, int]:
        """
        Calculate catch success using Gen 1 formula.

        Args:
            pokemon: Wild Pokemon to catch
            ball_bonus: Pokeball type modifier (1 = regular, 1.5 = Great, 2 = Ultra)

        Returns:
            Tuple of (caught: bool, shakes: int)
        """
        catch_rate = pokemon.species.capture_rate

        hp_factor = (pokemon.stats.hp * 255 * 4) // (pokemon.current_hp * 12)

        status_bonus = 0
        if pokemon.status in [StatusCondition.SLEEP, StatusCondition.FREEZE]:
            status_bonus = 25
        elif pokemon.status in [StatusCondition.PARALYSIS, StatusCondition.BURN, StatusCondition.POISON]:
            status_bonus = 12

        a = min(int((catch_rate + status_bonus) * hp_factor * ball_bonus / 255), 255)

        shakes = 0
        for _ in range(4):
            if random.randint(0, 255) >= a:
                return (False, shakes)
            shakes += 1

        return (True, 4)
