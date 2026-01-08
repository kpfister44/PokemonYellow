# ABOUTME: Pokemon instance class for individual Pokemon
# ABOUTME: Handles stats calculation, moves, and battle state

from dataclasses import dataclass
from src.battle.species import Species
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

        # Status condition (none for Phase 6)
        self.status = None

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
