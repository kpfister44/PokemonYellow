# ABOUTME: Save data definitions for persistence of game state
# ABOUTME: Handles serialization to and from dictionaries

from typing import Any, Iterable

from src.items.bag import Bag
from src.party.party import Party


SAVE_DATA_VERSION = 1


def _default_reserved_flags() -> dict[str, Any]:
    return {
        "badges": [],
        "story": {},
        "pokedex_seen": [],
        "pokedex_caught": []
    }


def _normalize_flag_list(values: Iterable[str] | None) -> list[str]:
    if values is None:
        return []
    if isinstance(values, set):
        return sorted(values)
    if isinstance(values, list):
        return values
    return list(values)


def _normalize_reserved_flags(reserved_flags: dict[str, Any] | None) -> dict[str, Any]:
    normalized = _default_reserved_flags()
    if reserved_flags:
        normalized.update(reserved_flags)

    normalized["pokedex_seen"] = _normalize_flag_list(normalized.get("pokedex_seen"))
    normalized["pokedex_caught"] = _normalize_flag_list(normalized.get("pokedex_caught"))
    normalized["badges"] = list(normalized.get("badges", []))
    normalized["story"] = normalized.get("story") or {}
    return normalized


class SaveData:
    """Represents a full save snapshot for the game."""

    def __init__(
        self,
        player_name: str,
        player_direction: str,
        map_path: str,
        player_x: int,
        player_y: int,
        party: Party,
        bag: Bag,
        defeated_trainers: Iterable[str],
        collected_items: Iterable[str],
        reserved_flags: dict[str, Any] | None = None,
        version: int = SAVE_DATA_VERSION
    ):
        self.version = version
        self.player_name = player_name
        self.player_direction = player_direction
        self.map_path = map_path
        self.player_x = player_x
        self.player_y = player_y
        self.party = party
        self.bag = bag
        self.defeated_trainers = set(defeated_trainers)
        self.collected_items = set(collected_items)
        self.reserved_flags = _normalize_reserved_flags(reserved_flags)

    def to_dict(self) -> dict[str, Any]:
        """Serialize save data to a dictionary."""
        return {
            "version": self.version,
            "player": {
                "name": self.player_name,
                "direction": self.player_direction
            },
            "overworld": {
                "map_path": self.map_path,
                "x": self.player_x,
                "y": self.player_y
            },
            "party": self.party.to_dict(),
            "bag": self.bag.to_dict(),
            "flags": {
                "defeated_trainers": sorted(self.defeated_trainers),
                "collected_items": sorted(self.collected_items),
                "reserved": self.reserved_flags
            }
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any], species_loader) -> "SaveData":
        """Deserialize save data from a dictionary."""
        player_data = data.get("player", {})
        overworld_data = data.get("overworld", {})
        flags_data = data.get("flags", {})

        party = Party.from_dict(data.get("party", []), species_loader)
        bag = Bag.from_dict(data.get("bag", []))

        reserved_flags = _normalize_reserved_flags(flags_data.get("reserved"))

        return cls(
            player_name=player_data.get("name", "PLAYER"),
            player_direction=player_data.get("direction", "down"),
            map_path=overworld_data.get("map_path", "data/maps/pallet_town.json"),
            player_x=overworld_data.get("x", 0),
            player_y=overworld_data.get("y", 0),
            party=party,
            bag=bag,
            defeated_trainers=set(flags_data.get("defeated_trainers", [])),
            collected_items=set(flags_data.get("collected_items", [])),
            reserved_flags=reserved_flags,
            version=data.get("version", SAVE_DATA_VERSION)
        )

    def get_pokedex_seen(self) -> set[str]:
        return set(self.reserved_flags.get("pokedex_seen", []))

    def get_pokedex_caught(self) -> set[str]:
        return set(self.reserved_flags.get("pokedex_caught", []))
