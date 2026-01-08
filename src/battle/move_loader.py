# ABOUTME: Move data loader for battle system
# ABOUTME: Loads and caches move definitions from YAML

from src.battle.move import Move
from src.data import data_loader


class MoveLoader:
    """Loads and caches move data."""

    def __init__(self):
        """Initialize move loader."""
        self.moves_cache = {}
        self._load_all_moves()

    def _load_all_moves(self):
        """Load all moves from YAML."""
        moves_data = data_loader.load_yaml("data/moves/moves.yaml")

        for move_id, move_data in moves_data.items():
            self.moves_cache[move_id] = Move.from_dict(move_id, move_data)

    def get_move(self, move_id: str) -> Move:
        """
        Get move by ID.

        Args:
            move_id: Move identifier (e.g., "tackle")

        Returns:
            Move instance

        Raises:
            KeyError: If move not found
        """
        if move_id not in self.moves_cache:
            raise KeyError(f"Move not found: {move_id}")

        return self.moves_cache[move_id]

    def get_all_moves(self) -> dict[str, Move]:
        """Get all loaded moves."""
        return self.moves_cache.copy()
