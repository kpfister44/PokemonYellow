# ABOUTME: Summary screen UI component for detailed Pokemon info
# ABOUTME: Renders INFO and MOVES pages with stats, types, and move list

import pygame
from typing import Optional
from src.party.party import Party
from src.battle.pokemon import Pokemon
from src.engine.constants import GAME_WIDTH, GAME_HEIGHT


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
        Render INFO page showing Pokemon stats and types.

        Args:
            renderer: Renderer instance
        """
        surface = renderer.surface
        surface.fill((248, 248, 248))

        # Draw sprite (64x64)
        if self.pokemon.species.sprites and self.pokemon.species.sprites.front:
            sprite = renderer.load_sprite(self.pokemon.species.sprites.front)
            if sprite and isinstance(sprite, pygame.Surface):
                scaled_sprite = pygame.transform.scale(sprite, (64, 64))
                surface.blit(scaled_sprite, (16, 16))

        # Draw name and level
        name_text = self.pokemon.species.name.upper()
        renderer.draw_text(name_text, 96, 16)

        level_text = f"Lv{self.pokemon.level}"
        renderer.draw_text(level_text, 96, 32)

        # Draw types
        y_offset = 48
        for i, poke_type in enumerate(self.pokemon.species.types):
            type_text = f"TYPE/{poke_type.upper()}"
            renderer.draw_text(type_text, 96, y_offset + (i * 16))

        # Draw status condition if present
        if self.pokemon.status and self.pokemon.status.name != "NONE":
            status_text = f"STATUS/{self.pokemon.status.name}"
            renderer.draw_text(status_text, 96, y_offset + (len(self.pokemon.species.types) * 16))

        # Draw stats
        stats_y = 100
        renderer.draw_text("STATS", 16, stats_y)

        stats = [
            ("HP", self.pokemon.stats.hp),
            ("ATK", self.pokemon.stats.attack),
            ("DEF", self.pokemon.stats.defense),
            ("SPECIAL", self.pokemon.stats.special),
            ("SPEED", self.pokemon.stats.speed)
        ]

        for i, (stat_name, stat_value) in enumerate(stats):
            y = stats_y + 16 + (i * 16)
            renderer.draw_text(f"{stat_name:7s} {stat_value:3d}", 16, y)

        # Draw current HP
        hp_text = f"HP {self.pokemon.current_hp:3d}/{self.pokemon.stats.hp:3d}"
        renderer.draw_text(hp_text, 16, stats_y + 16 + (len(stats) * 16))

        # Draw page indicator
        renderer.draw_text("INFO", GAME_WIDTH - 48, GAME_HEIGHT - 16)

    def _render_moves_page(self, renderer) -> None:
        """
        Render MOVES page showing Pokemon move list.

        Args:
            renderer: Renderer instance
        """
        surface = renderer.surface
        surface.fill((248, 248, 248))

        # Draw name and level
        name_text = self.pokemon.species.name.upper()
        renderer.draw_text(name_text, 16, 16)

        level_text = f"Lv{self.pokemon.level}"
        renderer.draw_text(level_text, 120, 16)

        # Draw moves section
        renderer.draw_text("MOVES", 16, 40)

        # Draw move list (max 4 moves)
        moves_y = 60
        if self.pokemon.moves:
            for i, move_id in enumerate(self.pokemon.moves[:4]):
                # Move name
                move_name = move_id.upper().replace("-", " ")
                renderer.draw_text(move_name, 16, moves_y + (i * 32))

                # PP placeholder (will be real in Task 7)
                pp_text = "PP --/--"
                renderer.draw_text(pp_text, 16, moves_y + (i * 32) + 12)

                # Type placeholder (would need move loader for real type)
                type_text = "TYPE ???"
                renderer.draw_text(type_text, 100, moves_y + (i * 32) + 12)
        else:
            renderer.draw_text("No moves learned", 16, moves_y)

        # Draw page indicator
        renderer.draw_text("MOVES", GAME_WIDTH - 48, GAME_HEIGHT - 16)
