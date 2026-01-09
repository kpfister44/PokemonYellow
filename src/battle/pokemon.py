# ABOUTME: Pokemon instance class for individual Pokemon
# ABOUTME: Handles stats calculation, moves, and battle state

from dataclasses import dataclass, field
from src.battle.species import Species
from src.battle.status_effects import StatusCondition
from src.battle.stat_stages import StatStages
from typing import Optional
import random


@dataclass
class PokemonStats:
    """Calculated stats for a Pokemon instance."""
    hp: int
    attack: int
    defense: int
    special: int
    speed: int


class Pokemon:
    """Individual Pokemon instance (not species)."""

    def __init__(self, species: Species, level: int):
        """
        Create a Pokemon instance.

        Args:
            species: Species data
            level: Pokemon level (1-100)
        """
        self.species = species
        self.level = level

        # Generate random IVs (0-15 in Gen 1)
        self.iv_attack = random.randint(0, 15)
        self.iv_defense = random.randint(0, 15)
        self.iv_speed = random.randint(0, 15)
        self.iv_special = random.randint(0, 15)

        # HP IV derived from other IVs in Gen 1
        self.iv_hp = self._calculate_hp_iv()

        # Calculate stats
        self.stats = self._calculate_stats()

        # Current HP (starts at max)
        self.current_hp = self.stats.hp

        # Moves (for Phase 6, just the level 1 move)
        self.moves = self._determine_moves()

        # Status condition
        self.status: Optional[StatusCondition] = None
        self.status_turns: int = 0  # For sleep counter and toxic damage

        # Stat stage modifiers
        self.stat_stages: StatStages = StatStages()

        # Experience tracking
        self.experience: int = 0
        self.exp_to_next_level: int = 0
        self._update_exp_requirements()

    def _calculate_hp_iv(self) -> int:
        """
        Calculate HP IV from other IVs (Gen 1 mechanic).
        HP IV = (Atk IV odd) * 8 + (Def IV odd) * 4 + (Spd IV odd) * 2 + (Spc IV odd)
        """
        return (
            ((self.iv_attack & 1) << 3) |
            ((self.iv_defense & 1) << 2) |
            ((self.iv_speed & 1) << 1) |
            (self.iv_special & 1)
        )

    def _calculate_stats(self) -> PokemonStats:
        """
        Calculate stats using Gen 1 formulas.

        Stat = floor(((Base + IV) * 2 * Level) / 100) + Level + 10
        HP = floor(((Base + IV) * 2 * Level) / 100) + Level + 10
        """
        base = self.species.base_stats

        # HP formula (same in Gen 1)
        hp = ((base.hp + self.iv_hp) * 2 * self.level) // 100 + self.level + 10

        # Other stats
        attack = ((base.attack + self.iv_attack) * 2 * self.level) // 100 + 5
        defense = ((base.defense + self.iv_defense) * 2 * self.level) // 100 + 5
        special = ((base.special + self.iv_special) * 2 * self.level) // 100 + 5
        speed = ((base.speed + self.iv_speed) * 2 * self.level) // 100 + 5

        return PokemonStats(
            hp=hp,
            attack=attack,
            defense=defense,
            special=special,
            speed=speed
        )

    def _determine_moves(self) -> list[str]:
        """
        Determine which moves this Pokemon knows.
        For Phase 6: just the first move learned at level 1.
        """
        moves = []
        for learned_move in self.species.level_up_moves:
            if learned_move.level <= self.level:
                moves.append(learned_move.move)

        # For Phase 6, just take the first move
        return moves[:1] if moves else []

    def take_damage(self, damage: int):
        """Apply damage to this Pokemon."""
        self.current_hp = max(0, self.current_hp - damage)

    def is_fainted(self) -> bool:
        """Check if Pokemon has fainted."""
        return self.current_hp <= 0

    def get_hp_percentage(self) -> float:
        """Get HP as a percentage (0.0 to 1.0)."""
        return self.current_hp / self.stats.hp if self.stats.hp > 0 else 0.0

    def apply_status(self, condition: StatusCondition) -> bool:
        """
        Apply status condition if not already statused.

        Gen 1 rule: Pokemon can only have one status condition at a time.

        Args:
            condition: Status condition to apply

        Returns:
            True if status was applied, False if already statused
        """
        if self.status is not None and self.status != StatusCondition.NONE:
            return False  # Already has a status

        self.status = condition

        # Initialize sleep turns (1-7 turns in Gen 1)
        if condition == StatusCondition.SLEEP:
            self.status_turns = random.randint(1, 7)

        # Initialize toxic counter
        if condition == StatusCondition.BADLY_POISON:
            self.status_turns = 0  # Will increment each turn

        return True

    def apply_stat_change(self, stat: str, change: int) -> tuple[bool, str]:
        """
        Apply stat stage change.

        Args:
            stat: Stat name (attack, defense, speed, special, accuracy, evasion)
            change: Number of stages to modify

        Returns:
            Tuple of (changed: bool, message: str)
        """
        changed = self.stat_stages.modify(stat, change)

        if changed:
            direction = "rose" if change > 0 else "fell"
            if abs(change) >= 2:
                modifier = "sharply "
            else:
                modifier = ""
            return (True, f"{modifier}{direction}")
        else:
            if change > 0:
                return (False, "won't go any higher")
            else:
                return (False, "won't go any lower")

    def _update_exp_requirements(self):
        """Update experience required for next level."""
        from src.battle.experience_calculator import ExperienceCalculator

        calc = ExperienceCalculator()
        current_level_exp = calc.get_exp_for_level(self.species.growth_rate, self.level)
        next_level_exp = calc.get_exp_for_level(self.species.growth_rate, self.level + 1)

        if self.experience == 0:
            self.experience = current_level_exp

        self.exp_to_next_level = next_level_exp

    def gain_experience(self, amount: int) -> bool:
        """
        Add experience and check for level up.

        Args:
            amount: Experience points to add

        Returns:
            True if Pokemon leveled up
        """
        self.experience += amount

        if self.experience >= self.exp_to_next_level:
            return True

        return False

    def level_up(self):
        """Increase level and recalculate stats."""
        self.level += 1

        old_stats = self.stats
        self.stats = self._calculate_stats()

        self.current_hp = self.stats.hp

        self._update_exp_requirements()

        return old_stats
