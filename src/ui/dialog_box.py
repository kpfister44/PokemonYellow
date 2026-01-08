# ABOUTME: Dialog box UI component for NPC conversations
# ABOUTME: Handles rendering dialog text with simple box interface

import pygame


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
        self.x = 8
        self.y = 100  # Near bottom of 144px screen
        self.width = 160 - 16  # Full width minus padding
        self.height = 36

        # Colors (Game Boy palette)
        self.bg_color = (248, 248, 248)  # Light
        self.border_color = (0, 0, 0)
        self.text_color = (0, 0, 0)

    def render(self, renderer):
        """Render the dialog box."""
        if not self.visible:
            return

        # Draw background box
        renderer.draw_rect(self.border_color, (self.x, self.y, self.width, self.height), 2)
        renderer.draw_rect(self.bg_color, (self.x+2, self.y+2, self.width-4, self.height-4), 0)

        # Draw NPC name if present
        text_y = self.y + 6
        if self.npc_name:
            renderer.draw_text(f"{self.npc_name}:", self.x + 6, text_y, self.text_color, 12)
            text_y += 14

        # Draw dialog text (simple, no wrapping for MVP)
        renderer.draw_text(self.text, self.x + 6, text_y, self.text_color, 12)

    def close(self):
        """Hide the dialog box."""
        self.visible = False
