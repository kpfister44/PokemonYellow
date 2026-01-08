# ABOUTME: Battle state for Pokemon battles
# ABOUTME: Manages battle flow, UI, and damage calculation

from src.states.base_state import BaseState
from src.battle.pokemon import Pokemon
from src.battle.damage_calculator import DamageCalculator
from src.battle.move_loader import MoveLoader
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
        self.phase = "intro"  # intro, player_turn, showing_message, enemy_turn, end
        self.message = f"Wild {enemy_pokemon.species.name.upper()}\nappeared!"
        self.awaiting_input = False
        self.show_message = True  # Whether to show message box

        # Systems
        self.damage_calculator = DamageCalculator()
        self.move_loader = MoveLoader()

        # Delay before allowing player input (frames)
        self.intro_timer = 60  # 1 second at 60 FPS

    def enter(self):
        """Called when entering battle state."""
        print(f"Battle started: {self.player_pokemon.species.name} vs {self.enemy_pokemon.species.name}")

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

        # Press Z to advance through battle
        if input_handler.is_just_pressed("a"):
            if self.phase == "showing_message":
                # Message is done, hide it and go to next phase
                self.show_message = False
                self.awaiting_input = False
            elif self.phase == "player_turn":
                self._execute_player_attack()
            elif self.phase == "enemy_turn":
                self._execute_enemy_attack()
            elif self.phase == "end":
                self._end_battle()

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

        # After message is dismissed, decide next phase
        if self.phase == "showing_message" and not self.show_message:
            if self.message.endswith("appeared!"):
                # Intro done, player's turn
                self.phase = "player_turn"
                self.show_message = False
                self.awaiting_input = True
            elif "used" in self.message:
                # Attack message shown, now check who attacks next
                if self.enemy_pokemon.is_fainted() or self.player_pokemon.is_fainted():
                    self.phase = "end"
                    self.message = f"Wild {self.enemy_pokemon.species.name.upper()}\nfainted!" if self.enemy_pokemon.is_fainted() else f"{self.player_pokemon.species.name.upper()}\nfainted!"
                    self.show_message = True
                    self.awaiting_input = True
                elif self.player_pokemon.current_hp < self.player_pokemon.stats.hp or self.enemy_pokemon.current_hp < self.enemy_pokemon.stats.hp:
                    # Damage was dealt, go to opposite turn
                    if "Wild" in self.message:
                        # Enemy just attacked, player's turn
                        self.phase = "player_turn"
                    else:
                        # Player just attacked, enemy's turn
                        self.phase = "enemy_turn"
                    self.awaiting_input = True

    def render(self, renderer):
        """
        Render the battle screen.

        Args:
            renderer: Renderer instance
        """
        # Clear screen with white background
        renderer.clear(constants.COLOR_WHITE)

        # Render enemy info box (top-left)
        self._render_enemy_info(renderer)

        # Render player info box (bottom-right)
        self._render_player_info(renderer)

        # Render message box if active
        if self.show_message:
            self._render_message_box(renderer)

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

    def _execute_player_attack(self):
        """Execute player's attack."""
        self.awaiting_input = False

        # For Phase 6, just use the first move
        if not self.player_pokemon.moves:
            self.message = "No moves available!"
            self.show_message = True
            self.awaiting_input = True
            return

        move_id = self.player_pokemon.moves[0]
        move = self.move_loader.get_move(move_id)

        # Calculate damage
        damage = self.damage_calculator.calculate_damage(
            self.player_pokemon,
            self.enemy_pokemon,
            move
        )

        # Apply damage
        self.enemy_pokemon.take_damage(damage)

        # Update message with uppercase name
        self.message = f"{self.player_pokemon.species.name.upper()} used\n{move.name.upper()}!"
        self.show_message = True
        self.phase = "showing_message"
        self.awaiting_input = True

    def _execute_enemy_attack(self):
        """Execute enemy's attack."""
        if not self.enemy_pokemon.moves:
            self.phase = "player_turn"
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

        # Update message with uppercase name
        self.message = f"Wild {self.enemy_pokemon.species.name.upper()}\nused {move.name.upper()}!"
        self.show_message = True
        self.phase = "showing_message"
        self.awaiting_input = True

    def _end_battle(self):
        """End the battle and return to overworld."""
        self.game.pop_state()
