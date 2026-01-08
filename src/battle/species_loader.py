# ABOUTME: Species data loader for Pokemon definitions
# ABOUTME: Loads and caches species data from YAML

from src.battle.species import Species
from src.data import data_loader


class SpeciesLoader:
    """Loads and caches Pokemon species data."""

    def __init__(self):
        """Initialize species loader."""
        self.species_cache = {}
        self._load_all_species()

    def _load_all_species(self):
        """Load all species from YAML."""
        data = data_loader.load_yaml("data/pokemon/species.yaml")
        species_list = data.get("species", [])

        for spec_data in species_list:
            species = Species.from_dict(spec_data)
            self.species_cache[species.species_id] = species

    def get_species(self, species_id: str) -> Species:
        """
        Get species by ID.

        Args:
            species_id: Species identifier (e.g., "rattata")

        Returns:
            Species instance

        Raises:
            KeyError: If species not found
        """
        if species_id not in self.species_cache:
            raise KeyError(f"Species not found: {species_id}")

        return self.species_cache[species_id]

    def get_all_species(self) -> dict[str, Species]:
        """Get all loaded species."""
        return self.species_cache.copy()
