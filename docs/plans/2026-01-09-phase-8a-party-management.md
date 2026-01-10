# Phase 8A: Party Management UI - Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement complete party management system with Start Menu, Party Screen, Pokemon Summary, and battle switching.

**Architecture:** State-machine approach with three new states (StartMenuState, PartyState, SummaryState). Party class manages up to 6 Pokemon with add/remove/reorder operations. Integration with existing battle and catching systems.

**Tech Stack:** PyGame 2.6.1, Python 3.13.5, existing state machine pattern

---

## Table of Contents

1. [Task 1: Party Data Structure](#task-1-party-data-structure)
2. [Task 2: Start Menu State](#task-2-start-menu-state)
3. [Task 3: Party Screen State](#task-3-party-screen-state)
4. [Task 4: Pokemon Summary State](#task-4-pokemon-summary-state)
5. [Task 5: Integrate Start Menu with Overworld](#task-5-integrate-start-menu-with-overworld)
6. [Task 6: Party Screen Navigation](#task-6-party-screen-navigation)
7. [Task 7: Summary Screen Details](#task-7-summary-screen-details)
8. [Task 8: Battle Switching Integration](#task-8-battle-switching-integration)
9. [Task 9: Catching Integration](#task-9-catching-integration)
10. [Task 10: Polish and Edge Cases](#task-10-polish-and-edge-cases)

---

## Task 1: Party Data Structure

**Files:**
- Create: `src/party/party.py`
- Create: `tests/test_party.py`

### Step 1: Write failing test for Party initialization

**File:** `tests/test_party.py`

```python
# ABOUTME: Tests for party management system
# ABOUTME: Validates party operations (add, remove, reorder, limits)

import pytest
from src.party.party import Party
from src.battle.pokemon import Pokemon
from src.battle.species_loader import SpeciesLoader


def test_party_initializes_empty():
    """Party should initialize with no Pokemon."""
    party = Party()
    assert len(party.pokemon) == 0
    assert party.size() == 0


def test_party_add_pokemon():
    """Should add Pokemon to party."""
    party = Party()
    species_loader = SpeciesLoader()
    pikachu_species = species_loader.get_species("pikachu")
    pikachu = Pokemon(pikachu_species, 5)

    party.add(pikachu)

    assert party.size() == 1
    assert party.pokemon[0] == pikachu


def test_party_max_size_is_six():
    """Party should not exceed 6 Pokemon."""
    party = Party()
    species_loader = SpeciesLoader()
    pikachu_species = species_loader.get_species("pikachu")

    # Add 6 Pokemon
    for i in range(6):
        party.add(Pokemon(pikachu_species, 5))

    assert party.size() == 6
    assert party.is_full()

    # Try to add 7th
    result = party.add(Pokemon(pikachu_species, 5))
    assert result is False
    assert party.size() == 6


def test_party_get_active_pokemon():
    """First Pokemon in party is active."""
    party = Party()
    species_loader = SpeciesLoader()
    pikachu_species = species_loader.get_species("pikachu")
    pikachu = Pokemon(pikachu_species, 5)

    party.add(pikachu)

    assert party.get_active() == pikachu


def test_party_remove_pokemon():
    """Should remove Pokemon from party."""
    party = Party()
    species_loader = SpeciesLoader()
    pikachu_species = species_loader.get_species("pikachu")
    pikachu = Pokemon(pikachu_species, 5)

    party.add(pikachu)
    party.remove(0)

    assert party.size() == 0


def test_party_swap_pokemon():
    """Should swap positions of two Pokemon."""
    party = Party()
    species_loader = SpeciesLoader()
    pikachu_species = species_loader.get_species("pikachu")
    rattata_species = species_loader.get_species("rattata")

    pikachu = Pokemon(pikachu_species, 5)
    rattata = Pokemon(rattata_species, 3)

    party.add(pikachu)
    party.add(rattata)

    party.swap(0, 1)

    assert party.pokemon[0] == rattata
    assert party.pokemon[1] == pikachu
```

### Step 2: Run test to verify it fails

```bash
uv run pytest tests/test_party.py -v
```

**Expected:** FAIL - Module `src.party.party` not found

### Step 3: Create Party class with minimal implementation

**File:** `src/party/party.py`

```python
# ABOUTME: Party management for up to 6 Pokemon
# ABOUTME: Handles add, remove, swap, and active Pokemon operations

from typing import Optional
from src.battle.pokemon import Pokemon


class Party:
    """Manages player's party of up to 6 Pokemon."""

    MAX_SIZE = 6

    def __init__(self):
        """Initialize empty party."""
        self.pokemon: list[Pokemon] = []

    def size(self) -> int:
        """Return number of Pokemon in party."""
        return len(self.pokemon)

    def is_full(self) -> bool:
        """Check if party is at max capacity."""
        return len(self.pokemon) >= self.MAX_SIZE

    def add(self, pokemon: Pokemon) -> bool:
        """
        Add Pokemon to party.

        Args:
            pokemon: Pokemon to add

        Returns:
            True if added successfully, False if party full
        """
        if self.is_full():
            return False

        self.pokemon.append(pokemon)
        return True

    def remove(self, index: int) -> Optional[Pokemon]:
        """
        Remove Pokemon at index.

        Args:
            index: Position in party (0-5)

        Returns:
            Removed Pokemon, or None if index invalid
        """
        if 0 <= index < len(self.pokemon):
            return self.pokemon.pop(index)
        return None

    def get_active(self) -> Optional[Pokemon]:
        """
        Get active Pokemon (first non-fainted Pokemon).

        Returns:
            Active Pokemon, or None if party empty/all fainted
        """
        for pokemon in self.pokemon:
            if not pokemon.is_fainted():
                return pokemon
        return None

    def swap(self, index1: int, index2: int) -> bool:
        """
        Swap positions of two Pokemon.

        Args:
            index1: First position
            index2: Second position

        Returns:
            True if swapped, False if indices invalid
        """
        if (0 <= index1 < len(self.pokemon) and
            0 <= index2 < len(self.pokemon)):
            self.pokemon[index1], self.pokemon[index2] = (
                self.pokemon[index2], self.pokemon[index1]
            )
            return True
        return False

    def get_all_alive(self) -> list[Pokemon]:
        """Get all non-fainted Pokemon."""
        return [p for p in self.pokemon if not p.is_fainted()]

    def has_alive_pokemon(self) -> bool:
        """Check if party has any non-fainted Pokemon."""
        return any(not p.is_fainted() for p in self.pokemon)
```

### Step 4: Run tests to verify they pass

```bash
uv run pytest tests/test_party.py -v
```

**Expected:** All tests PASS

### Step 5: Commit

```bash
git add src/party/party.py tests/test_party.py
git commit -m "feat(party): add Party data structure with tests"
```

---

## Task 2: Start Menu State

**Files:**
- Create: `src/states/start_menu_state.py`
- Create: `src/ui/start_menu.py`
- Create: `tests/test_start_menu.py`

### Step 1: Write failing test for StartMenu UI component

**File:** `tests/test_start_menu.py`

```python
# ABOUTME: Tests for start menu UI component
# ABOUTME: Validates menu navigation and selection

import pytest
from src.ui.start_menu import StartMenu


def test_start_menu_initializes_with_options():
    """Start menu should have correct options."""
    menu = StartMenu()

    expected_options = [
        "POKéDEX",
        "POKéMON",
        "ITEM",
        "PLAYER",  # Placeholder for player name
        "SAVE",
        "OPTION",
        "EXIT"
    ]

    assert menu.options == expected_options
    assert menu.cursor_index == 0


def test_start_menu_cursor_navigation():
    """Should navigate cursor up and down."""
    menu = StartMenu()

    # Start at 0
    assert menu.cursor_index == 0

    # Move down
    menu.move_cursor(1)
    assert menu.cursor_index == 1

    # Move down to last
    for _ in range(5):
        menu.move_cursor(1)
    assert menu.cursor_index == 6

    # Wrap around to top
    menu.move_cursor(1)
    assert menu.cursor_index == 0

    # Move up wraps to bottom
    menu.move_cursor(-1)
    assert menu.cursor_index == 6


def test_start_menu_get_selection():
    """Should return current selection."""
    menu = StartMenu()

    assert menu.get_selection() == "POKéDEX"

    menu.move_cursor(1)
    assert menu.get_selection() == "POKéMON"

    menu.cursor_index = 6
    assert menu.get_selection() == "EXIT"
```

### Step 2: Run test to verify it fails

```bash
uv run pytest tests/test_start_menu.py -v
```

**Expected:** FAIL - Module not found

### Step 3: Create StartMenu UI component

**File:** `src/ui/start_menu.py`

```python
# ABOUTME: Start menu UI component for main game menu
# ABOUTME: Handles menu rendering and cursor navigation

import pygame
from src.engine.constants import SCREEN_WIDTH, SCREEN_HEIGHT


class StartMenu:
    """Main start menu UI component."""

    def __init__(self, player_name: str = "PLAYER"):
        """
        Initialize start menu.

        Args:
            player_name: Player's name to display
        """
        self.options = [
            "POKéDEX",
            "POKéMON",
            "ITEM",
            player_name,
            "SAVE",
            "OPTION",
            "EXIT"
        ]
        self.cursor_index = 0

    def move_cursor(self, direction: int):
        """
        Move cursor up (-1) or down (1).

        Args:
            direction: -1 for up, 1 for down
        """
        self.cursor_index = (self.cursor_index + direction) % len(self.options)

    def get_selection(self) -> str:
        """Get currently selected option."""
        return self.options[self.cursor_index]

    def render(self, surface: pygame.Surface, renderer):
        """
        Render the start menu.

        Args:
            surface: Surface to render on
            renderer: Renderer instance for drawing
        """
        # Menu box dimensions (right side of screen)
        menu_width = 80
        menu_height = 120
        menu_x = SCREEN_WIDTH - menu_width - 8
        menu_y = 8

        # Draw menu background box
        renderer.draw_box(surface, menu_x, menu_y, menu_width, menu_height)

        # Draw options
        text_x = menu_x + 16
        text_y = menu_y + 8
        line_height = 16

        for i, option in enumerate(self.options):
            y = text_y + (i * line_height)

            # Draw cursor
            if i == self.cursor_index:
                renderer.draw_text(surface, "▶", text_x - 10, y)

            # Draw option text
            renderer.draw_text(surface, option, text_x, y)
```

### Step 4: Run tests to verify they pass

```bash
uv run pytest tests/test_start_menu.py -v
```

**Expected:** All tests PASS

### Step 5: Create StartMenuState

**File:** `src/states/start_menu_state.py`

```python
# ABOUTME: Start menu game state
# ABOUTME: Manages start menu navigation and transitions to other states

import pygame
from src.states.base_state import BaseState
from src.ui.start_menu import StartMenu


class StartMenuState(BaseState):
    """State for main start menu."""

    def __init__(self, game, previous_state):
        """
        Initialize start menu state.

        Args:
            game: Game instance
            previous_state: State to return to (usually OverworldState)
        """
        super().__init__(game)
        self.previous_state = previous_state
        self.menu = StartMenu(player_name="RED")  # TODO: Get from player data

    def handle_input(self, input_handler):
        """Handle menu input."""
        if input_handler.is_just_pressed("down"):
            self.menu.move_cursor(1)

        elif input_handler.is_just_pressed("up"):
            self.menu.move_cursor(-1)

        elif input_handler.is_just_pressed("a"):
            # Handle selection
            selection = self.menu.get_selection()
            self._handle_selection(selection)

        elif input_handler.is_just_pressed("b"):
            # Close menu (return to previous state)
            self.game.pop_state()

    def _handle_selection(self, selection: str):
        """
        Handle menu selection.

        Args:
            selection: Selected menu option
        """
        if selection == "POKéMON":
            from src.states.party_state import PartyState
            party_state = PartyState(self.game, self.previous_state.party)
            self.game.push_state(party_state)

        elif selection == "EXIT":
            # Close menu
            self.game.pop_state()

        elif selection == "POKéDEX":
            # TODO: Implement in future phase
            pass

        elif selection == "ITEM":
            # TODO: Implement in Phase 8B
            pass

        elif selection == "SAVE":
            # TODO: Implement in Phase 8C
            pass

        elif selection == "OPTION":
            # TODO: Implement in future phase
            pass

    def update(self, dt: float):
        """Update menu state (nothing to update)."""
        pass

    def render(self, surface: pygame.Surface):
        """
        Render start menu over previous state.

        Args:
            surface: Surface to render on
        """
        # Render previous state (overworld) first
        if self.previous_state:
            self.previous_state.render(surface)

        # Render menu on top
        self.menu.render(surface, self.game.renderer)
```

### Step 6: Test imports

```bash
uv run python -c "from src.states.start_menu_state import StartMenuState; print('✓ StartMenuState OK')"
```

**Expected:** ✓ StartMenuState OK

### Step 7: Commit

```bash
git add src/states/start_menu_state.py src/ui/start_menu.py tests/test_start_menu.py
git commit -m "feat(menu): add start menu UI and state"
```

---

## Task 3: Party Screen State

**Files:**
- Create: `src/states/party_state.py`
- Create: `src/ui/party_screen.py`
- Create: `tests/test_party_screen.py`

### Step 1: Write failing test for PartyScreen UI component

**File:** `tests/test_party_screen.py`

```python
# ABOUTME: Tests for party screen UI component
# ABOUTME: Validates party list rendering and navigation

import pytest
from src.ui.party_screen import PartyScreen
from src.party.party import Party
from src.battle.pokemon import Pokemon
from src.battle.species_loader import SpeciesLoader


def test_party_screen_initializes():
    """Party screen should initialize with party."""
    party = Party()
    screen = PartyScreen(party)

    assert screen.party == party
    assert screen.cursor_index == 0


def test_party_screen_cursor_navigation():
    """Should navigate cursor through party."""
    party = Party()
    species_loader = SpeciesLoader()

    # Add 3 Pokemon
    for species_id in ["pikachu", "rattata", "squirtle"]:
        species = species_loader.get_species(species_id)
        party.add(Pokemon(species, 5))

    screen = PartyScreen(party)

    # Navigate down
    screen.move_cursor(1)
    assert screen.cursor_index == 1

    screen.move_cursor(1)
    assert screen.cursor_index == 2

    # At last Pokemon, wrap to first
    screen.move_cursor(1)
    assert screen.cursor_index == 0

    # Navigate up wraps to last
    screen.move_cursor(-1)
    assert screen.cursor_index == 2


def test_party_screen_get_selected_pokemon():
    """Should return selected Pokemon."""
    party = Party()
    species_loader = SpeciesLoader()
    pikachu_species = species_loader.get_species("pikachu")
    pikachu = Pokemon(pikachu_species, 5)

    party.add(pikachu)
    screen = PartyScreen(party)

    assert screen.get_selected_pokemon() == pikachu
```

### Step 2: Run test to verify it fails

```bash
uv run pytest tests/test_party_screen.py -v
```

**Expected:** FAIL - Module not found

### Step 3: Create PartyScreen UI component

**File:** `src/ui/party_screen.py`

```python
# ABOUTME: Party screen UI component for Pokemon list view
# ABOUTME: Renders party Pokemon with sprites, names, levels, and HP

import pygame
from typing import Optional
from src.party.party import Party
from src.battle.pokemon import Pokemon
from src.engine.constants import SCREEN_WIDTH, SCREEN_HEIGHT


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
        """Get currently selected Pokemon."""
        if 0 <= self.cursor_index < self.party.size():
            return self.party.pokemon[self.cursor_index]
        return None

    def render(self, surface: pygame.Surface, renderer):
        """
        Render the party screen.

        Args:
            surface: Surface to render on
            renderer: Renderer instance for drawing
        """
        # Clear screen with white background
        surface.fill((248, 248, 248))

        # Draw each Pokemon in party
        for i in range(min(6, self.party.size())):
            self._render_party_slot(surface, renderer, i)

        # Draw prompt text at bottom
        prompt_y = SCREEN_HEIGHT - 24
        renderer.draw_box(surface, 0, prompt_y, SCREEN_WIDTH, 24)
        renderer.draw_text(surface, "Choose a POKéMON.", 8, prompt_y + 8)

    def _render_party_slot(self, surface: pygame.Surface, renderer, index: int):
        """
        Render a single party slot.

        Args:
            surface: Surface to render on
            renderer: Renderer instance
            index: Party slot index (0-5)
        """
        pokemon = self.party.pokemon[index]

        # Calculate position (2 rows of 3)
        slot_width = SCREEN_WIDTH // 2
        slot_height = 40
        x = (index % 2) * slot_width
        y = (index // 2) * slot_height + 8

        # Draw selection cursor
        if index == self.cursor_index:
            renderer.draw_text(surface, "▶", x + 4, y + 12)

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
        renderer.draw_text(surface, name_text, info_x, y + 4)

        level_text = f"Lv{pokemon.level}"
        renderer.draw_text(surface, level_text, info_x + 60, y + 4)

        # HP
        hp_text = f"{pokemon.current_hp:3d}/{pokemon.stats.hp:3d}"
        renderer.draw_text(surface, hp_text, info_x, y + 20)

        # Status condition (if any)
        if pokemon.status and pokemon.status.name != "NONE":
            status_text = pokemon.status.name[:3]  # e.g., "PAR", "BRN"
            renderer.draw_text(surface, status_text, info_x + 60, y + 20)
```

### Step 4: Run tests to verify they pass

```bash
uv run pytest tests/test_party_screen.py -v
```

**Expected:** All tests PASS

### Step 5: Create PartyState

**File:** `src/states/party_state.py`

```python
# ABOUTME: Party screen game state
# ABOUTME: Manages party list navigation and transitions to summary

import pygame
from src.states.base_state import BaseState
from src.ui.party_screen import PartyScreen
from src.party.party import Party


class PartyState(BaseState):
    """State for party screen."""

    def __init__(self, game, party: Party, mode: str = "view"):
        """
        Initialize party state.

        Args:
            game: Game instance
            party: Party to display
            mode: "view" (default) or "switch" (for battle switching)
        """
        super().__init__(game)
        self.party = party
        self.mode = mode
        self.screen = PartyScreen(party)

    def handle_input(self, input_handler):
        """Handle party screen input."""
        if input_handler.is_just_pressed("down"):
            self.screen.move_cursor(1)

        elif input_handler.is_just_pressed("up"):
            self.screen.move_cursor(-1)

        elif input_handler.is_just_pressed("a"):
            # Select Pokemon - open summary
            selected = self.screen.get_selected_pokemon()
            if selected:
                from src.states.summary_state import SummaryState
                summary_state = SummaryState(self.game, selected, self.party)
                self.game.push_state(summary_state)

        elif input_handler.is_just_pressed("b"):
            # Go back
            self.game.pop_state()

    def update(self, dt: float):
        """Update party state (nothing to update)."""
        pass

    def render(self, surface: pygame.Surface):
        """
        Render party screen.

        Args:
            surface: Surface to render on
        """
        self.screen.render(surface, self.game.renderer)
```

### Step 6: Test imports

```bash
uv run python -c "from src.states.party_state import PartyState; print('✓ PartyState OK')"
```

**Expected:** ✓ PartyState OK

### Step 7: Commit

```bash
git add src/states/party_state.py src/ui/party_screen.py tests/test_party_screen.py
git commit -m "feat(party): add party screen UI and state"
```

---

## Task 4: Pokemon Summary State

**Files:**
- Create: `src/states/summary_state.py`
- Create: `src/ui/summary_screen.py`
- Create: `tests/test_summary_screen.py`

### Step 1: Write failing test for SummaryScreen UI component

**File:** `tests/test_summary_screen.py`

```python
# ABOUTME: Tests for Pokemon summary screen UI component
# ABOUTME: Validates summary rendering and navigation

import pytest
from src.ui.summary_screen import SummaryScreen
from src.battle.pokemon import Pokemon
from src.battle.species_loader import SpeciesLoader
from src.party.party import Party


def test_summary_screen_initializes():
    """Summary screen should initialize with Pokemon."""
    species_loader = SpeciesLoader()
    pikachu_species = species_loader.get_species("pikachu")
    pikachu = Pokemon(pikachu_species, 5)

    party = Party()
    party.add(pikachu)

    screen = SummaryScreen(pikachu, party)

    assert screen.pokemon == pikachu
    assert screen.party == party
    assert screen.current_page == 0


def test_summary_screen_page_navigation():
    """Should navigate between summary pages."""
    species_loader = SpeciesLoader()
    pikachu_species = species_loader.get_species("pikachu")
    pikachu = Pokemon(pikachu_species, 5)

    party = Party()
    party.add(pikachu)

    screen = SummaryScreen(pikachu, party)

    # Navigate to next page
    screen.change_page(1)
    assert screen.current_page == 1

    # Navigate to previous page
    screen.change_page(-1)
    assert screen.current_page == 0

    # Wrap around at edges
    screen.change_page(-1)
    assert screen.current_page == 1  # Assuming 2 pages


def test_summary_screen_pokemon_navigation():
    """Should navigate between Pokemon in party."""
    species_loader = SpeciesLoader()
    party = Party()

    # Add 3 Pokemon
    pikachu_species = species_loader.get_species("pikachu")
    rattata_species = species_loader.get_species("rattata")
    squirtle_species = species_loader.get_species("squirtle")

    pikachu = Pokemon(pikachu_species, 5)
    rattata = Pokemon(rattata_species, 3)
    squirtle = Pokemon(squirtle_species, 5)

    party.add(pikachu)
    party.add(rattata)
    party.add(squirtle)

    screen = SummaryScreen(pikachu, party)

    # Navigate to next Pokemon
    screen.change_pokemon(1)
    assert screen.pokemon == rattata

    # Navigate to next Pokemon
    screen.change_pokemon(1)
    assert screen.pokemon == squirtle

    # Wrap to first
    screen.change_pokemon(1)
    assert screen.pokemon == pikachu

    # Navigate backwards
    screen.change_pokemon(-1)
    assert screen.pokemon == squirtle
```

### Step 2: Run test to verify it fails

```bash
uv run pytest tests/test_summary_screen.py -v
```

**Expected:** FAIL - Module not found

### Step 3: Create SummaryScreen UI component

**File:** `src/ui/summary_screen.py`

```python
# ABOUTME: Pokemon summary screen UI component
# ABOUTME: Displays detailed Pokemon info including stats, moves, and status

import pygame
from src.battle.pokemon import Pokemon
from src.party.party import Party
from src.engine.constants import SCREEN_WIDTH, SCREEN_HEIGHT


class SummaryScreen:
    """Pokemon summary screen showing detailed info."""

    def __init__(self, pokemon: Pokemon, party: Party):
        """
        Initialize summary screen.

        Args:
            pokemon: Pokemon to display
            party: Full party (for navigation between Pokemon)
        """
        self.pokemon = pokemon
        self.party = party
        self.current_page = 0  # 0 = INFO, 1 = MOVES
        self.num_pages = 2

        # Find current Pokemon index in party
        self.party_index = 0
        for i, p in enumerate(party.pokemon):
            if p == pokemon:
                self.party_index = i
                break

    def change_page(self, direction: int):
        """
        Change summary page.

        Args:
            direction: -1 for previous, 1 for next
        """
        self.current_page = (self.current_page + direction) % self.num_pages

    def change_pokemon(self, direction: int):
        """
        Switch to next/previous Pokemon in party.

        Args:
            direction: -1 for previous, 1 for next
        """
        self.party_index = (self.party_index + direction) % self.party.size()
        self.pokemon = self.party.pokemon[self.party_index]

    def render(self, surface: pygame.Surface, renderer):
        """
        Render the summary screen.

        Args:
            surface: Surface to render on
            renderer: Renderer instance for drawing
        """
        # Clear screen
        surface.fill((248, 248, 248))

        if self.current_page == 0:
            self._render_info_page(surface, renderer)
        elif self.current_page == 1:
            self._render_moves_page(surface, renderer)

    def _render_info_page(self, surface: pygame.Surface, renderer):
        """Render INFO page (stats, type, status)."""
        # Draw Pokemon sprite (larger)
        if self.pokemon.species.sprites and self.pokemon.species.sprites.front:
            sprite = renderer.load_sprite(self.pokemon.species.sprites.front)
            if sprite:
                scaled_sprite = pygame.transform.scale(sprite, (64, 64))
                surface.blit(scaled_sprite, (8, 8))

        # Pokemon name and level
        name_text = f"{self.pokemon.species.name.upper()}"
        renderer.draw_text(surface, name_text, 80, 12)

        level_text = f"Lv{self.pokemon.level}"
        renderer.draw_text(surface, level_text, 80, 28)

        # Type(s)
        types_text = "/".join(self.pokemon.species.types).upper()
        renderer.draw_text(surface, f"TYPE/{types_text}", 8, 80)

        # Status
        status_text = self.pokemon.status.name if self.pokemon.status else "OK"
        renderer.draw_text(surface, f"STATUS/{status_text}", 8, 96)

        # Stats
        stats_y = 112
        renderer.draw_text(surface, "STATS", 8, stats_y)

        stats_data = [
            ("HP", self.pokemon.stats.hp),
            ("ATTACK", self.pokemon.stats.attack),
            ("DEFENSE", self.pokemon.stats.defense),
            ("SPECIAL", self.pokemon.stats.special),
            ("SPEED", self.pokemon.stats.speed)
        ]

        for i, (stat_name, stat_value) in enumerate(stats_data):
            y = stats_y + 16 + (i * 12)
            renderer.draw_text(surface, f"{stat_name}:", 16, y)
            renderer.draw_text(surface, f"{stat_value:3d}", 100, y)

        # Current HP
        hp_text = f"HP: {self.pokemon.current_hp}/{self.pokemon.stats.hp}"
        renderer.draw_text(surface, hp_text, 8, 44)

        # Page indicator
        renderer.draw_text(surface, "INFO", 8, SCREEN_HEIGHT - 16)

    def _render_moves_page(self, surface: pygame.Surface, renderer):
        """Render MOVES page (move list with PP)."""
        # Pokemon name header
        name_text = f"{self.pokemon.species.name.upper()}"
        renderer.draw_text(surface, name_text, 8, 8)

        # Moves title
        renderer.draw_text(surface, "MOVES", 8, 28)

        # Draw each move
        from src.battle.move_loader import MoveLoader
        move_loader = MoveLoader()

        for i, move_id in enumerate(self.pokemon.moves):
            if i >= 4:  # Max 4 moves
                break

            move = move_loader.get_move(move_id)
            y = 44 + (i * 20)

            # Move name
            renderer.draw_text(surface, move.name.upper(), 16, y)

            # PP (not implemented yet, show placeholder)
            pp_text = f"PP --/--"
            renderer.draw_text(surface, pp_text, 16, y + 10)

            # Type
            type_text = f"TYPE/{move.type.upper()}"
            renderer.draw_text(surface, type_text, 100, y + 10)

        # If no moves
        if len(self.pokemon.moves) == 0:
            renderer.draw_text(surface, "No moves learned", 16, 44)

        # Page indicator
        renderer.draw_text(surface, "MOVES", 8, SCREEN_HEIGHT - 16)
```

### Step 4: Run tests to verify they pass

```bash
uv run pytest tests/test_summary_screen.py -v
```

**Expected:** All tests PASS

### Step 5: Create SummaryState

**File:** `src/states/summary_state.py`

```python
# ABOUTME: Pokemon summary game state
# ABOUTME: Manages summary screen navigation and page switching

import pygame
from src.states.base_state import BaseState
from src.ui.summary_screen import SummaryScreen
from src.battle.pokemon import Pokemon
from src.party.party import Party


class SummaryState(BaseState):
    """State for Pokemon summary screen."""

    def __init__(self, game, pokemon: Pokemon, party: Party):
        """
        Initialize summary state.

        Args:
            game: Game instance
            pokemon: Pokemon to display
            party: Full party for navigation
        """
        super().__init__(game)
        self.screen = SummaryScreen(pokemon, party)

    def handle_input(self, input_handler):
        """Handle summary screen input."""
        if input_handler.is_just_pressed("left"):
            # Previous page
            self.screen.change_page(-1)

        elif input_handler.is_just_pressed("right"):
            # Next page
            self.screen.change_page(1)

        elif input_handler.is_just_pressed("up"):
            # Previous Pokemon in party
            self.screen.change_pokemon(-1)

        elif input_handler.is_just_pressed("down"):
            # Next Pokemon in party
            self.screen.change_pokemon(1)

        elif input_handler.is_just_pressed("b") or input_handler.is_just_pressed("a"):
            # Go back to party screen
            self.game.pop_state()

    def update(self, dt: float):
        """Update summary state (nothing to update)."""
        pass

    def render(self, surface: pygame.Surface):
        """
        Render summary screen.

        Args:
            surface: Surface to render on
        """
        self.screen.render(surface, self.game.renderer)
```

### Step 6: Test imports

```bash
uv run python -c "from src.states.summary_state import SummaryState; print('✓ SummaryState OK')"
```

**Expected:** ✓ SummaryState OK

### Step 7: Commit

```bash
git add src/states/summary_state.py src/ui/summary_screen.py tests/test_summary_screen.py
git commit -m "feat(party): add Pokemon summary screen and state"
```

---

## Task 5: Integrate Start Menu with Overworld

**Files:**
- Modify: `src/states/overworld_state.py`
- Modify: `src/engine/input.py`

### Step 1: Add 'S' key to input handler

**File:** `src/engine/input.py`

Find the `KEY_MAP` and add:

```python
KEY_MAP = {
    # ... existing keys ...
    pygame.K_s: "start",
}
```

### Step 2: Add party field to OverworldState

**File:** `src/states/overworld_state.py`

In `__init__`, add:

```python
# Initialize party with starter Pokemon (Pikachu for Yellow)
from src.party.party import Party
self.party = Party()

# Add starter Pokemon
if not hasattr(self, 'player_pokemon'):
    # Create Pikachu starter
    from src.battle.species_loader import SpeciesLoader
    from src.battle.pokemon import Pokemon
    species_loader = SpeciesLoader()
    pikachu_species = species_loader.get_species("pikachu")
    self.player_pokemon = Pokemon(pikachu_species, 5)

self.party.add(self.player_pokemon)
```

### Step 3: Add start menu input handling

**File:** `src/states/overworld_state.py`

In `handle_input` method, add:

```python
def handle_input(self, input_handler):
    """Handle overworld input."""
    # Open start menu
    if input_handler.is_just_pressed("start"):
        from src.states.start_menu_state import StartMenuState
        start_menu = StartMenuState(self.game, self)
        self.game.push_state(start_menu)
        return

    # ... rest of existing input handling ...
```

### Step 4: Test in-game

```bash
uv run python -m src.main
```

**Expected:**
- Game starts in Pallet Town
- Press 'S' key
- Start menu appears on right side
- Can navigate with arrow keys
- Selecting POKéMON opens party screen
- Party screen shows Pikachu starter
- Can press 'B' to close menus

### Step 5: Commit

```bash
git add src/states/overworld_state.py src/engine/input.py
git commit -m "feat(menu): integrate start menu with overworld"
```

---

## Task 6: Party Screen Navigation

**Files:**
- Modify: `src/ui/party_screen.py`
- Modify: `src/engine/renderer.py`

### Step 1: Add draw_box method to Renderer

**File:** `src/engine/renderer.py`

Add method:

```python
def draw_box(self, surface: pygame.Surface, x: int, y: int, width: int, height: int,
             bg_color: tuple = (248, 248, 248), border_color: tuple = (0, 0, 0)):
    """
    Draw a bordered box.

    Args:
        surface: Surface to draw on
        x, y: Top-left corner
        width, height: Box dimensions
        bg_color: Background color (default white)
        border_color: Border color (default black)
    """
    # Draw background
    pygame.draw.rect(surface, bg_color, (x, y, width, height))

    # Draw border
    pygame.draw.rect(surface, border_color, (x, y, width, height), 2)
```

### Step 2: Update party screen to use proper layout

**File:** `src/ui/party_screen.py`

Update `_render_party_slot` method to match Gen 1 layout (vertical list, not grid):

```python
def _render_party_slot(self, surface: pygame.Surface, renderer, index: int):
    """
    Render a single party slot.

    Args:
        surface: Surface to render on
        renderer: Renderer instance
        index: Party slot index (0-5)
    """
    pokemon = self.party.pokemon[index]

    # Vertical list layout
    slot_height = 22
    y = 8 + (index * slot_height)
    x = 8

    # Draw selection cursor
    if index == self.cursor_index:
        renderer.draw_text(surface, "▶", x, y + 4)

    # Draw Pokemon sprite (small)
    if pokemon.species.sprites and pokemon.species.sprites.front:
        sprite = renderer.load_sprite(pokemon.species.sprites.front)
        if sprite:
            # Scale sprite to 16x16
            scaled_sprite = pygame.transform.scale(sprite, (16, 16))
            surface.blit(scaled_sprite, (x + 12, y))

    # Draw Pokemon info
    info_x = x + 32

    # Name and level
    name_text = f"{pokemon.species.name.upper()}"
    renderer.draw_text(surface, name_text, info_x, y + 2)

    # Level on same line
    level_text = f"Lv{pokemon.level:>3d}"
    renderer.draw_text(surface, level_text, info_x + 60, y + 2)

    # HP on second line
    hp_text = f"{pokemon.current_hp:3d}/{pokemon.stats.hp:3d}"
    renderer.draw_text(surface, hp_text, info_x + 80, y + 10)
```

### Step 3: Test in-game

```bash
uv run python -m src.main
```

**Expected:**
- Start menu opens
- Party screen shows vertical list of Pokemon
- Cursor navigates properly
- Layout matches Gen 1 style

### Step 4: Commit

```bash
git add src/ui/party_screen.py src/engine/renderer.py
git commit -m "feat(party): improve party screen layout to match Gen 1"
```

---

## Task 7: Summary Screen Details

**Files:**
- Modify: `src/ui/summary_screen.py`
- Modify: `src/battle/pokemon.py`

### Step 1: Add PP tracking to Pokemon

**File:** `src/battle/pokemon.py`

Add field in `__init__`:

```python
# PP tracking for moves (current PP / max PP)
self.move_pp: dict[str, tuple[int, int]] = {}  # move_id -> (current, max)
self._initialize_move_pp()
```

Add method:

```python
def _initialize_move_pp(self):
    """Initialize PP for all moves."""
    from src.battle.move_loader import MoveLoader
    move_loader = MoveLoader()

    for move_id in self.moves:
        move = move_loader.get_move(move_id)
        max_pp = move.pp
        self.move_pp[move_id] = (max_pp, max_pp)  # (current, max)

def use_move_pp(self, move_id: str) -> bool:
    """
    Deduct 1 PP from move.

    Args:
        move_id: Move to deduct PP from

    Returns:
        True if PP deducted, False if no PP left
    """
    if move_id in self.move_pp:
        current_pp, max_pp = self.move_pp[move_id]
        if current_pp > 0:
            self.move_pp[move_id] = (current_pp - 1, max_pp)
            return True
    return False

def get_move_pp(self, move_id: str) -> tuple[int, int]:
    """
    Get current and max PP for move.

    Args:
        move_id: Move ID

    Returns:
        Tuple of (current_pp, max_pp)
    """
    return self.move_pp.get(move_id, (0, 0))
```

### Step 2: Update summary screen to show real PP

**File:** `src/ui/summary_screen.py`

Update `_render_moves_page` method:

```python
def _render_moves_page(self, surface: pygame.Surface, renderer):
    """Render MOVES page (move list with PP)."""
    # Pokemon name header
    name_text = f"{self.pokemon.species.name.upper()}"
    renderer.draw_text(surface, name_text, 8, 8)

    # Moves title
    renderer.draw_text(surface, "MOVES", 8, 28)

    # Draw each move
    from src.battle.move_loader import MoveLoader
    move_loader = MoveLoader()

    for i, move_id in enumerate(self.pokemon.moves):
        if i >= 4:  # Max 4 moves
            break

        move = move_loader.get_move(move_id)
        y = 44 + (i * 24)

        # Move name
        renderer.draw_text(surface, move.name.upper(), 16, y)

        # PP (show real PP now)
        current_pp, max_pp = self.pokemon.get_move_pp(move_id)
        pp_text = f"PP {current_pp:2d}/{max_pp:2d}"
        renderer.draw_text(surface, pp_text, 16, y + 12)

        # Type
        type_text = f"TYPE/{move.type.upper()}"
        renderer.draw_text(surface, type_text, 90, y + 6)

        # Power (if applicable)
        if move.power:
            power_text = f"PWR/{move.power}"
            renderer.draw_text(surface, power_text, 90, y + 16)

    # If no moves
    if len(self.pokemon.moves) == 0:
        renderer.draw_text(surface, "No moves learned", 16, 44)

    # Page indicator
    renderer.draw_text(surface, "< MOVES >", SCREEN_WIDTH // 2 - 32, SCREEN_HEIGHT - 16)
```

### Step 3: Update BattleState to use PP tracking

**File:** `src/states/battle_state.py`

In `_execute_player_attack` method, after move selection:

```python
# Deduct PP
if not self.player_pokemon.use_move_pp(move.move_id):
    self._queue_message("No PP left!")
    self._show_next_message()
    return
```

### Step 4: Test PP deduction

```bash
uv run python -m src.main
```

**Expected:**
- Use moves in battle, PP decreases
- Summary screen shows correct PP values
- When PP reaches 0, see "No PP left!" message

### Step 5: Commit

```bash
git add src/battle/pokemon.py src/ui/summary_screen.py src/states/battle_state.py
git commit -m "feat(party): add PP tracking and display in summary"
```

---

## Task 8: Battle Switching Integration

**Files:**
- Modify: `src/states/battle_state.py`
- Modify: `src/states/party_state.py`

### Step 1: Add switching mode to PartyState

**File:** `src/states/party_state.py`

Update `handle_input` method:

```python
def handle_input(self, input_handler):
    """Handle party screen input."""
    if input_handler.is_just_pressed("down"):
        self.screen.move_cursor(1)

    elif input_handler.is_just_pressed("up"):
        self.screen.move_cursor(-1)

    elif input_handler.is_just_pressed("a"):
        selected = self.screen.get_selected_pokemon()

        if self.mode == "switch":
            # Battle switching mode
            if selected and not selected.is_fainted():
                # Return selected Pokemon to battle state
                self.game.pop_state()  # Close party screen

                # Notify battle state of switch
                # Battle state will handle the switch
                from src.states.battle_state import BattleState
                battle_state = self.game.state_stack[-1]
                if isinstance(battle_state, BattleState):
                    battle_state.handle_switch(selected)
            else:
                # Can't switch to fainted Pokemon
                # TODO: Show error message
                pass
        else:
            # View mode - open summary
            if selected:
                from src.states.summary_state import SummaryState
                summary_state = SummaryState(self.game, selected, self.party)
                self.game.push_state(summary_state)

    elif input_handler.is_just_pressed("b"):
        # Go back
        self.game.pop_state()
```

### Step 2: Update BattleState to handle PKM button

**File:** `src/states/battle_state.py`

Update `_handle_battle_menu_selection` method:

```python
def _handle_battle_menu_selection(self, selection: str):
    """Handle battle menu selection."""
    if selection == "FIGHT":
        # ... existing FIGHT code ...
        pass

    elif selection == "ITEM":
        # ... existing ITEM code ...
        pass

    elif selection == "PKM":
        # Open party screen in switch mode
        if hasattr(self, 'party'):
            from src.states.party_state import PartyState
            party_state = PartyState(self.game, self.party, mode="switch")
            self.game.push_state(party_state)
        else:
            self._queue_message("Party not\\nimplemented yet!")
            self._show_next_message()

    elif selection == "RUN":
        # ... existing RUN code ...
        pass
```

### Step 3: Add switch handling to BattleState

**File:** `src/states/battle_state.py`

Add method:

```python
def handle_switch(self, new_pokemon: Pokemon):
    """
    Handle switching to a new Pokemon.

    Args:
        new_pokemon: Pokemon to switch to
    """
    # Can't switch to already active Pokemon
    if new_pokemon == self.player_pokemon:
        self._queue_message(f"{new_pokemon.species.name.upper()} is\\nalready out!")
        self._show_next_message()
        self.battle_menu.activate()
        self.phase = "battle_menu"
        return

    # Switch Pokemon
    old_pokemon = self.player_pokemon
    self.player_pokemon = new_pokemon

    # Update sprite
    if new_pokemon.species.sprites and new_pokemon.species.sprites.back:
        self.player_sprite = self.game.renderer.load_sprite(
            new_pokemon.species.sprites.back
        )

    # Queue switch messages
    self._queue_message(f"{old_pokemon.species.name.upper()},\\ncome back!")
    self._queue_message(f"Go! {new_pokemon.species.name.upper()}!")

    # Switching uses a turn, so enemy attacks after
    self.phase = "enemy_turn"
    self._show_next_message()
```

### Step 4: Pass party to BattleState

**File:** `src/states/overworld_state.py`

Update battle trigger code to pass party:

```python
# In _trigger_wild_encounter method
battle_state = BattleState(
    self.game,
    self.player_pokemon,
    wild_pokemon,
    is_trainer_battle=False
)

# Add party reference
battle_state.party = self.party

self.game.push_state(battle_state)
```

Also update trainer battle code:

```python
# In _check_npc_interaction method (trainer battle section)
battle_state = BattleState(
    self.game,
    self.player_pokemon,
    trainer_party[0],
    is_trainer_battle=True,
    trainer=trainer,
    trainer_pokemon_remaining=trainer_party[1:]
)

# Add party reference
battle_state.party = self.party

self.game.push_state(battle_state)
```

### Step 5: Test battle switching

```bash
uv run python -m src.main
```

**Expected:**
- In battle, select PKM button
- Party screen opens
- Select different Pokemon
- See switch messages
- Enemy attacks after switch
- HP bars update for new Pokemon

### Step 6: Commit

```bash
git add src/states/battle_state.py src/states/party_state.py src/states/overworld_state.py
git commit -m "feat(battle): add Pokemon switching during battle"
```

---

## Task 9: Catching Integration

**Files:**
- Modify: `src/states/battle_state.py`

### Step 1: Update catching to add to party

**File:** `src/states/battle_state.py`

Update `_attempt_catch` method (or create if using RUN placeholder):

```python
def _attempt_catch(self):
    """Attempt to catch wild Pokemon."""
    from src.battle.catch_calculator import CatchCalculator

    self.phase = "throwing_ball"
    self._queue_message("Used POKE BALL!")

    calc = CatchCalculator()
    caught, shakes = calc.calculate_catch_chance(self.enemy_pokemon, ball_bonus=1)

    # Show shake messages
    for i in range(shakes):
        self._queue_message("...")

    if caught:
        self._queue_message(f"Gotcha!\\n{self.enemy_pokemon.species.name.upper()} was caught!")

        # Add to party
        if hasattr(self, 'party'):
            if not self.party.is_full():
                self.party.add(self.enemy_pokemon)

                # Show added message
                self._queue_message(f"{self.enemy_pokemon.species.name.upper()} was\\nadded to party!")
            else:
                # Party full - no PC yet
                self._queue_message("Party is full!\\n(PC not implemented)")

        self.phase = "end"
    else:
        self._queue_message(f"{self.enemy_pokemon.species.name.upper()}\\nbroke free!")
        # Continue to enemy turn
        self.phase = "enemy_turn"

    self._show_next_message()
```

### Step 2: Wire RUN button to catching (temporary)

**File:** `src/states/battle_state.py`

In `_handle_battle_menu_selection`, update RUN handling:

```python
elif selection == "RUN":
    if self.is_trainer_battle:
        self._queue_message("Can't run from a\\ntrainer battle!")
        self._show_next_message()
        self.battle_menu.activate()
        self.phase = "battle_menu"
    else:
        # TODO: Phase 8B - Replace with ITEM -> BALL flow
        # For now, RUN triggers catch attempt
        self._attempt_catch()
```

### Step 3: Test catching

```bash
uv run python -m src.main
```

**Expected:**
- Encounter wild Pokemon
- Select RUN (placeholder for catching)
- See "Used POKE BALL!" and shake messages
- If caught, Pokemon added to party
- Open party screen, see new Pokemon

### Step 4: Commit

```bash
git add src/states/battle_state.py
git commit -m "feat(battle): integrate catching with party system"
```

---

## Task 10: Polish and Edge Cases

**Files:**
- Modify: `src/states/party_state.py`
- Modify: `src/states/battle_state.py`
- Modify: `src/ui/party_screen.py`

### Step 1: Add fainted Pokemon visual indicator

**File:** `src/ui/party_screen.py`

Update `_render_party_slot` to show fainted Pokemon differently:

```python
def _render_party_slot(self, surface: pygame.Surface, renderer, index: int):
    """Render a single party slot."""
    pokemon = self.party.pokemon[index]

    # ... existing position and cursor code ...

    # Dim sprite if fainted
    if pokemon.species.sprites and pokemon.species.sprites.front:
        sprite = renderer.load_sprite(pokemon.species.sprites.front)
        if sprite:
            scaled_sprite = pygame.transform.scale(sprite, (16, 16))

            # If fainted, dim the sprite
            if pokemon.is_fainted():
                scaled_sprite.set_alpha(100)  # 40% opacity

            surface.blit(scaled_sprite, (x + 12, y))

    # ... existing info rendering ...

    # If fainted, show "FNT" instead of HP
    if pokemon.is_fainted():
        renderer.draw_text(surface, "FNT", info_x + 80, y + 10)
    else:
        hp_text = f"{pokemon.current_hp:3d}/{pokemon.stats.hp:3d}"
        renderer.draw_text(surface, hp_text, info_x + 80, y + 10)
```

### Step 2: Prevent switching to active Pokemon

**File:** `src/states/battle_state.py`

Already implemented in Task 8, verify logic is correct.

### Step 3: Handle party wipe (all fainted)

**File:** `src/states/battle_state.py`

Add check after player Pokemon faints:

```python
def _check_battle_end(self):
    """Check if battle should end."""
    # Player Pokemon fainted
    if self.player_pokemon.is_fainted():
        self._queue_message(f"{self.player_pokemon.species.name.upper()}\\nfainted!")

        # Check if player has any Pokemon left
        if hasattr(self, 'party') and self.party.has_alive_pokemon():
            # Force switch to next Pokemon
            self._queue_message("Choose next POKéMON!")
            self._show_next_message()

            # Open party in forced switch mode
            from src.states.party_state import PartyState
            party_state = PartyState(self.game, self.party, mode="forced_switch")
            self.game.push_state(party_state)
        else:
            # No Pokemon left - white out
            self._queue_message("You have no more\\nPOKéMON!")
            self._queue_message("You blacked out!")
            self._show_next_message()
            self.phase = "end"
            # TODO: Teleport to Pokemon Center

        return

    # Enemy Pokemon fainted
    if self.enemy_pokemon.is_fainted():
        # ... existing victory code ...
        pass
```

### Step 4: Update PartyState for forced switches

**File:** `src/states/party_state.py`

Update to handle `"forced_switch"` mode:

```python
def handle_input(self, input_handler):
    """Handle party screen input."""
    # ... existing navigation code ...

    elif input_handler.is_just_pressed("a"):
        selected = self.screen.get_selected_pokemon()

        if self.mode == "switch" or self.mode == "forced_switch":
            if selected and not selected.is_fainted():
                self.game.pop_state()

                from src.states.battle_state import BattleState
                battle_state = self.game.state_stack[-1]
                if isinstance(battle_state, BattleState):
                    battle_state.handle_switch(selected)
            else:
                # Can't switch to fainted Pokemon
                pass
        else:
            # View mode - open summary
            # ... existing code ...

    elif input_handler.is_just_pressed("b"):
        # Can't cancel forced switch
        if self.mode == "forced_switch":
            # Show message
            pass
        else:
            self.game.pop_state()
```

### Step 5: Test edge cases

```bash
uv run python -m src.main
```

**Test cases:**
- ✓ Catch multiple Pokemon, party fills up
- ✓ Try to catch when party full, see error
- ✓ Switch to different Pokemon in battle
- ✓ Try to switch to already active Pokemon
- ✓ Try to switch to fainted Pokemon
- ✓ Let player Pokemon faint, forced to switch
- ✓ All Pokemon faint, see black out message

### Step 6: Commit

```bash
git add src/states/party_state.py src/states/battle_state.py src/ui/party_screen.py
git commit -m "feat(party): add edge case handling and polish"
```

---

## Testing Checklist

### Party Data Structure
- [ ] Party initializes empty
- [ ] Add Pokemon to party (up to 6)
- [ ] Party rejects 7th Pokemon
- [ ] Get active Pokemon (first non-fainted)
- [ ] Remove Pokemon from party
- [ ] Swap Pokemon positions

### Start Menu
- [ ] Press 'S' key opens start menu
- [ ] Navigate with arrow keys
- [ ] Cursor wraps at top/bottom
- [ ] POKéMON option opens party screen
- [ ] EXIT closes menu
- [ ] Press 'B' closes menu

### Party Screen
- [ ] Shows list of all party Pokemon
- [ ] Displays sprite, name, level, HP for each
- [ ] Navigate with arrow keys
- [ ] Select Pokemon opens summary
- [ ] Press 'B' returns to start menu
- [ ] Fainted Pokemon shown dimmed with "FNT"

### Summary Screen
- [ ] Shows Pokemon details (stats, type, status)
- [ ] Navigate between pages (INFO/MOVES) with left/right
- [ ] Navigate between Pokemon with up/down
- [ ] MOVES page shows move names, PP, type, power
- [ ] Press 'B' returns to party screen

### Battle Switching
- [ ] PKM button in battle opens party screen
- [ ] Select Pokemon switches active Pokemon
- [ ] See switch messages ("come back", "Go!")
- [ ] Enemy attacks after switch
- [ ] Can't switch to already active Pokemon
- [ ] Can't switch to fainted Pokemon
- [ ] Forced switch when active Pokemon faints

### Catching
- [ ] Catch Pokemon, added to party
- [ ] Party screen shows newly caught Pokemon
- [ ] Can't catch when party full (shows error)
- [ ] Caught Pokemon has correct level, moves, stats

### Edge Cases
- [ ] All Pokemon faint, see black out message
- [ ] Navigate through empty party (shouldn't crash)
- [ ] Switch Pokemon then view summary (shows correct Pokemon)
- [ ] Catch fills party to exactly 6 (no errors)

---

## Future Phase Integration Notes

**Phase 8B (Inventory):**
- Replace RUN placeholder with proper ITEM menu
- Add BALL item in bag
- Proper catch flow: ITEM -> BALL -> throw

**Phase 8C (Save/Load):**
- Serialize Party data
- Save party composition, levels, HP, PP
- Load party on game start

**Phase 9+ (Advanced):**
- PC Box system (when party full)
- Deposit/Withdraw Pokemon
- Multi-box management
- Move learning UI (replace move on level up)
- Move deleter/relearner NPCs

---

## Common Issues & Solutions

**Issue:** Party not persisting between battles
**Solution:** Ensure `self.party` is stored on OverworldState and passed to BattleState

**Issue:** Sprites not loading in party screen
**Solution:** Check sprite paths in `species.yaml`, ensure `renderer.load_sprite()` caches correctly

**Issue:** Switching crashes battle
**Solution:** Verify `handle_switch()` updates `self.player_pokemon` and sprite before continuing turn

**Issue:** Can't see start menu
**Solution:** Check render order - menu should render after overworld (draw over it)

**Issue:** PP not saving between battles
**Solution:** Pokemon instances must persist in party, not recreated each battle

---

## Commands Reference

```bash
# Run game
uv run python -m src.main

# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_party.py -v

# Run specific test
uv run pytest tests/test_party.py::test_party_add_pokemon -v

# Test imports
uv run python -c "from src.party.party import Party; print('✓ OK')"
```

---

**Plan complete!** This comprehensive plan covers all of Phase 8A: Party Management UI, broken down into bite-sized TDD tasks with exact file paths, code, and testing steps.
