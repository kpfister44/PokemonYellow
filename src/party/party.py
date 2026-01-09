# ABOUTME: Party management for up to 6 Pokemon
# ABOUTME: Handles add, remove, swap, and active Pokemon operations

from typing import Optional
from src.battle.pokemon import Pokemon


class Party:
    """Manages player's party of up to 6 Pokemon."""

    MAX_SIZE = 6

    def __init__(self):
        """Initialize empty party."""
        self.pokemon: list[Pokemon] = []

    def size(self) -> int:
        """Return number of Pokemon in party."""
        return len(self.pokemon)

    def is_full(self) -> bool:
        """Check if party is at max capacity."""
        return len(self.pokemon) >= self.MAX_SIZE

    def add(self, pokemon: Pokemon) -> bool:
        """
        Add Pokemon to party.

        Args:
            pokemon: Pokemon to add

        Returns:
            True if added successfully, False if party full
        """
        if self.is_full():
            return False

        self.pokemon.append(pokemon)
        return True

    def remove(self, index: int) -> Optional[Pokemon]:
        """
        Remove Pokemon at index.

        Args:
            index: Position in party (0-5)

        Returns:
            Removed Pokemon, or None if index invalid
        """
        if 0 <= index < len(self.pokemon):
            return self.pokemon.pop(index)
        return None

    def get_active(self) -> Optional[Pokemon]:
        """
        Get active Pokemon (first non-fainted Pokemon).

        Returns:
            Active Pokemon, or None if party empty/all fainted
        """
        for pokemon in self.pokemon:
            if not pokemon.is_fainted():
                return pokemon
        return None

    def swap(self, index1: int, index2: int) -> bool:
        """
        Swap positions of two Pokemon.

        Args:
            index1: First position
            index2: Second position

        Returns:
            True if swapped, False if indices invalid
        """
        if (0 <= index1 < len(self.pokemon) and
            0 <= index2 < len(self.pokemon)):
            self.pokemon[index1], self.pokemon[index2] = (
                self.pokemon[index2], self.pokemon[index1]
            )
            return True
        return False

    def get_all_alive(self) -> list[Pokemon]:
        """Get all non-fainted Pokemon."""
        return [p for p in self.pokemon if not p.is_fainted()]

    def has_alive_pokemon(self) -> bool:
        """Check if party has any non-fainted Pokemon."""
        return any(not p.is_fainted() for p in self.pokemon)
