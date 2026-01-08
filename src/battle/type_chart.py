# ABOUTME: Type effectiveness chart for damage calculation
# ABOUTME: Loads and queries Gen 1 type matchups

from src.data import data_loader


class TypeChart:
    """Type effectiveness lookup for damage calculation."""

    def __init__(self):
        """Load type chart data."""
        self.chart = data_loader.load_yaml("data/types/type_chart.yaml")

    def get_effectiveness(self, attacking_type: str, defending_type: str) -> float:
        """
        Get type effectiveness multiplier.

        Args:
            attacking_type: Type of the attacking move
            defending_type: Type of the defending Pokemon

        Returns:
            Multiplier (0.0, 0.5, 1.0, or 2.0)
        """
        if attacking_type not in self.chart:
            return 1.0

        matchups = self.chart[attacking_type]
        return matchups.get(defending_type, 1.0)

    def get_dual_type_effectiveness(self, attacking_type: str,
                                   def_type1: str, def_type2: str = None) -> float:
        """
        Get effectiveness against dual-type Pokemon.

        Args:
            attacking_type: Type of the move
            def_type1: Primary type
            def_type2: Secondary type (optional)

        Returns:
            Combined multiplier
        """
        multiplier = self.get_effectiveness(attacking_type, def_type1)

        if def_type2:
            multiplier *= self.get_effectiveness(attacking_type, def_type2)

        return multiplier


# Global instance
_type_chart = TypeChart()


def get_effectiveness(attacking_type: str, defending_type: str) -> float:
    """Global function to get type effectiveness."""
    return _type_chart.get_effectiveness(attacking_type, defending_type)


def get_dual_type_effectiveness(attacking_type: str,
                                def_type1: str, def_type2: str = None) -> float:
    """Global function to get dual-type effectiveness."""
    return _type_chart.get_dual_type_effectiveness(attacking_type, def_type1, def_type2)
