# ABOUTME: Dialog box UI component for NPC conversations
# ABOUTME: Handles rendering dialog text with simple box interface

import pygame

from src.engine import constants


class DialogBox:
    """Dialog box for NPC conversations."""

    def __init__(self, text, npc_name=None):
        """
        Initialize dialog box.

        Args:
            text: Dialog text to display
            npc_name: Optional NPC name to show
        """
        self.text = text
        self.npc_name = npc_name
        self.visible = True

        # Dialog box position (bottom of screen)
        self.x = 8 * constants.UI_SCALE
        self.y = 100 * constants.UI_SCALE
        self.width = (160 - 16) * constants.UI_SCALE
        self.height = 36 * constants.UI_SCALE

        # Colors (Game Boy palette)
        self.bg_color = (248, 248, 248)  # Light
        self.border_color = (0, 0, 0)
        self.text_color = (0, 0, 0)

    def _wrap_text(self, text, max_chars):
        """
        Wrap text to fit within max_chars per line.

        Args:
            text: Text to wrap
            max_chars: Maximum characters per line

        Returns:
            List of text lines
        """
        lines = []
        paragraphs = text.split('\n')

        for paragraph in paragraphs:
            words = paragraph.split(' ') if paragraph else []
            current_line = []

            for word in words:
                test_line = ' '.join(current_line + [word])
                if len(test_line) <= max_chars:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                    current_line = [word]

            if current_line:
                lines.append(' '.join(current_line))
            elif paragraph == "":
                lines.append("")

        return lines

    def render(self, renderer):
        """Render the dialog box."""
        if not self.visible:
            return

        # Draw background box
        border_width = 2 * constants.UI_SCALE
        inner_offset = 2 * constants.UI_SCALE
        renderer.draw_rect(self.border_color, (self.x, self.y, self.width, self.height), border_width)
        renderer.draw_rect(
            self.bg_color,
            (self.x + inner_offset, self.y + inner_offset,
             self.width - (inner_offset * 2), self.height - (inner_offset * 2)),
            0
        )

        # Draw NPC name if present
        text_y = self.y + (6 * constants.UI_SCALE)
        if self.npc_name:
            renderer.draw_text(
                f"{self.npc_name}:",
                self.x + (6 * constants.UI_SCALE),
                text_y,
                self.text_color,
                12 * constants.UI_SCALE
            )
            text_y += 14 * constants.UI_SCALE

        # Draw dialog text with word wrapping
        wrapped_lines = self._wrap_text(self.text, max_chars=21)
        for i, line in enumerate(wrapped_lines[:2]):  # Max 2 lines
            renderer.draw_text(
                line,
                self.x + (6 * constants.UI_SCALE),
                text_y + (i * (13 * constants.UI_SCALE)),
                self.text_color,
                12 * constants.UI_SCALE
            )

    def close(self):
        """Hide the dialog box."""
        self.visible = False
