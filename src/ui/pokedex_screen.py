# ABOUTME: Pokedex UI component for list and entry screens
# ABOUTME: Renders dex list, entry details, and Yellow-style layout

from typing import Iterable

from src.battle.species import Species
from src.engine.constants import GAME_HEIGHT, GAME_WIDTH


VISIBILITY_UNSEEN = "unseen"
VISIBILITY_SEEN = "seen"
VISIBILITY_CAUGHT = "caught"


def get_species_in_dex_order(species_by_id: dict[str, Species]) -> list[Species]:
    """Return species ordered by National Dex number."""
    return sorted(species_by_id.values(), key=lambda species: species.number)


def get_visibility_state(species_id: str, seen: Iterable[str], caught: Iterable[str]) -> str:
    """Return visibility state for a species based on seen/caught sets."""
    caught_set = set(caught)
    if species_id in caught_set:
        return VISIBILITY_CAUGHT
    if species_id in set(seen):
        return VISIBILITY_SEEN
    return VISIBILITY_UNSEEN


def format_height_feet_inches(height_dm: int) -> str:
    """Format height in decimeters as feet and inches."""
    total_inches = height_dm * 3.93701
    rounded_inches = int(round(total_inches))
    feet = rounded_inches // 12
    inches = rounded_inches % 12
    return f"{feet}'{inches:02d}\""


def format_weight_pounds(weight_hg: int) -> str:
    """Format weight in hectograms as pounds."""
    pounds = weight_hg * 0.220462
    return f"{pounds:.1f}LB."


class PokedexScreen:
    """Pokedex UI component for list and entry rendering."""

    def __init__(
        self,
        species_by_id: dict[str, Species],
        pokedex_seen: Iterable[str],
        pokedex_caught: Iterable[str]
    ):
        self.species_by_id = species_by_id
        self.species_list = get_species_in_dex_order(species_by_id)
        self.pokedex_seen = set(pokedex_seen)
        self.pokedex_caught = set(pokedex_caught)
        self.cursor_index = 0
        self.scroll_offset = 0
        self.mode = "list"
        self.entry_species = None

    def set_pokedex_flags(self, seen: Iterable[str], caught: Iterable[str]) -> None:
        self.pokedex_seen = set(seen)
        self.pokedex_caught = set(caught)

    def move_cursor(self, direction: int) -> None:
        if not self.species_list:
            return
        self.cursor_index = (self.cursor_index + direction) % len(self.species_list)

    def get_selected_species(self) -> Species | None:
        if not self.species_list:
            return None
        if self.cursor_index >= len(self.species_list):
            self.cursor_index = max(0, len(self.species_list) - 1)
        return self.species_list[self.cursor_index]

    def open_entry(self) -> bool:
        species = self.get_selected_species()
        if not species:
            return False
        state = get_visibility_state(species.species_id, self.pokedex_seen, self.pokedex_caught)
        if state == VISIBILITY_UNSEEN:
            return False
        self.mode = "entry"
        self.entry_species = species
        return True

    def close_entry(self) -> None:
        self.mode = "list"
        self.entry_species = None

    def render(self, renderer) -> None:
        if self.mode == "entry":
            self._render_entry(renderer)
        else:
            self._render_list(renderer)

    def _render_list(self, renderer) -> None:
        renderer.clear((248, 248, 248))

        divider_x = 104
        renderer.draw_rect((0, 0, 0), (divider_x, 0, 1, GAME_HEIGHT), 0)

        line_height = 12
        list_top = 8
        list_height = GAME_HEIGHT - list_top
        max_lines = list_height // line_height

        self._adjust_scroll(len(self.species_list), max_lines)

        visible = self.species_list[self.scroll_offset:self.scroll_offset + max_lines]
        for index, species in enumerate(visible):
            y = list_top + (index * line_height)
            list_index = self.scroll_offset + index

            if list_index == self.cursor_index:
                renderer.draw_text("▶", 2, y)

            number_text = f"{species.number:03d}"
            renderer.draw_text(number_text, 12, y)

            state = get_visibility_state(
                species.species_id,
                self.pokedex_seen,
                self.pokedex_caught
            )
            name_text = species.name.upper() if state != VISIBILITY_UNSEEN else "?????"
            renderer.draw_text(name_text, 44, y)

        self._render_right_panel(renderer, divider_x + 6)

    def _render_right_panel(self, renderer, x: int) -> None:
        text_color = (0, 0, 0)
        seen_count = len(self.pokedex_seen | self.pokedex_caught)
        owned_count = len(self.pokedex_caught)

        renderer.draw_text("SEEN", x, 8, text_color, 12)
        renderer.draw_text(f"{seen_count}", x + 4, 20, text_color, 12)
        renderer.draw_text("OWN", x, 36, text_color, 12)
        renderer.draw_text(f"{owned_count}", x + 4, 48, text_color, 12)

        menu_y = 68
        options = ["INFO", "CRY", "AREA", "PRNT", "QUIT"]
        for i, option in enumerate(options):
            renderer.draw_text(option, x, menu_y + (i * 12), text_color, 12)

    def _render_entry(self, renderer) -> None:
        renderer.clear((248, 248, 248))
        species = self.entry_species
        if not species:
            return

        if species.sprites and species.sprites.front:
            try:
                import pygame
            except ImportError:
                pygame = None

            sprite = renderer.load_sprite(species.sprites.front)
            if sprite and pygame:
                scaled_sprite = pygame.transform.scale(sprite, (48, 48))
                renderer.game_surface.blit(scaled_sprite, (8, 24))

        renderer.draw_text(species.name.upper(), 72, 8)

        genus_text = species.genus.upper() if species.genus else "?????"
        renderer.draw_text(genus_text, 72, 24)

        height_text = format_height_feet_inches(species.height)
        renderer.draw_text(f"HT  {height_text}", 72, 40)

        weight_text = format_weight_pounds(species.weight)
        renderer.draw_text(f"WT  {weight_text}", 72, 52)

        renderer.draw_text(f"No.{species.number:03d}", 8, 72)

        entry_lines = self._wrap_text(species.pokedex_entry, max_chars=19)
        for i, line in enumerate(entry_lines[:3]):
            renderer.draw_text(line, 8, 92 + (i * 12))

    def _wrap_text(self, text: str, max_chars: int) -> list[str]:
        lines = []
        words = text.split()
        current_line = []

        for word in words:
            test_line = " ".join(current_line + [word])
            if len(test_line) <= max_chars:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]

        if current_line:
            lines.append(" ".join(current_line))

        return lines

    def _adjust_scroll(self, total_entries: int, max_lines: int) -> None:
        if total_entries <= max_lines:
            self.scroll_offset = 0
            return

        if self.cursor_index < self.scroll_offset:
            self.scroll_offset = self.cursor_index
        elif self.cursor_index >= self.scroll_offset + max_lines:
            self.scroll_offset = self.cursor_index - max_lines + 1
