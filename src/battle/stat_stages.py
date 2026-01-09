# ABOUTME: Stat stage tracking for battle system
# ABOUTME: Implements Gen 1 stat stage modifiers (-6 to +6) and multiplier calculation

from dataclasses import dataclass


@dataclass
class StatStages:
    """
    Track stat stage modifiers for a Pokemon in battle.

    Gen 1 mechanics:
    - Each stat can be modified from -6 to +6 stages
    - Stage 0 is neutral (no modifier)
    - Multipliers use numerator/denominator ratios, not simple percentages
    """
    attack: int = 0
    defense: int = 0
    speed: int = 0
    special: int = 0
    accuracy: int = 0
    evasion: int = 0

    def modify(self, stat: str, change: int) -> bool:
        """
        Apply stat stage change, respecting -6 to +6 limits.

        Args:
            stat: Stat name (attack, defense, speed, special, accuracy, evasion)
            change: Number of stages to modify (can be negative)

        Returns:
            True if stat was changed, False if already at limit
        """
        if not hasattr(self, stat):
            raise ValueError(f"Invalid stat name: {stat}")

        current_stage = getattr(self, stat)
        new_stage = max(-6, min(6, current_stage + change))

        if new_stage == current_stage:
            return False  # Already at limit

        setattr(self, stat, new_stage)
        return True

    def get_multiplier(self, stat: str) -> float:
        """
        Get Gen 1 stat stage multiplier.

        Gen 1 uses numerator/denominator ratios:
        - Stage -6: 2/8 = 0.25x
        - Stage -5: 2/7 = 0.286x
        - Stage -4: 2/6 = 0.333x
        - Stage -3: 2/5 = 0.4x
        - Stage -2: 2/4 = 0.5x
        - Stage -1: 2/3 = 0.667x
        - Stage  0: 2/2 = 1.0x
        - Stage +1: 3/2 = 1.5x
        - Stage +2: 4/2 = 2.0x
        - Stage +3: 5/2 = 2.5x
        - Stage +4: 6/2 = 3.0x
        - Stage +5: 7/2 = 3.5x
        - Stage +6: 8/2 = 4.0x

        Args:
            stat: Stat name

        Returns:
            Multiplier to apply to base stat
        """
        if not hasattr(self, stat):
            raise ValueError(f"Invalid stat name: {stat}")

        stage = getattr(self, stat)

        # Gen 1 formula
        if stage >= 0:
            # Positive stages: (2 + stage) / 2
            numerator = 2 + stage
            denominator = 2
        else:
            # Negative stages: 2 / (2 - stage)
            numerator = 2
            denominator = 2 - stage

        return numerator / denominator

    def reset(self):
        """Reset all stat stages to 0."""
        self.attack = 0
        self.defense = 0
        self.speed = 0
        self.special = 0
        self.accuracy = 0
        self.evasion = 0
