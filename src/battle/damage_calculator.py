# ABOUTME: Gen 1 damage calculation engine
# ABOUTME: Implements authentic Gen 1 damage formula with type effectiveness

from src.battle.pokemon import Pokemon
from src.battle.move import Move
from src.battle.type_chart import get_dual_type_effectiveness
import random


class DamageCalculator:
    """Calculate damage using Gen 1 formula."""

    def calculate_damage(self, attacker: Pokemon, defender: Pokemon, move: Move) -> int:
        """
        Calculate damage using Gen 1 formula.

        Gen 1 Formula:
        Damage = ((((2 * Level / 5) + 2) * Power * A/D) / 50 + 2) * Modifier

        Where Modifier includes:
        - STAB (Same Type Attack Bonus): 1.5x if move type matches attacker type
        - Type effectiveness: 0x, 0.5x, 1x, or 2x (can stack for dual types)
        - Random factor: 217-255 / 255 (0.85 to 1.0)

        Args:
            attacker: Attacking Pokemon
            defender: Defending Pokemon
            move: Move being used

        Returns:
            Damage amount (integer)
        """
        if move.power is None or move.power == 0:
            return 0  # Status moves don't deal damage

        level = attacker.level
        power = move.power

        # Get appropriate attack/defense stats based on move category
        if move.is_physical():
            attack = attacker.stats.attack
            defense = defender.stats.defense
        else:  # Special
            attack = attacker.stats.special
            defense = defender.stats.special

        # Base damage calculation
        damage = (((2 * level / 5) + 2) * power * attack / defense) / 50 + 2

        # STAB (Same Type Attack Bonus)
        stab = 1.5 if (move.type == attacker.species.type1 or
                      move.type == attacker.species.type2) else 1.0

        # Type effectiveness
        type_effectiveness = get_dual_type_effectiveness(
            move.type,
            defender.species.type1,
            defender.species.type2
        )

        # Random factor (217-255)
        random_factor = random.randint(217, 255) / 255.0

        # Apply modifiers
        damage = damage * stab * type_effectiveness * random_factor

        # Minimum damage is 1 (if move hits and isn't 0x effective)
        if type_effectiveness > 0:
            damage = max(1, int(damage))
        else:
            damage = 0

        return int(damage)
