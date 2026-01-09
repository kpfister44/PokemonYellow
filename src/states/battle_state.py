# ABOUTME: Battle state for Pokemon battles
# ABOUTME: Manages battle flow, UI, and damage calculation

from src.states.base_state import BaseState
from src.battle.pokemon import Pokemon
from src.battle.damage_calculator import DamageCalculator
from src.battle.move_loader import MoveLoader
from src.battle.move import Move
from src.ui.battle_menu import BattleMenu
from src.ui.move_menu import MoveMenu
from src.engine import constants


class BattleState(BaseState):
    """State for Pokemon battles."""

    def __init__(self, game, player_pokemon: Pokemon, enemy_pokemon: Pokemon):
        """
        Initialize battle state.

        Args:
            game: Reference to Game instance
            player_pokemon: Player's Pokemon
            enemy_pokemon: Wild/enemy Pokemon
        """
        super().__init__(game)
        self.player_pokemon = player_pokemon
        self.enemy_pokemon = enemy_pokemon

        # Battle flow state
        self.phase = "intro"  # intro, showing_message, battle_menu, move_selection, enemy_turn, end
        self.message = f"Wild {enemy_pokemon.species.name.upper()}\nappeared!"
        self.awaiting_input = False
        self.show_message = True  # Whether to show message box

        # Message queue system (Phase 7.8)
        self.message_queue: list[str] = []

        # Systems
        self.damage_calculator = DamageCalculator()
        self.move_loader = MoveLoader()

        # UI components (Phase 7.2)
        self.battle_menu = BattleMenu()
        self.move_menu = None  # Created when FIGHT is selected

        # PP tracking for player's moves
        self.player_move_pp = {}
        self._initialize_player_pp()

        # Delay before allowing player input (frames)
        self.intro_timer = 60  # 1 second at 60 FPS

        # Sprite surfaces (loaded in enter())
        self.player_sprite = None
        self.enemy_sprite = None

    def _initialize_player_pp(self):
        """Initialize PP tracking for player's moves."""
        for move_id in self.player_pokemon.moves:
            move = self.move_loader.get_move(move_id)
            self.player_move_pp[move_id] = move.pp

    def enter(self):
        """Called when entering battle state."""
        print(f"Battle started: {self.player_pokemon.species.name} vs {self.enemy_pokemon.species.name}")

        # Load Pokemon sprites at native size (no scaling - perfectly crisp)
        if self.player_pokemon.species.sprites and self.player_pokemon.species.sprites.back:
            self.player_sprite = self.game.renderer.load_sprite(self.player_pokemon.species.sprites.back)

        if self.enemy_pokemon.species.sprites and self.enemy_pokemon.species.sprites.front:
            self.enemy_sprite = self.game.renderer.load_sprite(self.enemy_pokemon.species.sprites.front)

    def exit(self):
        """Called when exiting battle state."""
        print("Battle ended")

    def handle_input(self, input_handler):
        """
        Handle player input during battle.

        Args:
            input_handler: Input instance
        """
        if not self.awaiting_input:
            return

        # Battle menu phase - handle menu navigation
        if self.phase == "battle_menu":
            selection = self.battle_menu.handle_input(input_handler)
            if selection:
                self._handle_battle_menu_selection(selection)
            return

        # Move selection phase - handle move menu
        if self.phase == "move_selection":
            result = self.move_menu.handle_input(input_handler)
            if result:
                selected_move, cancelled = result
                if cancelled:
                    # B button pressed, go back to battle menu
                    self.move_menu.deactivate()
                    self.battle_menu.activate()
                    self.phase = "battle_menu"
                elif selected_move:
                    # Move selected, execute attack
                    self._execute_player_attack(selected_move)
            return

        # Press Z to advance through messages
        if input_handler.is_just_pressed("a"):
            if self.phase == "showing_message":
                # Show next message or proceed
                self._show_next_message()
            elif self.phase == "enemy_turn":
                self._execute_enemy_attack()
            elif self.phase == "end":
                self._end_battle()

    def _handle_battle_menu_selection(self, selection: str):
        """Handle battle menu selection."""
        self.battle_menu.deactivate()

        if selection == "FIGHT":
            # Create move menu with player's moves
            player_moves = [self.move_loader.get_move(mid) for mid in self.player_pokemon.moves]
            self.move_menu = MoveMenu(player_moves, self.player_move_pp)
            self.move_menu.activate()
            self.phase = "move_selection"

        elif selection == "ITEM":
            self._queue_message("Items not implemented yet!")
            self._show_next_message()

        elif selection == "PKM":
            self._queue_message("Party switching not\nimplemented yet!")
            self._show_next_message()

        elif selection == "RUN":
            # For now, always succeed in running from wild battles
            self._queue_message("Got away safely!")
            self._show_next_message()
            self.phase = "end"

    def update(self, dt):
        """
        Update battle state.

        Args:
            dt: Delta time in seconds
        """
        # Intro phase - wait before allowing input
        if self.phase == "intro":
            self.intro_timer -= 1
            if self.intro_timer <= 0:
                self.phase = "showing_message"
                self.awaiting_input = True

        # Message queue is handled in _show_next_message(), no automatic transitions here

    def render(self, renderer):
        """
        Render the battle screen.

        Args:
            renderer: Renderer instance
        """
        # Clear screen with white background
        renderer.clear(constants.COLOR_WHITE)

        # Render Pokemon sprites
        self._render_sprites(renderer)

        # Render enemy info box (top-left)
        self._render_enemy_info(renderer)

        # Render player info box (bottom-right)
        self._render_player_info(renderer)

        # Render message box if active
        if self.show_message:
            self._render_message_box(renderer)

        # Render menus (Phase 7.2)
        if self.phase == "battle_menu":
            self.battle_menu.render(renderer, 8, 100)
        elif self.phase == "move_selection" and self.move_menu:
            self.move_menu.render(renderer, 8, 100)

    def _render_sprites(self, renderer):
        """Render Pokemon sprites on the battle screen."""
        # Sprites are 96x96 - position them to fit in 160x144 screen
        # Enemy sprite (top-right area)
        if self.enemy_sprite:
            enemy_x = 64  # Right side (160 - 96 = 64)
            enemy_y = -24  # Slightly off top to fit better
            renderer.draw_surface(self.enemy_sprite, (enemy_x, enemy_y))

        # Player sprite (bottom-left area)
        if self.player_sprite:
            player_x = 0  # Left edge
            player_y = 48  # Lower area (144 - 96 = 48)
            renderer.draw_surface(self.player_sprite, (player_x, player_y))

    def _render_enemy_info(self, renderer):
        """Render enemy Pokemon info box (top-left, authentic Pokemon Yellow style)."""
        # Info box position
        box_x = 8
        box_y = 8
        box_width = 64
        box_height = 28

        # Draw info box frame
        renderer.draw_rect(constants.COLOR_BLACK, (box_x, box_y, box_width, box_height), 1)

        # Pokemon name (uppercase)
        enemy_name = self.enemy_pokemon.species.name.upper()
        renderer.draw_text(enemy_name, box_x + 2, box_y + 2, constants.COLOR_BLACK, 10)

        # Level (with :L prefix like in Pokemon Yellow)
        level_text = f":L{self.enemy_pokemon.level}"
        renderer.draw_text(level_text, box_x + 2, box_y + 11, constants.COLOR_BLACK, 10)

        # HP label
        renderer.draw_text("HP:", box_x + 2, box_y + 19, constants.COLOR_BLACK, 8)

        # HP bar
        hp_bar_x = box_x + 14
        hp_bar_y = box_y + 20
        hp_bar_width = 46
        hp_bar_height = 3
        hp_percentage = self.enemy_pokemon.get_hp_percentage()

        # Background (empty part of HP bar)
        renderer.draw_rect(constants.COLOR_DARKEST, (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height), 0)

        # Filled part of HP bar (green/yellow/red based on HP)
        filled_width = int(hp_bar_width * hp_percentage)
        if filled_width > 0:
            hp_color = self._get_hp_bar_color(hp_percentage)
            renderer.draw_rect(hp_color, (hp_bar_x, hp_bar_y, filled_width, hp_bar_height), 0)

    def _render_player_info(self, renderer):
        """Render player Pokemon info box (bottom-right, authentic Pokemon Yellow style)."""
        # Info box position
        box_x = 72
        box_y = 80
        box_width = 80
        box_height = 36

        # Draw info box frame
        renderer.draw_rect(constants.COLOR_BLACK, (box_x, box_y, box_width, box_height), 1)

        # Pokemon name (uppercase, right-aligned-ish)
        player_name = self.player_pokemon.species.name.upper()
        renderer.draw_text(player_name, box_x + 26, box_y + 2, constants.COLOR_BLACK, 10)

        # Level (with :L prefix)
        level_text = f":L{self.player_pokemon.level}"
        renderer.draw_text(level_text, box_x + 26, box_y + 11, constants.COLOR_BLACK, 10)

        # HP label
        renderer.draw_text("HP:", box_x + 2, box_y + 19, constants.COLOR_BLACK, 8)

        # HP bar
        hp_bar_x = box_x + 14
        hp_bar_y = box_y + 20
        hp_bar_width = 62
        hp_bar_height = 3
        hp_percentage = self.player_pokemon.get_hp_percentage()

        # Background
        renderer.draw_rect(constants.COLOR_DARKEST, (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height), 0)

        # Filled part
        filled_width = int(hp_bar_width * hp_percentage)
        if filled_width > 0:
            hp_color = self._get_hp_bar_color(hp_percentage)
            renderer.draw_rect(hp_color, (hp_bar_x, hp_bar_y, filled_width, hp_bar_height), 0)

        # HP numbers (current / max)
        hp_text = f"{self.player_pokemon.current_hp:3}/ {self.player_pokemon.stats.hp:3}"
        renderer.draw_text(hp_text, box_x + 20, box_y + 26, constants.COLOR_BLACK, 10)

    def _get_hp_bar_color(self, hp_percentage):
        """Get HP bar color based on percentage (green > yellow > red)."""
        if hp_percentage > 0.5:
            return (48, 208, 48)  # Green
        elif hp_percentage > 0.2:
            return (248, 208, 48)  # Yellow
        else:
            return (248, 88, 56)  # Red

    def _wrap_text(self, text, max_chars):
        """
        Wrap text to fit within max_chars per line.

        Args:
            text: Text to wrap
            max_chars: Maximum characters per line

        Returns:
            List of text lines
        """
        words = text.split(' ')
        lines = []
        current_line = []

        for word in words:
            # Test if adding this word exceeds max_chars
            test_line = ' '.join(current_line + [word])
            if len(test_line) <= max_chars:
                current_line.append(word)
            else:
                # Start new line
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        # Add remaining words
        if current_line:
            lines.append(' '.join(current_line))

        return lines

    def _render_message_box(self, renderer):
        """Render battle message box (authentic Pokemon Yellow style)."""
        box_x = 8
        box_y = 112
        box_width = 144
        box_height = 28

        # Draw double border (authentic style)
        renderer.draw_rect(constants.COLOR_BLACK, (box_x, box_y, box_width, box_height), 2)
        renderer.draw_rect(constants.COLOR_BLACK, (box_x + 4, box_y + 4, box_width - 8, box_height - 8), 2)
        renderer.draw_rect(constants.COLOR_WHITE, (box_x + 6, box_y + 6, box_width - 12, box_height - 12), 0)

        # Draw message (supports \n for line breaks)
        lines = self.message.split('\n')
        for i, line in enumerate(lines[:2]):  # Max 2 lines
            renderer.draw_text(line, box_x + 10, box_y + 8 + (i * 10), constants.COLOR_BLACK, 10)

    def _queue_message(self, text: str):
        """Add message to queue."""
        self.message_queue.append(text)

    def _show_next_message(self):
        """Display next queued message or continue turn flow."""
        if self.message_queue:
            # Show next message
            self.message = self.message_queue.pop(0)
            self.show_message = True
            self.awaiting_input = True
            self.phase = "showing_message"
        else:
            # No more messages, proceed to next phase
            self.show_message = False
            self.awaiting_input = False
            self._advance_turn()

    def _advance_turn(self):
        """Advance to next phase after messages are done."""
        # Check for fainted Pokemon
        if self.enemy_pokemon.is_fainted():
            self._queue_message(f"Wild {self.enemy_pokemon.species.name.upper()}\nfainted!")
            self._show_next_message()
            self.phase = "end"
            return

        if self.player_pokemon.is_fainted():
            self._queue_message(f"{self.player_pokemon.species.name.upper()}\nfainted!")
            self._show_next_message()
            self.phase = "end"
            return

        # Check current phase to determine next phase
        if self.phase == "showing_message":
            # After intro message
            if self.message.endswith("appeared!"):
                self.battle_menu.activate()
                self.phase = "battle_menu"
                self.awaiting_input = True
            # After player's attack, enemy's turn
            elif self.message and not "Wild" in self.message and "used" in self.message:
                self.phase = "enemy_turn"
                self.awaiting_input = True
            # After enemy's attack, player's turn (show menu)
            elif "Wild" in self.message and "used" in self.message:
                self.battle_menu.activate()
                self.phase = "battle_menu"
                self.awaiting_input = True

    def _execute_player_attack(self, move: Move):
        """
        Execute player's attack.

        Args:
            move: Move to use
        """
        self.awaiting_input = False

        # Deduct PP
        if move.move_id in self.player_move_pp:
            self.player_move_pp[move.move_id] -= 1

        # Calculate damage
        damage = self.damage_calculator.calculate_damage(
            self.player_pokemon,
            self.enemy_pokemon,
            move
        )

        # Apply damage
        self.enemy_pokemon.take_damage(damage)

        # Queue attack message
        self._queue_message(f"{self.player_pokemon.species.name.upper()} used\n{move.name.upper()}!")
        self._show_next_message()

    def _execute_enemy_attack(self):
        """Execute enemy's attack."""
        self.awaiting_input = False

        if not self.enemy_pokemon.moves:
            self.battle_menu.activate()
            self.phase = "battle_menu"
            self.awaiting_input = True
            return

        move_id = self.enemy_pokemon.moves[0]
        move = self.move_loader.get_move(move_id)

        damage = self.damage_calculator.calculate_damage(
            self.enemy_pokemon,
            self.player_pokemon,
            move
        )

        self.player_pokemon.take_damage(damage)

        # Queue attack message
        self._queue_message(f"Wild {self.enemy_pokemon.species.name.upper()}\nused {move.name.upper()}!")
        self._show_next_message()

    def _end_battle(self):
        """End the battle and return to overworld."""
        self.game.pop_state()
