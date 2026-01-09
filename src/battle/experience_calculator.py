# ABOUTME: Experience calculation for Pokemon battles
# ABOUTME: Implements Gen 1 experience formulas and level-up requirements

from src.battle.pokemon import Pokemon


class ExperienceCalculator:
    """Calculate experience gain and level-up requirements."""

    def calculate_exp_gain(self, defeated: Pokemon, is_wild: bool, participated: int) -> int:
        """
        Calculate experience gain using Gen 1 formula.

        Args:
            defeated: Defeated Pokemon
            is_wild: True for wild battles, False for trainer battles
            participated: Number of Pokemon that participated

        Returns:
            Experience points gained
        """
        base = defeated.species.base_experience
        level = defeated.level

        trainer_mod = 1.5 if not is_wild else 1.0
        exp = int((base * level / 7) * trainer_mod / participated)

        return exp

    def get_exp_for_level(self, growth_rate: str, level: int) -> int:
        """
        Calculate total EXP needed to reach level.

        Args:
            growth_rate: Growth rate name (fast, medium-fast, medium-slow, slow)
            level: Target level

        Returns:
            Total experience required
        """
        n = level

        if growth_rate == "fast":
            return int((4 * n ** 3) / 5)
        if growth_rate == "medium-fast" or growth_rate == "medium":
            return n ** 3
        if growth_rate == "medium-slow":
            return int((6 * n ** 3 / 5) - (15 * n ** 2) + (100 * n) - 140)
        if growth_rate == "slow":
            return int((5 * n ** 3) / 4)

        return n ** 3
