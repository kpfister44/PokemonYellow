# ABOUTME: Party screen UI component for Pokemon list view
# ABOUTME: Renders party Pokemon with sprites, names, levels, and HP

import pygame
from typing import Optional
from src.party.party import Party
from src.battle.pokemon import Pokemon
from src.engine.constants import GAME_WIDTH, GAME_HEIGHT
from src.battle.hp_bar_display import HpBarDisplay


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
        self.bar_width = 48
        self.hp_displays = [
            HpBarDisplay(pokemon.stats.hp, pokemon.current_hp, self.bar_width)
            for pokemon in self.party.pokemon
        ]

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

    def get_display_units(self, index: int) -> int:
        if 0 <= index < len(self.hp_displays):
            return self.hp_displays[index].display_units
        return 0

    def update(self, dt: float) -> None:
        self._sync_displays()
        for pokemon, display in zip(self.party.pokemon, self.hp_displays):
            display.update(pokemon.current_hp, dt)

    def render(self, renderer) -> None:
        """
        Render the party screen.

        Args:
            renderer: Renderer instance for drawing
        """
        # Clear screen with white background
        renderer.clear((248, 248, 248))

        # Draw each Pokemon in party
        for i in range(min(6, self.party.size())):
            self._render_party_slot(renderer, i)

        # Draw prompt box at bottom (y=120, height=24 for 144 total)
        prompt_y = 120
        bg_color = (248, 248, 248)
        border_color = (0, 0, 0)

        # Draw bordered box
        renderer.draw_rect(bg_color, (0, prompt_y, GAME_WIDTH, 24), 0)
        renderer.draw_rect(border_color, (0, prompt_y, GAME_WIDTH, 24), 1)

        renderer.draw_text("Choose a POKéMON.", 8, prompt_y + 6)

    def _render_party_slot(self, renderer, index: int) -> None:
        """
        Render a single party slot with two rows per Pokemon.

        Row 1: cursor, sprite, NAME, :L##
        Row 2: HP bar + HP values

        Args:
            renderer: Renderer instance
            index: Party slot index (0-5)
        """
        pokemon = self.party.pokemon[index]
        display = self.hp_displays[index]

        # Each Pokemon gets 20px (two rows of ~10px each)
        slot_height = 20
        y = 2 + (index * slot_height)

        # === ROW 1: Cursor, Sprite, Name, Level ===

        # Draw selection cursor at x=4
        if index == self.cursor_index:
            renderer.draw_text("▶", 4, y)

        # Draw Pokemon sprite (16x16) at x=16
        if pokemon.species.sprites and pokemon.species.sprites.front:
            sprite = renderer.load_sprite(pokemon.species.sprites.front)
            if sprite:
                scaled_sprite = pygame.transform.scale(sprite, (16, 16))
                if pokemon.is_fainted():
                    scaled_sprite.set_alpha(100)
                renderer.game_surface.blit(scaled_sprite, (16, y))

        # Draw Pokemon name at x=36
        name_text = pokemon.species.name.upper()
        renderer.draw_text(name_text, 36, y)

        # Draw level (format: :L##)
        level_text = f":L{pokemon.level}"
        renderer.draw_text(level_text, 100, y)

        # === ROW 2: HP bar + HP values ===
        row2_y = y + 10

        if pokemon.is_fainted():
            # Just show FNT for fainted Pokemon
            renderer.draw_text("FNT", 36, row2_y)
        else:
            # Draw HP bar
            bar_x = 36
            bar_width = self.bar_width
            bar_height = 4

            # Background (empty bar)
            renderer.draw_rect((200, 200, 200), (bar_x, row2_y + 2, bar_width, bar_height), 0)

            # Calculate HP percentage and color
            hp_percent = display.display_hp / pokemon.stats.hp if pokemon.stats.hp > 0 else 0
            filled_width = display.display_units

            # Color: green > 50%, yellow 20-50%, red < 20%
            if hp_percent > 0.5:
                color = (0, 200, 0)
            elif hp_percent > 0.2:
                color = (248, 208, 48)
            else:
                color = (248, 88, 56)

            # Draw filled portion
            if filled_width > 0:
                renderer.draw_rect(color, (bar_x, row2_y + 2, filled_width, bar_height), 0)

            # Draw border
            renderer.draw_rect((0, 0, 0), (bar_x, row2_y + 2, bar_width, bar_height), 1)

            # Draw HP values next to bar
            hp_text = f"{display.display_hp}/{pokemon.stats.hp}"
            renderer.draw_text(hp_text, bar_x + bar_width + 4, row2_y)

    def _sync_displays(self) -> None:
        if len(self.hp_displays) != self.party.size():
            self.hp_displays = [
                HpBarDisplay(pokemon.stats.hp, pokemon.current_hp, self.bar_width)
                for pokemon in self.party.pokemon
            ]
            return

        for index, pokemon in enumerate(self.party.pokemon):
            display = self.hp_displays[index]
            if display.max_hp != pokemon.stats.hp:
                self.hp_displays[index] = HpBarDisplay(
                    pokemon.stats.hp,
                    pokemon.current_hp,
                    self.bar_width
                )
