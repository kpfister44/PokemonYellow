# ABOUTME: Dialog loader for NPC dialog text keyed by dialog_id
# ABOUTME: Reads dialog entries from YAML and caches them for reuse

import os

from src.data import data_loader


class DialogLoader:
    """Loads dialog text keyed by dialog_id."""

    def __init__(self, dialog_path: str = "data/dialogs/dialogs.yaml"):
        self.dialog_path = dialog_path
        self.dialogs = self._load_dialogs()

    def _load_dialogs(self) -> dict[str, str]:
        if not os.path.exists(self.dialog_path):
            return {}
        data = data_loader.load_yaml(self.dialog_path)
        if not data:
            return {}
        return data.get("dialogs", {})

    def get_dialog(self, dialog_id: str) -> str | None:
        if dialog_id is None:
            return None
        return self.dialogs.get(dialog_id, dialog_id)
