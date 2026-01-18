# ABOUTME: Pokedex UI component for list and entry screens
# ABOUTME: Renders dex list, entry details, and Yellow-style layout

from typing import Iterable

from src.battle.species import Species
from src.engine import constants


VISIBILITY_UNSEEN = "unseen"
VISIBILITY_SEEN = "seen"
VISIBILITY_CAUGHT = "caught"
FOCUS_LIST = "list"
FOCUS_MENU = "menu"


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


def wrap_text_lines(text: str, max_chars: int) -> list[str]:
    """Wrap text into lines of max_chars length."""
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


def paginate_text(text: str, max_chars: int, max_lines: int) -> list[list[str]]:
    """Paginate wrapped text into pages of max_lines each."""
    lines = wrap_text_lines(text, max_chars)
    pages = []

    for index in range(0, len(lines), max_lines):
        pages.append(lines[index:index + max_lines])

    if not pages:
        pages.append([])

    return pages


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
        self.menu_index = 0
        self.focus = FOCUS_LIST
        self.mode = "list"
        self.entry_species = None
        self.entry_pages = [[]]
        self.entry_page_index = 0
        self.menu_options = ["INFO", "CRY", "AREA", "PRNT", "QUIT"]

    def set_pokedex_flags(self, seen: Iterable[str], caught: Iterable[str]) -> None:
        self.pokedex_seen = set(seen)
        self.pokedex_caught = set(caught)

    def move_cursor(self, direction: int) -> None:
        if self.focus == FOCUS_MENU:
            if not self.menu_options:
                return
            self.menu_index = (self.menu_index + direction) % len(self.menu_options)
            return

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
        self.entry_pages = paginate_text(species.pokedex_entry, max_chars=19, max_lines=3)
        self.entry_page_index = 0
        return True

    def close_entry(self) -> None:
        self.mode = "list"
        self.entry_species = None
        self.entry_page_index = 0

    def render(self, renderer) -> None:
        if self.mode == "entry":
            self._render_entry(renderer)
        else:
            self._render_list(renderer)

    def set_focus(self, focus: str) -> None:
        self.focus = focus

    def get_selected_menu_option(self) -> str:
        if not self.menu_options:
            return "INFO"
        return self.menu_options[self.menu_index]

    def can_advance_page(self) -> bool:
        return self.entry_page_index < len(self.entry_pages) - 1

    def can_go_back_page(self) -> bool:
        return self.entry_page_index > 0

    def advance_page(self) -> None:
        if self.can_advance_page():
            self.entry_page_index += 1

    def go_back_page(self) -> None:
        if self.can_go_back_page():
            self.entry_page_index -= 1

    def _render_list(self, renderer) -> None:
        renderer.clear((248, 248, 248))

        divider_x = 104 * constants.UI_SCALE
        self._render_dotted_divider(renderer, divider_x)

        row_height = 9 * constants.UI_SCALE
        entry_height = row_height * 2
        list_top = 8 * constants.UI_SCALE
        max_entries = 7
        list_height = entry_height * max_entries

        self._adjust_scroll(len(self.species_list), max_entries)

        visible = self.species_list[self.scroll_offset:self.scroll_offset + max_entries]
        for index, species in enumerate(visible):
            base_y = list_top + (index * entry_height)
            list_index = self.scroll_offset + index
            state = get_visibility_state(
                species.species_id,
                self.pokedex_seen,
                self.pokedex_caught
            )

            number_text = f"{species.number:03d}"
            renderer.draw_text(
                number_text,
                6 * constants.UI_SCALE,
                base_y,
                (0, 0, 0),
                11 * constants.UI_SCALE
            )

            name_text = species.name.upper() if state != VISIBILITY_UNSEEN else "?????"
            name_y = base_y + row_height
            if self.focus == FOCUS_LIST and list_index == self.cursor_index:
                renderer.draw_text(
                    "▶",
                    2 * constants.UI_SCALE,
                    name_y,
                    font_size=12 * constants.UI_SCALE
                )

            name_x = 28 * constants.UI_SCALE
            if state == VISIBILITY_CAUGHT:
                renderer.draw_text(
                    "●",
                    12 * constants.UI_SCALE,
                    name_y,
                    (0, 0, 0),
                    10 * constants.UI_SCALE
                )
                renderer.draw_text(
                    name_text,
                    name_x,
                    name_y,
                    (0, 0, 0),
                    11 * constants.UI_SCALE
                )
            else:
                renderer.draw_text(
                    name_text,
                    name_x,
                    name_y,
                    (0, 0, 0),
                    11 * constants.UI_SCALE
                )

        self._render_right_panel(renderer, divider_x + 6)

    def _render_right_panel(self, renderer, x: int) -> None:
        text_color = (0, 0, 0)
        seen_count = len(self.pokedex_seen | self.pokedex_caught)
        owned_count = len(self.pokedex_caught)

        stats_box = (
            divider_x := x - (6 * constants.UI_SCALE),
            0,
            constants.GAME_WIDTH - divider_x,
            52 * constants.UI_SCALE
        )
        menu_box = (
            divider_x,
            56 * constants.UI_SCALE,
            constants.GAME_WIDTH - divider_x,
            88 * constants.UI_SCALE
        )
        self._render_double_box(renderer, stats_box)
        self._render_double_box(renderer, menu_box)

        renderer.draw_text("SEEN", x, 8 * constants.UI_SCALE, text_color, 12 * constants.UI_SCALE)
        renderer.draw_text(
            f"{seen_count}",
            x + (4 * constants.UI_SCALE),
            20 * constants.UI_SCALE,
            text_color,
            10 * constants.UI_SCALE
        )
        renderer.draw_text("OWN", x, 32 * constants.UI_SCALE, text_color, 12 * constants.UI_SCALE)
        renderer.draw_text(
            f"{owned_count}",
            x + (4 * constants.UI_SCALE),
            42 * constants.UI_SCALE,
            text_color,
            10 * constants.UI_SCALE
        )

        menu_y = 64 * constants.UI_SCALE
        for i, option in enumerate(self.menu_options):
            y = menu_y + (i * (12 * constants.UI_SCALE))
            if self.focus == FOCUS_MENU and i == self.menu_index:
                renderer.draw_text(
                    "▶",
                    x - (10 * constants.UI_SCALE),
                    y,
                    text_color,
                    12 * constants.UI_SCALE
                )
            renderer.draw_text(option, x, y, text_color, 12 * constants.UI_SCALE)

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
                sprite_size = 48 * constants.UI_SCALE
                scaled_sprite = pygame.transform.scale(sprite, (sprite_size, sprite_size))
                renderer.game_surface.blit(
                    scaled_sprite,
                    (8 * constants.UI_SCALE, 24 * constants.UI_SCALE)
                )

        renderer.draw_text(
            species.name.upper(),
            72 * constants.UI_SCALE,
            8 * constants.UI_SCALE,
            font_size=16 * constants.UI_SCALE
        )

        genus_text = species.genus.upper() if species.genus else "?????"
        renderer.draw_text(
            genus_text,
            72 * constants.UI_SCALE,
            24 * constants.UI_SCALE,
            font_size=16 * constants.UI_SCALE
        )

        height_text = format_height_feet_inches(species.height)
        renderer.draw_text(
            f"HT  {height_text}",
            72 * constants.UI_SCALE,
            40 * constants.UI_SCALE,
            font_size=16 * constants.UI_SCALE
        )

        weight_text = format_weight_pounds(species.weight)
        renderer.draw_text(
            f"WT  {weight_text}",
            72 * constants.UI_SCALE,
            52 * constants.UI_SCALE,
            font_size=16 * constants.UI_SCALE
        )

        renderer.draw_text(
            f"No.{species.number:03d}",
            8 * constants.UI_SCALE,
            72 * constants.UI_SCALE,
            font_size=16 * constants.UI_SCALE
        )

        entry_lines = self.entry_pages[self.entry_page_index] if self.entry_pages else []
        for i, line in enumerate(entry_lines):
            renderer.draw_text(
                line,
                8 * constants.UI_SCALE,
                (92 * constants.UI_SCALE) + (i * (12 * constants.UI_SCALE)),
                font_size=16 * constants.UI_SCALE
            )

        if len(self.entry_pages) > 1:
            page_text = f"{self.entry_page_index + 1}/{len(self.entry_pages)}"
            renderer.draw_text(
                page_text,
                124 * constants.UI_SCALE,
                128 * constants.UI_SCALE,
                font_size=16 * constants.UI_SCALE
            )
            if self.can_advance_page():
                renderer.draw_text(
                    "▼",
                    146 * constants.UI_SCALE,
                    128 * constants.UI_SCALE,
                    font_size=16 * constants.UI_SCALE
                )

    def _adjust_scroll(self, total_entries: int, max_lines: int) -> None:
        if total_entries <= max_lines:
            self.scroll_offset = 0
            return

        if self.cursor_index < self.scroll_offset:
            self.scroll_offset = self.cursor_index
        elif self.cursor_index >= self.scroll_offset + max_lines:
            self.scroll_offset = self.cursor_index - max_lines + 1

    def _render_double_box(self, renderer, rect: tuple[int, int, int, int]) -> None:
        x, y, width, height = rect
        renderer.draw_rect((0, 0, 0), (x, y, width, height), 1 * constants.UI_SCALE)
        renderer.draw_rect(
            (0, 0, 0),
            (x + (2 * constants.UI_SCALE), y + (2 * constants.UI_SCALE),
             width - (4 * constants.UI_SCALE), height - (4 * constants.UI_SCALE)),
            1 * constants.UI_SCALE
        )

    def _render_dotted_divider(self, renderer, x: int) -> None:
        renderer.draw_rect((0, 0, 0), (x, 0, 1 * constants.UI_SCALE, constants.GAME_HEIGHT), 0)
        step = 10 * constants.UI_SCALE
        for y in range(4 * constants.UI_SCALE, constants.GAME_HEIGHT, step):
            renderer.draw_rect(
                (248, 248, 248),
                (x - (1 * constants.UI_SCALE), y, 3 * constants.UI_SCALE, 2 * constants.UI_SCALE),
                0
            )
