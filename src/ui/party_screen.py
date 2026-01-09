# ABOUTME: Party screen UI component for Pokemon list view
# ABOUTME: Renders party Pokemon with sprites, names, levels, and HP

import pygame
from typing import Optional
from src.party.party import Party
from src.battle.pokemon import Pokemon
from src.engine.constants import GAME_WIDTH, GAME_HEIGHT


class PartyScreen:
    """Party screen UI component showing list of Pokemon."""

    def __init__(self, party: Party):
        """
        Initialize party screen.

        Args:
            party: Party to display
        """
        self.party = party
        self.cursor_index = 0

    def move_cursor(self, direction: int):
        """
        Move cursor up (-1) or down (1).

        Args:
            direction: -1 for up, 1 for down
        """
        if self.party.size() > 0:
            self.cursor_index = (self.cursor_index + direction) % self.party.size()

    def get_selected_pokemon(self) -> Optional[Pokemon]:
        """
        Get currently selected Pokemon.

        Returns:
            Currently selected Pokemon, or None if party empty
        """
        if 0 <= self.cursor_index < self.party.size():
            return self.party.pokemon[self.cursor_index]
        return None

    def render(self, renderer):
        """
        Render the party screen.

        Args:
            renderer: Renderer instance for drawing
        """
        # Clear screen with white background
        surface = renderer.surface
        surface.fill((248, 248, 248))

        # Draw each Pokemon in party
        for i in range(min(6, self.party.size())):
            self._render_party_slot(renderer, i)

        # Draw prompt text at bottom
        prompt_y = GAME_HEIGHT - 24
        bg_color = (248, 248, 248)
        border_color = (0, 0, 0)

        # Draw box
        renderer.draw_rect(bg_color, (0, prompt_y, GAME_WIDTH, 24), 0)
        renderer.draw_rect(border_color, (0, prompt_y, GAME_WIDTH, 24), 2)

        renderer.draw_text("Choose a POKéMON.", 8, prompt_y + 8)

    def _render_party_slot(self, renderer, index: int):
        """
        Render a single party slot.

        Args:
            renderer: Renderer instance
            index: Party slot index (0-5)
        """
        pokemon = self.party.pokemon[index]
        surface = renderer.surface

        # Calculate position (2 rows of 3)
        slot_width = GAME_WIDTH // 2
        slot_height = 40
        x = (index % 2) * slot_width
        y = (index // 2) * slot_height + 8

        # Draw selection cursor
        if index == self.cursor_index:
            renderer.draw_text("▶", x + 4, y + 12)

        # Draw Pokemon sprite (if available)
        if pokemon.species.sprites and pokemon.species.sprites.front:
            sprite = renderer.load_sprite(pokemon.species.sprites.front)
            if sprite:
                # Scale sprite to 32x32
                scaled_sprite = pygame.transform.scale(sprite, (32, 32))
                surface.blit(scaled_sprite, (x + 16, y + 4))

        # Draw Pokemon info
        info_x = x + 52

        # Name and level
        name_text = f"{pokemon.species.name.upper()}"
        renderer.draw_text(name_text, info_x, y + 4)

        level_text = f"Lv{pokemon.level}"
        renderer.draw_text(level_text, info_x + 60, y + 4)

        # HP
        hp_text = f"{pokemon.current_hp:3d}/{pokemon.stats.hp:3d}"
        renderer.draw_text(hp_text, info_x, y + 20)

        # Status condition (if any)
        if pokemon.status and pokemon.status.name != "NONE":
            status_text = pokemon.status.name[:3]  # e.g., "PAR", "BRN"
            renderer.draw_text(status_text, info_x + 60, y + 20)
