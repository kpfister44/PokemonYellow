# ABOUTME: Save file storage utilities for JSON persistence
# ABOUTME: Handles reading and writing save data to disk

import json
from pathlib import Path

from src.save.save_data import SaveData


DEFAULT_SAVE_DIR = Path("saves")
DEFAULT_SAVE_PATH = DEFAULT_SAVE_DIR / "save.json"


def _resolve_save_path(save_path: Path | str | None) -> Path:
    if save_path is None:
        return DEFAULT_SAVE_PATH
    return Path(save_path)


def save_exists(save_path: Path | str | None = None) -> bool:
    """Return True if a save file exists."""
    path = _resolve_save_path(save_path)
    return path.exists()


def write_save_data(save_data: SaveData, save_path: Path | str | None = None) -> None:
    """Write save data to disk."""
    path = _resolve_save_path(save_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(save_data.to_dict(), handle, indent=2)


def load_save_data(save_path: Path | str | None, species_loader) -> SaveData:
    """Load save data from disk."""
    path = _resolve_save_path(save_path)
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    return SaveData.from_dict(data, species_loader)
