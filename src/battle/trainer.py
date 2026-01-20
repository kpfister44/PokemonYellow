# ABOUTME: Trainer data structure for NPC battles
# ABOUTME: Defines trainer info and Pokemon teams

from dataclasses import dataclass

from src.battle.pokemon import Pokemon
from src.battle.species_loader import SpeciesLoader


@dataclass
class Trainer:
    """NPC trainer with Pokemon team."""
    name: str
    trainer_class: str
    team: list[dict]
    prize_money: int

    def get_party(self, species_loader: SpeciesLoader) -> list[Pokemon]:
        """
        Build Pokemon instances from team data.

        Args:
            species_loader: SpeciesLoader instance

        Returns:
            List of Pokemon instances
        """
        party = []
        for pokemon_data in self.team:
            # Accept either "species" or "species_id" for flexibility
            species_name = pokemon_data.get("species") or pokemon_data.get("species_id")
            species = species_loader.get_species(species_name)
            pokemon = Pokemon(species, pokemon_data["level"])
            party.append(pokemon)

        return party
