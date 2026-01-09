# ABOUTME: Gen 1 damage calculation engine
# ABOUTME: Implements authentic Gen 1 damage formula with type effectiveness

from src.battle.pokemon import Pokemon
from src.battle.move import Move
from src.battle.type_chart import get_dual_type_effectiveness
import random


class DamageCalculator:
    """Calculate damage using Gen 1 formula."""

    def check_accuracy(self, attacker: Pokemon, defender: Pokemon, move: Move) -> bool:
        """
        Roll accuracy check considering move accuracy and stat stages.

        Returns:
            True if attack hits, False if misses
        """
        if move.accuracy is None:
            return True  # Never-miss moves (e.g., Swift)

        # Get stat stage modifiers
        acc_stage = attacker.stat_stages.accuracy
        eva_stage = defender.stat_stages.evasion

        # Gen 1: Accuracy = move_accuracy * acc_multiplier / eva_multiplier
        acc_mult = attacker.stat_stages.get_multiplier("accuracy")
        eva_mult = defender.stat_stages.get_multiplier("evasion")

        threshold = int(move.accuracy * acc_mult / eva_mult)

        # Roll 0-99, hit if roll < threshold
        return random.randint(0, 99) < threshold

    def check_critical_hit(self, attacker: Pokemon, move: Move) -> bool:
        """
        Gen 1 critical hit mechanics based on speed and move crit_rate.

        Returns:
            True if critical hit
        """
        crit_rate_boost = move.meta.crit_rate if move.meta else 0

        # Gen 1: base_rate = speed / 512, high-crit moves = speed / 64
        if crit_rate_boost > 0:
            threshold = attacker.stats.speed / 64
        else:
            threshold = attacker.stats.speed / 512

        return random.random() < min(threshold, 0.255)  # Cap at 255/256

    def get_hit_count(self, move: Move) -> int:
        """
        Determine number of hits for multi-hit moves.

        Returns:
            Number of hits (1 for normal moves)
        """
        if not move.meta or move.meta.min_hits is None:
            return 1

        if move.meta.min_hits == 2 and move.meta.max_hits == 2:
            return 2

        if move.meta.min_hits == 2 and move.meta.max_hits == 5:
            # 37.5% 2 hits, 37.5% 3 hits, 12.5% 4 hits, 12.5% 5 hits
            roll = random.randint(0, 7)
            if roll < 3:
                return 2
            if roll < 6:
                return 3
            if roll == 6:
                return 4
            return 5

        return 1

    def calculate_damage(self, attacker: Pokemon, defender: Pokemon, move: Move, is_critical: bool = False) -> int:
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
        # Apply stat stage multipliers
        if move.is_physical():
            attack = attacker.stats.attack * attacker.stat_stages.get_multiplier("attack")
            defense = defender.stats.defense * defender.stat_stages.get_multiplier("defense")
        else:  # Special
            attack = attacker.stats.special * attacker.stat_stages.get_multiplier("special")
            defense = defender.stats.special * defender.stat_stages.get_multiplier("special")

        # Base damage calculation
        damage = (((2 * level / 5) + 2) * power * attack / defense) / 50 + 2

        # Burn halves physical attack damage
        from src.battle.status_effects import StatusCondition
        if attacker.status == StatusCondition.BURN and move.is_physical():
            damage = damage // 2

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

        # Critical hit doubles damage in Gen 1
        if is_critical:
            damage = int(damage * 2)

        # Minimum damage is 1 (if move hits and isn't 0x effective)
        if type_effectiveness > 0:
            damage = max(1, int(damage))
        else:
            damage = 0

        return int(damage)
