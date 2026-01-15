# ABOUTME: Tests dialog text wrapping behavior
# ABOUTME: Ensures explicit newlines are preserved

from src.ui.dialog_box import DialogBox


def test_dialog_box_wraps_preserves_newlines():
    dialog = DialogBox("NAME found\nRARE CANDY!")

    lines = dialog._wrap_text(dialog.text, max_chars=21)

    assert lines == ["NAME found", "RARE CANDY!"]
