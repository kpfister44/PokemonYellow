# ABOUTME: Summary screen UI component for detailed Pokemon info
# ABOUTME: Renders INFO and MOVES pages with stats, types, and move list

import pygame
from typing import Optional

from src.battle.pokemon import Pokemon
from src.engine import constants
from src.party.party import Party


class SummaryScreen:
    """Summary screen UI component showing detailed Pokemon info."""

    def __init__(self, pokemon: Pokemon, party: Party):
        """
        Initialize summary screen.

        Args:
            pokemon: Pokemon to display
            party: Party containing the Pokemon
        """
        self.pokemon = pokemon
        self.party = party
        self.current_page = 0  # 0=INFO, 1=MOVES

        # Find this Pokemon's index in the party
        self.pokemon_index = 0
        for i, p in enumerate(party.pokemon):
            if p == pokemon:
                self.pokemon_index = i
                break

    def change_page(self, direction: int) -> None:
        """
        Switch between INFO and MOVES pages with wrapping.

        Args:
            direction: -1 for left, 1 for right
        """
        self.current_page = (self.current_page + direction) % 2

    def change_pokemon(self, direction: int) -> None:
        """
        Switch to next/previous Pokemon in party with wrapping.

        Args:
            direction: -1 for up, 1 for down
        """
        party_size = self.party.size()
        if party_size > 0:
            self.pokemon_index = (self.pokemon_index + direction) % party_size
            self.pokemon = self.party.pokemon[self.pokemon_index]

    def render(self, renderer) -> None:
        """
        Render the summary screen.

        Args:
            renderer: Renderer instance for drawing
        """
        if self.current_page == 0:
            self._render_info_page(renderer)
        else:
            self._render_moves_page(renderer)

    def _render_info_page(self, renderer) -> None:
        """
        Render INFO page matching authentic Pokemon Yellow layout.

        Args:
            renderer: Renderer instance
        """
        renderer.clear((248, 248, 248))
        font_size = 16 * constants.UI_SCALE

        # === TOP SECTION ===

        # Draw large sprite (56x56) at top-left
        if self.pokemon.species.sprites and self.pokemon.species.sprites.front:
            sprite = renderer.load_sprite(self.pokemon.species.sprites.front)
            if sprite and isinstance(sprite, pygame.Surface):
                sprite_size = 56 * constants.UI_SCALE
                scaled_sprite = pygame.transform.scale(sprite, (sprite_size, sprite_size))
                renderer.game_surface.blit(scaled_sprite, (8 * constants.UI_SCALE, 8 * constants.UI_SCALE))

        # Draw Pokedex number below sprite
        pokedex_num = f"No.{self.pokemon.species.number:03d}"
        renderer.draw_text(
            pokedex_num,
            8 * constants.UI_SCALE,
            66 * constants.UI_SCALE,
            font_size=font_size
        )

        # === RIGHT PANEL (x=72) ===

        # Pokemon name
        name_text = self.pokemon.species.name.upper()
        renderer.draw_text(
            name_text,
            72 * constants.UI_SCALE,
            8 * constants.UI_SCALE,
            font_size=font_size
        )

        # Level
        level_text = f":L{self.pokemon.level}"
        renderer.draw_text(
            level_text,
            128 * constants.UI_SCALE,
            8 * constants.UI_SCALE,
            font_size=font_size
        )

        # HP bar + values
        self._draw_hp_bar(
            renderer,
            72 * constants.UI_SCALE,
            24 * constants.UI_SCALE,
            80 * constants.UI_SCALE,
            8 * constants.UI_SCALE,
            font_size
        )
        hp_text = f"{self.pokemon.current_hp:3d}/{self.pokemon.stats.hp:3d}"
        renderer.draw_text(
            hp_text,
            100 * constants.UI_SCALE,
            34 * constants.UI_SCALE,
            font_size=font_size
        )

        # Status
        if self.pokemon.status and self.pokemon.status.name != "NONE":
            status_text = f"STATUS/{self.pokemon.status.name}"
        else:
            status_text = "STATUS/OK"
        renderer.draw_text(
            status_text,
            72 * constants.UI_SCALE,
            48 * constants.UI_SCALE,
            font_size=font_size
        )

        # === BOTTOM SECTION (y=76+) ===

        # Stats on left side
        stats = [
            ("ATTACK", self.pokemon.stats.attack),
            ("DEFENSE", self.pokemon.stats.defense),
            ("SPEED", self.pokemon.stats.speed),
            ("SPECIAL", self.pokemon.stats.special),
        ]

        for i, (stat_name, stat_value) in enumerate(stats):
            y = (76 * constants.UI_SCALE) + (i * (12 * constants.UI_SCALE))
            renderer.draw_text(stat_name, 8 * constants.UI_SCALE, y, font_size=font_size)
            renderer.draw_text(f"{stat_value:3d}", 56 * constants.UI_SCALE, y, font_size=font_size)

        # Type on right side
        for i, poke_type in enumerate(self.pokemon.species.types):
            type_label = f"TYPE{i + 1}/" if len(self.pokemon.species.types) > 1 else "TYPE/"
            type_text = f"{type_label}{poke_type.upper()}"
            renderer.draw_text(
                type_text,
                96 * constants.UI_SCALE,
                (76 * constants.UI_SCALE) + (i * (12 * constants.UI_SCALE)),
                font_size=font_size
            )

        # Page indicator at bottom right
        renderer.draw_text(
            "INFO",
            128 * constants.UI_SCALE,
            128 * constants.UI_SCALE,
            font_size=font_size
        )

    def _draw_hp_bar(
        self,
        renderer,
        x: int,
        y: int,
        width: int,
        height: int,
        font_size: int
    ) -> None:
        """
        Draw HP bar with color based on HP percentage.

        Args:
            renderer: Renderer instance
            x, y: Position
            width, height: Bar dimensions
        """
        # Draw "HP:" label
        renderer.draw_text("HP:", x, y - (2 * constants.UI_SCALE), font_size=font_size)

        bar_x = x + (20 * constants.UI_SCALE)
        bar_width = width - (20 * constants.UI_SCALE)

        # Background (empty bar)
        renderer.draw_rect((200, 200, 200), (bar_x, y, bar_width, height), 0)

        # Calculate HP percentage and color
        hp_percent = self.pokemon.current_hp / self.pokemon.stats.hp if self.pokemon.stats.hp > 0 else 0
        filled_width = int(bar_width * hp_percent)

        # Color based on percentage: green > 50%, yellow 20-50%, red < 20%
        if hp_percent > 0.5:
            color = (0, 200, 0)  # Green
        elif hp_percent > 0.2:
            color = (248, 208, 48)  # Yellow
        else:
            color = (248, 88, 56)  # Red

        # Draw filled portion
        if filled_width > 0:
            renderer.draw_rect(color, (bar_x, y, filled_width, height), 0)

        # Draw border
        renderer.draw_rect((0, 0, 0), (bar_x, y, bar_width, height), 1 * constants.UI_SCALE)

    def _render_moves_page(self, renderer) -> None:
        """
        Render MOVES page matching authentic Pokemon Yellow layout.

        Args:
            renderer: Renderer instance
        """
        renderer.clear((248, 248, 248))
        font_size = 16 * constants.UI_SCALE

        # === HEADER SECTION ===

        # Draw small sprite (32x32) at top-left
        if self.pokemon.species.sprites and self.pokemon.species.sprites.front:
            sprite = renderer.load_sprite(self.pokemon.species.sprites.front)
            if sprite and isinstance(sprite, pygame.Surface):
                sprite_size = 32 * constants.UI_SCALE
                scaled_sprite = pygame.transform.scale(sprite, (sprite_size, sprite_size))
                renderer.game_surface.blit(
                    scaled_sprite,
                    (8 * constants.UI_SCALE, 4 * constants.UI_SCALE)
                )

        # Pokemon name and level
        name_text = self.pokemon.species.name.upper()
        renderer.draw_text(
            name_text,
            48 * constants.UI_SCALE,
            8 * constants.UI_SCALE,
            font_size=font_size
        )
        level_text = f":L{self.pokemon.level}"
        renderer.draw_text(
            level_text,
            120 * constants.UI_SCALE,
            8 * constants.UI_SCALE,
            font_size=font_size
        )

        # === MOVES SECTION ===

        moves_y = 40 * constants.UI_SCALE

        if self.pokemon.moves:
            for i, move_id in enumerate(self.pokemon.moves[:4]):
                y = moves_y + (i * (24 * constants.UI_SCALE))

                # Move name
                move_name = move_id.upper().replace("-", " ")
                renderer.draw_text(move_name, 8 * constants.UI_SCALE, y, font_size=font_size)

                # PP display
                current_pp, max_pp = self.pokemon.get_move_pp(move_id)
                pp_text = f"PP {current_pp:2d}/{max_pp:2d}"
                renderer.draw_text(
                    pp_text,
                    100 * constants.UI_SCALE,
                    y,
                    font_size=font_size
                )
        else:
            renderer.draw_text(
                "No moves",
                8 * constants.UI_SCALE,
                moves_y,
                font_size=font_size
            )

        # Page indicator at bottom right
        renderer.draw_text(
            "MOVES",
            128 * constants.UI_SCALE,
            128 * constants.UI_SCALE,
            font_size=font_size
        )
