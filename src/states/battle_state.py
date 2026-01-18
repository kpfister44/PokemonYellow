# ABOUTME: Battle state for Pokemon battles
# ABOUTME: Manages battle flow, UI, and damage calculation

from dataclasses import dataclass

import pygame

from src.states.base_state import BaseState
from src.battle.pokemon import Pokemon
from src.battle.damage_calculator import DamageCalculator
from src.battle.move_loader import MoveLoader
from src.battle.move import Move
from src.ui.battle_menu import BattleMenu
from src.ui.move_menu import MoveMenu
from src.ui.yes_no_menu import YesNoMenu
from src.ui.forget_move_menu import ForgetMoveMenu
from src.engine import constants
from src.battle.catch_calculator import CatchCalculator
from src.battle.hp_bar_display import HpBarDisplay


@dataclass
class AttackData:
    attacker: Pokemon
    defender: Pokemon
    move: Move
    is_player: bool


@dataclass
class AttackContext:
    attacker: Pokemon
    defender: Pokemon
    move: Move
    is_player: bool
    total_damage: int = 0
    hits_landed: int = 0
    planned_hits: int = 1
    is_critical: bool = False


class BattleState(BaseState):
    """State for Pokemon battles."""

    def __init__(
        self,
        game,
        player_pokemon: Pokemon,
        enemy_pokemon: Pokemon,
        is_trainer_battle: bool = False,
        trainer=None,
        trainer_pokemon_remaining: list[Pokemon] | None = None
    ):
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
        self.is_trainer_battle = is_trainer_battle
        self.trainer = trainer
        self.trainer_pokemon_remaining = trainer_pokemon_remaining or []

        # Battle flow state
        self.phase = "intro"  # intro, showing_message, battle_menu, move_selection, move_learn_choice, forget_move, enemy_turn, throwing_ball, catch_result, end
        if self.is_trainer_battle and self.trainer:
            self.message = f"{self.trainer.trainer_class}\n{self.trainer.name} wants to fight!"
        else:
            self.message = f"Wild {enemy_pokemon.species.name.upper()}\nappeared!"
        self.awaiting_input = False
        self.show_message = True  # Whether to show message box

        # Message queue system (Phase 7.8)
        self.message_queue: list[str] = []
        self.post_message_phase: str | None = None

        # Systems
        self.damage_calculator = DamageCalculator()
        self.move_loader = MoveLoader()

        # UI components (Phase 7.2)
        self.battle_menu = BattleMenu()
        self.move_menu = None  # Created when FIGHT is selected
        self.learn_menu = YesNoMenu()
        self.forget_menu = None
        self.sequence_active = False
        self.sequence_steps = []
        self.sequence_step_type = None
        self.sequence_end_phase = None
        self.flinch_target = None
        self.attack_animation_duration = 0.18
        self.attack_animation_timer = 0.0
        self.attack_animation_target = None
        self.attack_animation_tick = 0.0
        self.hp_tick_target = None
        self.pending_after_tick = None
        self.escape_attempts = 0
        self.ball_sprite_path = None
        self.ball_position = (0.0, 0.0)
        self.ball_start = (0.0, 0.0)
        self.ball_end = (0.0, 0.0)
        self.ball_throw_duration = 0.5
        self.ball_throw_elapsed = 0.0
        self.ball_arc_height = 24.0 * constants.UI_SCALE
        self.ball_shake_offsets = [
            0,
            3 * constants.UI_SCALE,
            0,
            -3 * constants.UI_SCALE,
            0
        ]
        self.ball_shake_index = 0
        self.ball_shake_timer = 0.0
        self.ball_shake_frame_time = 0.06
        self.ball_shake_pause = 0.16
        self.ball_shake_pause_timer = 0.0
        self.ball_shake_offset = 0
        self.ball_active = False
        self.catch_hide_enemy = False
        self.catch_attempts = 0
        self.catch_success = False
        self.exp_flow_active = False
        self.exp_flow_step = None
        self.exp_recipients: list[Pokemon] = []
        self.exp_recipient_index = 0
        self.exp_gain = 0
        self.pending_levels: list[int] = []
        self.pending_moves: list[str] = []
        self.pending_move_id: str | None = None
        self.pending_level: int | None = None
        self.exp_after_flow_phase: str | None = None
        self.victory_in_progress = False
        self.participants: list[Pokemon] = [self.player_pokemon]

        self.enemy_hp_bar_width = 46 * constants.UI_SCALE
        self.player_hp_bar_width = 62 * constants.UI_SCALE
        self.enemy_hp_display = HpBarDisplay(
            self.enemy_pokemon.stats.hp,
            self.enemy_pokemon.current_hp,
            self.enemy_hp_bar_width
        )
        self.player_hp_display = HpBarDisplay(
            self.player_pokemon.stats.hp,
            self.player_pokemon.current_hp,
            self.player_hp_bar_width
        )

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
        self.player_move_pp = {}
        for move_id, (current_pp, _) in self.player_pokemon.move_pp.items():
            self.player_move_pp[move_id] = current_pp

    def _sync_player_move_pp(self, pokemon: Pokemon):
        """Sync displayed PP values with Pokemon state."""
        if pokemon is not self.player_pokemon:
            return
        self._initialize_player_pp()

    def enter(self):
        """Called when entering battle state."""
        print(f"Battle started: {self.player_pokemon.species.name} vs {self.enemy_pokemon.species.name}")
        self._mark_seen()

        # Load Pokemon sprites at native size (no scaling - perfectly crisp)
        if self.player_pokemon.species.sprites and self.player_pokemon.species.sprites.back:
            self.player_sprite = self.game.renderer.load_sprite(self.player_pokemon.species.sprites.back)
            if self.player_sprite:
                self.player_sprite = pygame.transform.scale(
                    self.player_sprite,
                    (
                        self.player_sprite.get_width() * constants.UI_SCALE,
                        self.player_sprite.get_height() * constants.UI_SCALE
                    )
                )

        if self.enemy_pokemon.species.sprites and self.enemy_pokemon.species.sprites.front:
            self.enemy_sprite = self.game.renderer.load_sprite(self.enemy_pokemon.species.sprites.front)
            if self.enemy_sprite:
                self.enemy_sprite = pygame.transform.scale(
                    self.enemy_sprite,
                    (
                        self.enemy_sprite.get_width() * constants.UI_SCALE,
                        self.enemy_sprite.get_height() * constants.UI_SCALE
                    )
                )

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

        if self.sequence_active:
            if self.phase == "showing_message" and input_handler.is_just_pressed("a"):
                self._advance_sequence()
            return

        # Battle menu phase - handle menu navigation
        if self.phase == "battle_menu":
            selection = self.battle_menu.handle_input(input_handler)
            if selection:
                self._handle_battle_menu_selection(selection)
            return

        if self.phase == "move_learn_choice":
            choice = self.learn_menu.handle_input(input_handler)
            if choice is not None:
                self._handle_move_learning_choice(choice)
            return

        if self.phase == "forget_move":
            if self.forget_menu:
                selected_move, cancelled = self.forget_menu.handle_input(input_handler)
                if cancelled:
                    self._decline_move_learning()
                elif selected_move:
                    self._replace_move(selected_move)
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
        if selection != "RUN":
            self.escape_attempts = 0

        if selection == "FIGHT":
            # Create move menu with player's moves
            player_moves = [self.move_loader.get_move(mid) for mid in self.player_pokemon.moves]
            self.move_menu = MoveMenu(player_moves, self.player_move_pp)
            self.move_menu.activate()
            self.phase = "move_selection"

        elif selection == "ITEM":
            if hasattr(self, 'bag') and hasattr(self, 'party'):
                from src.states.bag_state import BagState
                bag_state = BagState(
                    self.game,
                    self.bag,
                    self.party,
                    mode="battle",
                    active_pokemon=self.player_pokemon,
                    is_trainer_battle=self.is_trainer_battle,
                    on_item_used=self._handle_item_result,
                    on_cancel=self._handle_bag_cancel
                )
                self.game.push_state(bag_state)
            else:
                self._queue_message("Items not\nimplemented yet!")
                self._show_next_message()

        elif selection == "PKM":
            # Open party screen in switch mode
            if hasattr(self, 'party'):
                from src.states.party_state import PartyState
                party_state = PartyState(
                    self.game,
                    self.party,
                    mode="switch",
                    on_cancel=self._handle_party_cancel
                )
                self.game.push_state(party_state)
            else:
                self._queue_message("Party not\nimplemented yet!")
                self._show_next_message()

        elif selection == "RUN":
            if self.is_trainer_battle:
                self._queue_message("Can't run from a\ntrainer battle!")
                self._show_next_message()
                self.battle_menu.activate()
                self.phase = "battle_menu"
                self.awaiting_input = True
            else:
                self._handle_run_attempt()

    def handle_switch(self, new_pokemon: Pokemon):
        """
        Handle switching to a new Pokemon.

        Args:
            new_pokemon: Pokemon to switch to
        """
        # Can't switch to already active Pokemon
        if new_pokemon == self.player_pokemon:
            self._queue_message(f"{new_pokemon.species.name.upper()} is\nalready out!")
            self._show_next_message()
            self.battle_menu.activate()
            self.phase = "battle_menu"
            return

        # Switch Pokemon
        old_pokemon = self.player_pokemon
        self.player_pokemon = new_pokemon
        if new_pokemon not in self.participants:
            self.participants.append(new_pokemon)
        self.player_hp_display = HpBarDisplay(
            self.player_pokemon.stats.hp,
            self.player_pokemon.current_hp,
            self.player_hp_bar_width
        )
        self._sync_player_move_pp(new_pokemon)

        # Update sprite
        if new_pokemon.species.sprites and new_pokemon.species.sprites.back:
            self.player_sprite = self.game.renderer.load_sprite(
                new_pokemon.species.sprites.back
            )

        # Queue switch messages
        self._queue_message(f"{old_pokemon.species.name.upper()},\ncome back!")
        self._queue_message(f"Go! {new_pokemon.species.name.upper()}!")

        # Switching uses a turn, so enemy attacks after
        self.phase = "enemy_turn"
        self._show_next_message()

    def update(self, dt):
        """
        Update battle state.

        Args:
            dt: Delta time in seconds
        """
        self.player_hp_display.update(self.player_pokemon.current_hp, dt)
        self.enemy_hp_display.update(self.enemy_pokemon.current_hp, dt)

        if self.sequence_active:
            if self.phase == "attack_animation":
                self.attack_animation_timer -= dt
                self.attack_animation_tick += dt
                if self.attack_animation_timer <= 0:
                    self._advance_sequence()
                return

            if self.phase == "hp_tick":
                if self._is_hp_tick_done():
                    if self.pending_after_tick:
                        extra_steps = self.pending_after_tick()
                        self.pending_after_tick = None
                        if extra_steps:
                            self.sequence_steps = extra_steps + self.sequence_steps
                        if not self.sequence_active:
                            return
                    self._advance_sequence()
                return

            if self.phase == "ball_throw":
                self.ball_throw_elapsed += dt
                t = min(1.0, self.ball_throw_elapsed / self.ball_throw_duration)
                start_x, start_y = self.ball_start
                end_x, end_y = self.ball_end
                arc_offset = self.ball_arc_height * 4 * t * (1 - t)
                self.ball_position = (
                    start_x + (end_x - start_x) * t,
                    start_y + (end_y - start_y) * t - arc_offset
                )
                if t >= 1.0:
                    self.ball_position = self.ball_end
                    self.catch_hide_enemy = True
                    self._advance_sequence()
                return

            if self.phase == "ball_shake":
                if self.ball_shake_pause_timer > 0:
                    self.ball_shake_pause_timer -= dt
                    if self.ball_shake_pause_timer <= 0:
                        self._advance_sequence()
                    return

                self.ball_shake_timer += dt
            if self.ball_shake_timer >= self.ball_shake_frame_time:
                self.ball_shake_timer -= self.ball_shake_frame_time
                self.ball_shake_index += 1
                if self.ball_shake_index >= len(self.ball_shake_offsets):
                    self.ball_shake_offset = 0
                    self.ball_shake_pause_timer = self.ball_shake_pause
                else:
                    self.ball_shake_offset = self.ball_shake_offsets[self.ball_shake_index]
            return

            return

        if not self.awaiting_input and not self.show_message:
            enemy_done = not self.enemy_hp_display.is_animating(self.enemy_pokemon.current_hp)
            player_done = not self.player_hp_display.is_animating(self.player_pokemon.current_hp)
            if (self.enemy_pokemon.is_fainted() and enemy_done) or (
                self.player_pokemon.is_fainted() and player_done
            ):
                self._advance_turn()

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
            self.battle_menu.render(
                renderer,
                8 * constants.UI_SCALE,
                100 * constants.UI_SCALE
            )
        elif self.phase == "move_selection" and self.move_menu:
            self.move_menu.render(
                renderer,
                8 * constants.UI_SCALE,
                100 * constants.UI_SCALE
            )
        elif self.phase == "move_learn_choice":
            self.learn_menu.render(
                renderer,
                104 * constants.UI_SCALE,
                88 * constants.UI_SCALE
            )
        elif self.phase == "forget_move" and self.forget_menu:
            self.forget_menu.render(
                renderer,
                8 * constants.UI_SCALE,
                72 * constants.UI_SCALE
            )

    def _render_sprites(self, renderer):
        """Render Pokemon sprites on the battle screen."""
        player_offset_x = 0
        enemy_offset_x = 0
        if self.phase == "attack_animation":
            offset = 2 * constants.UI_SCALE
            if int(self.attack_animation_tick * 20) % 2 != 0:
                offset = -offset
            if self.attack_animation_target == "player":
                player_offset_x = offset
            elif self.attack_animation_target == "enemy":
                enemy_offset_x = offset

        # Sprites are authored at 96x96 and scaled for the battle layout
        # Enemy sprite (top-right area)
        if self.enemy_sprite and not self.catch_hide_enemy:
            enemy_x = 64 * constants.UI_SCALE
            enemy_y = -24 * constants.UI_SCALE
            renderer.draw_surface(self.enemy_sprite, (enemy_x + enemy_offset_x, enemy_y))

        # Player sprite (bottom-left area)
        if self.player_sprite:
            player_x = 0
            player_y = 48 * constants.UI_SCALE
            renderer.draw_surface(self.player_sprite, (player_x + player_offset_x, player_y))

        if self.ball_active and self.ball_sprite_path:
            ball_sprite = renderer.load_sprite(self.ball_sprite_path)
            if ball_sprite:
                ball_sprite = pygame.transform.scale(
                    ball_sprite,
                    (
                        ball_sprite.get_width() * constants.UI_SCALE,
                        ball_sprite.get_height() * constants.UI_SCALE
                    )
                )
                ball_x = int(self.ball_position[0] + self.ball_shake_offset)
                ball_y = int(self.ball_position[1])
                renderer.draw_surface(ball_sprite, (ball_x, ball_y))

    def _render_enemy_info(self, renderer):
        """Render enemy Pokemon info box (top-left, authentic Pokemon Yellow style)."""
        # Info box position
        box_x = 8 * constants.UI_SCALE
        box_y = 8 * constants.UI_SCALE
        box_width = 64 * constants.UI_SCALE
        box_height = 28 * constants.UI_SCALE

        # Draw info box frame
        renderer.draw_rect(
            constants.COLOR_BLACK,
            (box_x, box_y, box_width, box_height),
            1 * constants.UI_SCALE
        )

        # Pokemon name (uppercase)
        enemy_name = self.enemy_pokemon.species.name.upper()
        renderer.draw_text(
            enemy_name,
            box_x + (2 * constants.UI_SCALE),
            box_y + (2 * constants.UI_SCALE),
            constants.COLOR_BLACK,
            10 * constants.UI_SCALE
        )

        # Level (with :L prefix like in Pokemon Yellow)
        level_text = f":L{self.enemy_pokemon.level}"
        renderer.draw_text(
            level_text,
            box_x + (2 * constants.UI_SCALE),
            box_y + (11 * constants.UI_SCALE),
            constants.COLOR_BLACK,
            10 * constants.UI_SCALE
        )

        # HP label
        renderer.draw_text(
            "HP:",
            box_x + (2 * constants.UI_SCALE),
            box_y + (19 * constants.UI_SCALE),
            constants.COLOR_BLACK,
            8 * constants.UI_SCALE
        )

        # HP bar
        hp_bar_x = box_x + (14 * constants.UI_SCALE)
        hp_bar_y = box_y + (20 * constants.UI_SCALE)
        hp_bar_width = self.enemy_hp_bar_width
        hp_bar_height = 3 * constants.UI_SCALE
        hp_percentage = self.enemy_hp_display.display_hp / self.enemy_pokemon.stats.hp

        # Background (empty part of HP bar)
        renderer.draw_rect(constants.COLOR_DARKEST, (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height), 0)

        # Filled part of HP bar (green/yellow/red based on HP)
        filled_width = self.enemy_hp_display.display_units
        if filled_width > 0:
            hp_color = self._get_hp_bar_color(hp_percentage)
            renderer.draw_rect(hp_color, (hp_bar_x, hp_bar_y, filled_width, hp_bar_height), 0)

    def _render_player_info(self, renderer):
        """Render player Pokemon info box (bottom-right, authentic Pokemon Yellow style)."""
        # Info box position
        box_x = 72 * constants.UI_SCALE
        box_y = 80 * constants.UI_SCALE
        box_width = 80 * constants.UI_SCALE
        box_height = 36 * constants.UI_SCALE

        # Draw info box frame
        renderer.draw_rect(
            constants.COLOR_BLACK,
            (box_x, box_y, box_width, box_height),
            1 * constants.UI_SCALE
        )

        # Pokemon name (uppercase, right-aligned-ish)
        player_name = self.player_pokemon.species.name.upper()
        renderer.draw_text(
            player_name,
            box_x + (26 * constants.UI_SCALE),
            box_y + (2 * constants.UI_SCALE),
            constants.COLOR_BLACK,
            10 * constants.UI_SCALE
        )

        # Level (with :L prefix)
        level_text = f":L{self.player_pokemon.level}"
        renderer.draw_text(
            level_text,
            box_x + (26 * constants.UI_SCALE),
            box_y + (11 * constants.UI_SCALE),
            constants.COLOR_BLACK,
            10 * constants.UI_SCALE
        )

        # HP label
        renderer.draw_text(
            "HP:",
            box_x + (2 * constants.UI_SCALE),
            box_y + (19 * constants.UI_SCALE),
            constants.COLOR_BLACK,
            8 * constants.UI_SCALE
        )

        # HP bar
        hp_bar_x = box_x + (14 * constants.UI_SCALE)
        hp_bar_y = box_y + (20 * constants.UI_SCALE)
        hp_bar_width = self.player_hp_bar_width
        hp_bar_height = 3 * constants.UI_SCALE
        hp_percentage = self.player_hp_display.display_hp / self.player_pokemon.stats.hp

        # Background
        renderer.draw_rect(constants.COLOR_DARKEST, (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height), 0)

        # Filled part
        filled_width = self.player_hp_display.display_units
        if filled_width > 0:
            hp_color = self._get_hp_bar_color(hp_percentage)
            renderer.draw_rect(hp_color, (hp_bar_x, hp_bar_y, filled_width, hp_bar_height), 0)

        # HP numbers (current / max)
        hp_text = f"{self.player_hp_display.display_hp:3}/ {self.player_pokemon.stats.hp:3}"
        renderer.draw_text(
            hp_text,
            box_x + (20 * constants.UI_SCALE),
            box_y + (26 * constants.UI_SCALE),
            constants.COLOR_BLACK,
            10 * constants.UI_SCALE
        )

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
        box_x = 8 * constants.UI_SCALE
        box_y = 112 * constants.UI_SCALE
        box_width = 144 * constants.UI_SCALE
        box_height = 28 * constants.UI_SCALE

        # Draw double border (authentic style)
        border_width = 2 * constants.UI_SCALE
        renderer.draw_rect(constants.COLOR_BLACK, (box_x, box_y, box_width, box_height), border_width)
        renderer.draw_rect(
            constants.COLOR_BLACK,
            (box_x + (4 * constants.UI_SCALE), box_y + (4 * constants.UI_SCALE),
             box_width - (8 * constants.UI_SCALE), box_height - (8 * constants.UI_SCALE)),
            border_width
        )
        renderer.draw_rect(
            constants.COLOR_WHITE,
            (box_x + (6 * constants.UI_SCALE), box_y + (6 * constants.UI_SCALE),
             box_width - (12 * constants.UI_SCALE), box_height - (12 * constants.UI_SCALE)),
            0
        )

        # Draw message (supports \n for line breaks)
        lines = self.message.split('\n')
        for i, line in enumerate(lines[:2]):  # Max 2 lines
            renderer.draw_text(
                line,
                box_x + (10 * constants.UI_SCALE),
                box_y + (8 * constants.UI_SCALE) + (i * (10 * constants.UI_SCALE)),
                constants.COLOR_BLACK,
                10 * constants.UI_SCALE
            )

    def _start_sequence(self, steps: list[dict], end_phase: str) -> None:
        self.sequence_active = True
        self.sequence_steps = steps
        self.sequence_step_type = None
        self.sequence_end_phase = end_phase
        self.attack_animation_target = None
        self.hp_tick_target = None
        self.pending_after_tick = None
        self._advance_sequence()

    def _finish_sequence(self) -> None:
        self.sequence_active = False
        self.sequence_step_type = None
        self.attack_animation_target = None
        self.hp_tick_target = None
        self.pending_after_tick = None

        if self.sequence_end_phase == "battle_menu":
            self.battle_menu.activate()
            self.phase = "battle_menu"
            self.awaiting_input = True
        elif self.sequence_end_phase == "enemy_turn":
            self.phase = "enemy_turn"
            self.awaiting_input = True
        elif self.sequence_end_phase == "enemy_attack":
            self._start_enemy_attack_sequence()
        elif self.sequence_end_phase == "end":
            self.phase = "end"
            self.awaiting_input = True

    def _advance_sequence(self) -> None:
        if not self.sequence_steps:
            self._finish_sequence()
            return

        step = self.sequence_steps.pop(0)
        step_type = step.get("type")
        self.sequence_step_type = step_type

        if step_type == "message":
            self.message = step["text"]
            self.show_message = True
            self.awaiting_input = True
            self.phase = "showing_message"
            return

        if step_type == "attack":
            self._expand_attack_step(step)
            return

        if step_type == "attack_animation":
            self.show_message = False
            self.awaiting_input = False
            self.phase = "attack_animation"
            self.attack_animation_target = step["target"]
            self.attack_animation_timer = step.get("duration", self.attack_animation_duration)
            self.attack_animation_tick = 0.0
            return

        if step_type == "ball_throw":
            self.show_message = False
            self.awaiting_input = False
            self.phase = "ball_throw"
            self.ball_sprite_path = step["sprite"]
            self.ball_start = step["start"]
            self.ball_end = step["end"]
            self.ball_throw_elapsed = 0.0
            self.ball_position = self.ball_start
            self.ball_active = True
            self.ball_shake_offset = 0
            return

        if step_type == "ball_shake":
            self.show_message = False
            self.awaiting_input = False
            self.phase = "ball_shake"
            self.ball_shake_index = 0
            self.ball_shake_timer = 0.0
            self.ball_shake_pause_timer = 0.0
            self.ball_shake_offset = self.ball_shake_offsets[0]
            return

        if step_type == "damage":
            target = step["target"]
            amount = max(0, step["amount"])
            actual = min(amount, target.current_hp)
            target.take_damage(amount)
            context = step.get("context")
            if context is not None:
                context.total_damage += actual
                context.hits_landed += 1
            self._start_hp_tick(target, step.get("after_tick"))
            return

        if step_type == "heal":
            target = step["target"]
            amount = max(0, step["amount"])
            if amount <= 0:
                self._advance_sequence()
                return
            target.heal(amount)
            self._start_hp_tick(target, None)
            return

        if step_type == "drain_heal":
            context = step["context"]
            percent = step["percent"]
            heal_amount = int(context.total_damage * percent / 100)
            if heal_amount <= 0:
                self._advance_sequence()
                return
            context.attacker.heal(heal_amount)
            self._start_hp_tick(context.attacker, None)
            return

        if step_type == "percent_heal":
            target = step["target"]
            percent = step["percent"]
            heal_amount = int(target.stats.hp * percent / 100)
            if heal_amount <= 0:
                self._advance_sequence()
                return
            target.heal(heal_amount)
            self._start_hp_tick(target, None)
            return

        if step_type == "critical_message":
            context = step["context"]
            if context.is_critical:
                self.message = "Critical hit!"
                self.show_message = True
                self.awaiting_input = True
                self.phase = "showing_message"
                return
            self._advance_sequence()
            return

        if step_type == "hit_count_message":
            context = step["context"]
            if context.hits_landed > 1:
                self.message = f"Hit {context.hits_landed} times!"
                self.show_message = True
                self.awaiting_input = True
                self.phase = "showing_message"
                return
            self._advance_sequence()
            return

        if step_type == "resolve_flinch":
            context = step["context"]
            if (
                context.move.meta
                and context.move.meta.flinch_chance > 0
                and not context.defender.is_fainted()
            ):
                import random
                if random.randint(1, 100) <= context.move.meta.flinch_chance:
                    self.flinch_target = context.defender
            self._advance_sequence()
            return

        if step_type == "faint_check":
            defender = step["defender"]
            if defender.is_fainted():
                self._handle_fainted(defender)
                return
            self._advance_sequence()
            return

        if step_type == "catch_end":
            self.ball_active = False
            if step.get("caught"):
                self.catch_hide_enemy = True
            else:
                self.catch_hide_enemy = False
            self._advance_sequence()
            return

        if step_type == "enemy_attack":
            self.ball_active = False
            self.catch_hide_enemy = False
            self._start_enemy_attack_sequence()
            return

        if step_type == "end_status":
            status_steps = self._build_end_status_steps()
            if status_steps:
                self.sequence_steps = status_steps + self.sequence_steps
            self._advance_sequence()
            return

        self._advance_sequence()

    def _expand_attack_step(self, step: dict) -> None:
        attack = step["attack"]
        if self.flinch_target is attack.attacker:
            self.flinch_target = None
            self.sequence_steps = [
                {"type": "message", "text": f"{attack.attacker.species.name.upper()} flinched!"}
            ] + self.sequence_steps
            self._advance_sequence()
            return

        steps = self._build_attack_steps(attack, step.get("can_flinch", False))
        self.sequence_steps = steps + self.sequence_steps
        self._advance_sequence()

    def _start_hp_tick(self, target: Pokemon, after_tick) -> None:
        self.show_message = False
        self.awaiting_input = False
        self.phase = "hp_tick"
        self.hp_tick_target = target
        self.pending_after_tick = after_tick

    def _is_hp_tick_done(self) -> bool:
        if self.hp_tick_target is None:
            return True
        display = self.player_hp_display if self.hp_tick_target is self.player_pokemon else self.enemy_hp_display
        return not display.is_animating(self.hp_tick_target.current_hp)

    def _cancel_pending_hits(self, context: AttackContext) -> None:
        self.sequence_steps = [
            step for step in self.sequence_steps
            if not (step.get("type") == "damage" and step.get("context") is context)
        ]

    def _build_turn_steps(self, turn_order: list[str], player_move: Move, enemy_move: Move) -> list[dict]:
        steps: list[dict] = []
        attacks = []
        for attacker_name in turn_order:
            if attacker_name == "player":
                attacks.append(AttackData(self.player_pokemon, self.enemy_pokemon, player_move, True))
            else:
                attacks.append(AttackData(self.enemy_pokemon, self.player_pokemon, enemy_move, False))

        for index, attack in enumerate(attacks):
            steps.append({
                "type": "attack",
                "attack": attack,
                "can_flinch": index == 0
            })

        steps.append({"type": "end_status"})
        return steps

    def _build_attack_steps(self, attack: AttackData, can_flinch: bool) -> list[dict]:
        steps: list[dict] = []
        attacker_name = attack.attacker.species.name.upper()
        prefix = "" if attack.is_player else "Wild "

        blocked, status_messages = self._check_status_before_move(attack.attacker)
        if status_messages:
            for message in status_messages:
                steps.append({"type": "message", "text": message})
        if blocked:
            return steps

        steps.append({"type": "message", "text": f"{prefix}{attacker_name} used\n{attack.move.name.upper()}!"})
        steps.append({
            "type": "attack_animation",
            "target": "player" if attack.is_player else "enemy",
            "duration": self.attack_animation_duration
        })

        if not self.damage_calculator.check_accuracy(attack.attacker, attack.defender, attack.move):
            steps.append({"type": "message", "text": f"{attacker_name}'s\nattack missed!"})
            return steps

        is_critical = self.damage_calculator.check_critical_hit(attack.attacker, attack.move)
        hit_count = self.damage_calculator.get_hit_count(attack.move)
        context = AttackContext(
            attacker=attack.attacker,
            defender=attack.defender,
            move=attack.move,
            is_player=attack.is_player,
            planned_hits=hit_count,
            is_critical=is_critical
        )

        def after_tick() -> list[dict]:
            if attack.defender.is_fainted():
                self._cancel_pending_hits(context)
            return []

        for _ in range(hit_count):
            damage = self.damage_calculator.calculate_damage(
                attack.attacker,
                attack.defender,
                attack.move,
                is_critical
            )
            steps.append({
                "type": "damage",
                "target": attack.defender,
                "amount": damage,
                "context": context,
                "after_tick": after_tick
            })

        if attack.move.meta and attack.move.meta.drain > 0:
            steps.append({
                "type": "drain_heal",
                "context": context,
                "percent": attack.move.meta.drain
            })
            steps.append({"type": "message", "text": f"{attacker_name}\ndrained HP!"})

        if attack.move.meta and attack.move.meta.healing > 0:
            steps.append({
                "type": "percent_heal",
                "target": attack.attacker,
                "percent": attack.move.meta.healing
            })
            steps.append({"type": "message", "text": f"{attacker_name}\nregained health!"})

        steps.append({"type": "critical_message", "context": context})
        steps.append({"type": "hit_count_message", "context": context})
        steps.append({"type": "faint_check", "defender": attack.defender})

        status_message = self._apply_status_after_hit(attack.defender, attack.move)
        if status_message:
            steps.append({"type": "message", "text": status_message})

        for message in self._apply_stat_changes_messages(attack.attacker, attack.move.stat_changes):
            steps.append({"type": "message", "text": message})

        if can_flinch and attack.move.meta and attack.move.meta.flinch_chance > 0:
            steps.append({"type": "resolve_flinch", "context": context})

        return steps

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
            if self.exp_flow_active:
                self._advance_exp_flow()
                return
            self._advance_turn()

    def _advance_turn(self):
        """Advance to next phase after messages are done."""
        # Check for fainted Pokemon
        if self.enemy_pokemon.is_fainted():
            if self.victory_in_progress:
                return
            if self.enemy_hp_display.is_animating(self.enemy_pokemon.current_hp):
                return
            self.victory_in_progress = True
            if self.is_trainer_battle:
                self._queue_message(f"Enemy {self.enemy_pokemon.species.name.upper()}\nfainted!")
            else:
                self._queue_message(f"Wild {self.enemy_pokemon.species.name.upper()}\nfainted!")
            self._handle_victory()
            return

        if self.player_pokemon.is_fainted():
            if self.player_hp_display.is_animating(self.player_pokemon.current_hp):
                return
            self._queue_message(f"{self.player_pokemon.species.name.upper()}\nfainted!")
            self._handle_player_faint()
            return

        # Check current phase to determine next phase
        if self.phase == "showing_message":
            if self.post_message_phase is not None:
                self.phase = self.post_message_phase
                self.post_message_phase = None
                self.awaiting_input = True
                return

            # After intro message
            if self.message.endswith("appeared!"):
                self.battle_menu.activate()
                self.phase = "battle_menu"
                self.awaiting_input = True
            else:
                self.battle_menu.activate()
                self.phase = "battle_menu"
                self.awaiting_input = True

    def _handle_victory(self):
        """Handle victory and award experience."""
        next_phase = "end"
        if self.is_trainer_battle and self.trainer_pokemon_remaining:
            next_phase = "trainer_next"

        self._start_exp_flow(next_phase)

    def _eligible_exp_participants(self) -> list[Pokemon]:
        """Get participating Pokemon eligible for experience."""
        return [pokemon for pokemon in self.participants if not pokemon.is_fainted()]

    def _start_exp_flow(self, next_phase: str):
        """Start EXP award and level-up flow."""
        from src.battle.experience_calculator import ExperienceCalculator

        recipients = self._eligible_exp_participants()
        if not recipients:
            self._finish_exp_flow(next_phase)
            return

        calc = ExperienceCalculator()
        exp_gain = calc.calculate_exp_gain(
            defeated=self.enemy_pokemon,
            is_wild=not self.is_trainer_battle,
            participated=len(recipients)
        )

        self.exp_flow_active = True
        self.exp_flow_step = "exp_message"
        self.exp_recipients = recipients
        self.exp_recipient_index = 0
        self.exp_gain = exp_gain
        self.pending_levels = []
        self.pending_moves = []
        self.pending_move_id = None
        self.pending_level = None
        self.exp_after_flow_phase = next_phase

        self._queue_exp_message()
        self._show_next_message()

    def _queue_exp_message(self):
        """Queue EXP message for current recipient."""
        pokemon = self.exp_recipients[self.exp_recipient_index]
        self._queue_message(
            f"{pokemon.species.name.upper()}\ngained {self.exp_gain} EXP. Points!"
        )

    def _queue_level_message(self, level: int):
        """Queue level-up message for current recipient."""
        pokemon = self.exp_recipients[self.exp_recipient_index]
        self._queue_message(
            f"{pokemon.species.name.upper()}\ngrew to Lv.{level}!"
        )

    def _advance_exp_flow(self):
        """Advance EXP award, level-up, and move learning flow."""
        if not self.exp_flow_active:
            return

        if self.exp_flow_step == "exp_message":
            pokemon = self.exp_recipients[self.exp_recipient_index]
            self.pending_levels = pokemon.gain_experience(self.exp_gain)

            if self.pending_levels:
                self.pending_level = self.pending_levels.pop(0)
                self.exp_flow_step = "level_message"
                self._queue_level_message(self.pending_level)
                self._show_next_message()
                return

            self._advance_exp_recipient()
            return

        if self.exp_flow_step == "level_message":
            pokemon = self.exp_recipients[self.exp_recipient_index]
            self.pending_moves = pokemon.get_level_up_moves(self.pending_level or pokemon.level)
            self.exp_flow_step = "move_learning"
            self._advance_move_learning()
            return

        if self.exp_flow_step == "move_message":
            self.exp_flow_step = "move_learning"
            self._advance_move_learning()
            return

        if self.exp_flow_step == "move_prompt":
            self._prompt_move_learning()
            return

    def _advance_exp_recipient(self):
        """Advance to the next EXP recipient or finish the flow."""
        self.exp_recipient_index += 1
        if self.exp_recipient_index >= len(self.exp_recipients):
            self._finish_exp_flow(self.exp_after_flow_phase or "end")
            return

        self.exp_flow_step = "exp_message"
        self._queue_exp_message()
        self._show_next_message()

    def _finish_exp_flow(self, next_phase: str):
        """Finish EXP flow and continue to the next phase."""
        self.exp_flow_active = False
        self.exp_flow_step = None
        self.pending_levels = []
        self.pending_moves = []
        self.pending_move_id = None
        self.pending_level = None
        self.exp_recipients = []
        self.exp_recipient_index = 0
        self.exp_gain = 0

        if next_phase == "trainer_next":
            self._send_next_trainer_pokemon()
            return

        self.phase = "end"
        self.awaiting_input = True

    def _send_next_trainer_pokemon(self):
        """Send out the next trainer Pokemon after EXP flow."""
        if not self.trainer_pokemon_remaining:
            self.phase = "end"
            self.awaiting_input = True
            return

        self.enemy_pokemon = self.trainer_pokemon_remaining.pop(0)
        self.enemy_hp_display = HpBarDisplay(
            self.enemy_pokemon.stats.hp,
            self.enemy_pokemon.current_hp,
            self.enemy_hp_bar_width
        )

        if self.enemy_pokemon.species.sprites and self.enemy_pokemon.species.sprites.front:
            self.enemy_sprite = self.game.renderer.load_sprite(
                self.enemy_pokemon.species.sprites.front
            )

        self._queue_message(
            f"{self.trainer.name} sent out\n{self.enemy_pokemon.species.name.upper()}!"
        )
        self._mark_seen()
        self._show_next_message()

        self.battle_menu.activate()
        self.phase = "battle_menu"
        self.awaiting_input = True
        self.victory_in_progress = False

    def _advance_move_learning(self):
        """Advance through pending move learning steps."""
        pokemon = self.exp_recipients[self.exp_recipient_index]
        if not self.pending_moves:
            if self.pending_levels:
                self.pending_level = self.pending_levels.pop(0)
                self.exp_flow_step = "level_message"
                self._queue_level_message(self.pending_level)
                self._show_next_message()
                return

            self._advance_exp_recipient()
            return

        move_id = self.pending_moves.pop(0)
        status = pokemon.try_learn_move(move_id)

        if status == "already_known":
            self.exp_flow_step = "move_message"
            self._queue_message(
                f"{pokemon.species.name.upper()} already knows\n{move_id.upper().replace('-', ' ')}."
            )
            self._show_next_message()
            return

        if status == "learned":
            self._sync_player_move_pp(pokemon)
            self.exp_flow_step = "move_message"
            self._queue_message(
                f"{pokemon.species.name.upper()} learned\n{move_id.upper().replace('-', ' ')}!"
            )
            self._show_next_message()
            return

        if status == "needs_replacement":
            self.pending_move_id = move_id
            self.exp_flow_step = "move_prompt"
            self._queue_message(
                f"{pokemon.species.name.upper()} is trying to\nlearn {move_id.upper().replace('-', ' ')}!"
            )
            self._queue_message(
                f"But {pokemon.species.name.upper()} can't\nlearn more than four moves!"
            )
            self._show_next_message()
            return

    def _prompt_move_learning(self):
        """Show yes/no prompt to learn a new move."""
        pokemon = self.exp_recipients[self.exp_recipient_index]
        move_name = (self.pending_move_id or "").upper().replace("-", " ")
        self.message = (
            f"Delete an older\nmove to make room\nfor {move_name}?"
        )
        self.show_message = True
        self.learn_menu.activate()
        self.phase = "move_learn_choice"
        self.awaiting_input = True

    def _handle_move_learning_choice(self, choice: bool):
        """Handle yes/no choice for move learning."""
        self.learn_menu.deactivate()
        if not choice:
            self._decline_move_learning()
            return

        pokemon = self.exp_recipients[self.exp_recipient_index]
        self.forget_menu = ForgetMoveMenu(pokemon.moves)
        self.forget_menu.activate()
        self.phase = "forget_move"
        self.awaiting_input = True

    def _decline_move_learning(self):
        """Decline learning the pending move."""
        pokemon = self.exp_recipients[self.exp_recipient_index]
        move_name = (self.pending_move_id or "").upper().replace("-", " ")
        self.pending_move_id = None
        if self.forget_menu:
            self.forget_menu.deactivate()
            self.forget_menu = None
        self.exp_flow_step = "move_message"
        self.phase = "showing_message"
        self._queue_message(
            f"{pokemon.species.name.upper()} did not\nlearn {move_name}!"
        )
        self._show_next_message()

    def _replace_move(self, old_move_id: str):
        """Replace a move with the pending move."""
        pokemon = self.exp_recipients[self.exp_recipient_index]
        new_move_id = self.pending_move_id or ""
        self.pending_move_id = None
        if self.forget_menu:
            self.forget_menu.deactivate()
            self.forget_menu = None

        if not pokemon.replace_move(old_move_id, new_move_id):
            self._decline_move_learning()
            return

        self._sync_player_move_pp(pokemon)
        old_name = old_move_id.upper().replace("-", " ")
        new_name = new_move_id.upper().replace("-", " ")
        self.exp_flow_step = "move_message"
        self.phase = "showing_message"
        self._queue_message("1, 2 and... Poof!")
        self._queue_message(f"{pokemon.species.name.upper()} forgot\n{old_name}!")
        self._queue_message(f"{pokemon.species.name.upper()} learned\n{new_name}!")
        self._show_next_message()

    def _handle_level_up(self):
        """Handle level up sequence."""
        old_stats = self.player_pokemon.level_up()

        self._queue_message(
            f"{self.player_pokemon.species.name.upper()}\ngrew to Lv.{self.player_pokemon.level}!"
        )

        self._show_next_message()
        self.phase = "end"

    def _attempt_catch_with_ball(
        self,
        ball_name: str,
        ball_bonus: float,
        force_catch: bool,
        ball_item_id: str | None,
        ball_sprite: str | None
    ):
        """Attempt to catch wild Pokemon with a ball."""
        self.catch_hide_enemy = False
        self.ball_active = False

        calc = CatchCalculator()
        if force_catch:
            caught = True
            shakes = 4
        else:
            caught, shakes = calc.calculate_catch_chance(self.enemy_pokemon, ball_bonus=ball_bonus)

        animation_shakes = 3 if caught else min(shakes, 3)
        sprite_path = ball_sprite or "assets/sprites/items/poke-ball.png"

        steps = [
            {"type": "message", "text": f"Used {ball_name.upper()}!"},
            {
                "type": "ball_throw",
                "sprite": sprite_path,
                "start": (24.0 * constants.UI_SCALE, 104.0 * constants.UI_SCALE),
                "end": (96.0 * constants.UI_SCALE, 40.0 * constants.UI_SCALE)
            }
        ]

        for _ in range(animation_shakes):
            steps.append({"type": "ball_shake"})

        if caught:
            steps.append({
                "type": "message",
                "text": f"Gotcha!\n{self.enemy_pokemon.species.name.upper()} was caught!"
            })
            self._mark_caught()

            if hasattr(self, 'party'):
                if not self.party.is_full():
                    self.party.add(self.enemy_pokemon)
                    steps.append({
                        "type": "message",
                        "text": f"{self.enemy_pokemon.species.name.upper()} was\nadded to party!"
                    })
                else:
                    steps.append({
                        "type": "message",
                        "text": "Party is full!\n(PC not implemented)"
                    })

            steps.append({"type": "catch_end", "caught": True})
            self._start_sequence(steps, "end")
            return

        steps.append({
            "type": "message",
            "text": f"{self.enemy_pokemon.species.name.upper()}\nbroke free!"
        })
        steps.append({"type": "catch_end", "caught": False})
        steps.append({"type": "enemy_attack"})
        self._start_sequence(steps, "battle_menu")

    def _handle_item_result(self, result):
        """Handle results from using an item in battle."""
        if not result.success:
            self.battle_menu.activate()
            self.phase = "battle_menu"
            self.awaiting_input = True
            return

        if result.action and result.action.get("type") == "catch":
            action = result.action
            self._attempt_catch_with_ball(
                action.get("ball_name", "POKE BALL"),
                action.get("ball_bonus", 1),
                action.get("force_catch", False),
                action.get("ball_item_id"),
                action.get("ball_sprite")
            )
            return

        for message in result.messages:
            self._queue_message(message)

        self.post_message_phase = "enemy_turn"
        self._show_next_message()

    def _handle_bag_cancel(self) -> None:
        self.battle_menu.activate()
        self.phase = "battle_menu"
        self.awaiting_input = True

    def _handle_party_cancel(self) -> None:
        self.battle_menu.activate()
        self.phase = "battle_menu"
        self.awaiting_input = True

    def _handle_run_attempt(self) -> None:
        if self._attempt_escape():
            self._start_sequence(
                [{"type": "message", "text": "Got away safely!"}],
                "end"
            )
            return

        self._start_sequence(
            [{"type": "message", "text": "Can't escape!"}],
            "enemy_attack"
        )

    def _attempt_escape(self) -> bool:
        self.escape_attempts += 1

        player_speed = self._get_escape_speed(self.player_pokemon)
        enemy_speed = self._get_escape_speed(self.enemy_pokemon)

        if player_speed >= enemy_speed:
            return True

        divisor = enemy_speed // 4
        if divisor == 0 or divisor % 256 == 0:
            return True

        odds = ((player_speed * 32) // divisor) % 256
        odds += 30 * self.escape_attempts

        if odds > 255:
            return True

        import random
        return random.randint(0, 255) < odds

    def _get_escape_speed(self, pokemon: Pokemon) -> int:
        speed = pokemon.stats.speed
        speed *= pokemon.stat_stages.get_multiplier("speed")
        from src.battle.status_effects import StatusCondition
        if pokemon.status == StatusCondition.PARALYSIS:
            speed = speed // 4
        return max(1, int(speed))

    def _start_enemy_attack_sequence(self) -> None:
        if not self.enemy_pokemon.moves:
            self._start_sequence(
                [{"type": "message", "text": "Enemy has no moves!"}],
                "battle_menu"
            )
            return

        enemy_move_id = self.enemy_pokemon.moves[0]
        enemy_move = self.move_loader.get_move(enemy_move_id)
        attack = AttackData(self.enemy_pokemon, self.player_pokemon, enemy_move, False)
        steps = self._build_attack_steps(attack, False)
        steps.append({"type": "end_status"})
        self._start_sequence(steps, "battle_menu")

    def _mark_seen(self) -> None:
        if hasattr(self, "pokedex_seen"):
            self.pokedex_seen.add(self.enemy_pokemon.species.species_id)

    def _mark_caught(self) -> None:
        if hasattr(self, "pokedex_caught"):
            self.pokedex_caught.add(self.enemy_pokemon.species.species_id)
        if hasattr(self, "pokedex_seen"):
            self.pokedex_seen.add(self.enemy_pokemon.species.species_id)

    def _apply_status_after_hit(self, target: Pokemon, move: Move) -> str | None:
        if not move.meta or not move.meta.ailment or move.meta.ailment == "none":
            return None

        from src.battle.status_effects import StatusCondition
        if target.status is not None and target.status != StatusCondition.NONE:
            return None

        if move.meta.ailment_chance > 0:
            import random
            if random.randint(1, 100) > move.meta.ailment_chance:
                return None

        status_map = {
            "paralysis": StatusCondition.PARALYSIS,
            "burn": StatusCondition.BURN,
            "freeze": StatusCondition.FREEZE,
            "poison": StatusCondition.POISON,
            "sleep": StatusCondition.SLEEP,
            "badly-poison": StatusCondition.BADLY_POISON
        }

        condition = status_map.get(move.meta.ailment)
        if condition and target.apply_status(condition):
            status_name = move.meta.ailment.upper()
            return f"{target.species.name.upper()} was\n{status_name}!"

        return None

    def _check_status_before_move(self, pokemon: Pokemon) -> tuple[bool, list[str]]:
        from src.battle.status_effects import StatusCondition

        if pokemon.status == StatusCondition.PARALYSIS:
            import random
            if random.randint(1, 4) == 1:
                return True, [f"{pokemon.species.name.upper()} is\nparalyzed!"]

        if pokemon.status == StatusCondition.SLEEP:
            pokemon.status_turns -= 1
            if pokemon.status_turns > 0:
                return True, [f"{pokemon.species.name.upper()} is\nfast asleep!"]
            pokemon.status = None
            return False, [f"{pokemon.species.name.upper()} woke up!"]

        if pokemon.status == StatusCondition.FREEZE:
            return True, [f"{pokemon.species.name.upper()} is\nfrozen solid!"]

        return False, []

    def _apply_stat_changes_messages(self, target: Pokemon, stat_changes: list) -> list[str]:
        messages = []
        for stat_change in stat_changes:
            changed, msg = target.apply_stat_change(stat_change.stat, stat_change.change)
            stat_display = stat_change.stat.upper()

            if changed:
                modifier = "sharply " if abs(stat_change.change) >= 2 else ""
                direction = "rose" if stat_change.change > 0 else "fell"
                messages.append(f"{target.species.name.upper()}'s\n{stat_display} {modifier}{direction}!")
            else:
                if stat_change.change > 0:
                    messages.append(f"{target.species.name.upper()}'s {stat_display}\nwon't go higher!")
                else:
                    messages.append(f"{target.species.name.upper()}'s {stat_display}\nwon't go lower!")

        return messages

    def _build_end_status_steps(self) -> list[dict]:
        steps: list[dict] = []
        from src.battle.status_effects import StatusCondition

        for pokemon in (self.player_pokemon, self.enemy_pokemon):
            if pokemon.is_fainted():
                continue

            def after_tick(pokemon=pokemon) -> list[dict]:
                if pokemon.is_fainted():
                    self._handle_fainted(pokemon)
                return []

            if pokemon.status == StatusCondition.BURN:
                damage = max(1, pokemon.stats.hp // 16)
                steps.append({"type": "message", "text": f"{pokemon.species.name.upper()} was\nhurt by burn!"})
                steps.append({"type": "damage", "target": pokemon, "amount": damage, "after_tick": after_tick})

            elif pokemon.status == StatusCondition.POISON:
                damage = max(1, pokemon.stats.hp // 16)
                steps.append({"type": "message", "text": f"{pokemon.species.name.upper()} was\nhurt by poison!"})
                steps.append({"type": "damage", "target": pokemon, "amount": damage, "after_tick": after_tick})

            elif pokemon.status == StatusCondition.BADLY_POISON:
                pokemon.status_turns += 1
                damage = max(1, (pokemon.stats.hp // 16) * pokemon.status_turns)
                steps.append({"type": "message", "text": f"{pokemon.species.name.upper()} was\nbadly poisoned!"})
                steps.append({"type": "damage", "target": pokemon, "amount": damage, "after_tick": after_tick})

        return steps

    def _handle_fainted(self, fainted: Pokemon) -> None:
        self.sequence_active = False
        self.sequence_steps = []
        self.sequence_step_type = None
        self.attack_animation_target = None
        self.hp_tick_target = None
        self.pending_after_tick = None
        self.show_message = False
        self.awaiting_input = False
        self.flinch_target = None

        if fainted is self.enemy_pokemon:
            self._queue_message(f"Wild {self.enemy_pokemon.species.name.upper()}\nfainted!")
            self._handle_victory()
            return

        if fainted is self.player_pokemon:
            self._queue_message(f"{self.player_pokemon.species.name.upper()}\nfainted!")
            self._handle_player_faint()

    def _handle_player_faint(self) -> None:
        if hasattr(self, 'party') and self.party.has_alive_pokemon():
            self._queue_message("Choose next POK\u00e9MON!")
            self._show_next_message()

            from src.states.party_state import PartyState
            party_state = PartyState(self.game, self.party, mode="forced_switch")
            self.game.push_state(party_state)
        else:
            self._queue_message("You have no more\nPOK\u00e9MON!")
            self._queue_message("You blacked out!")
            self._show_next_message()
            self.phase = "end"

    def _determine_turn_order(self, player_move: Move, enemy_move: Move) -> list[str]:
        """
        Determine who goes first based on priority and speed.

        Returns:
            List of ["player", "enemy"] or ["enemy", "player"]
        """
        # Compare priority
        if player_move.priority > enemy_move.priority:
            return ["player", "enemy"]
        elif enemy_move.priority > player_move.priority:
            return ["enemy", "player"]

        # Same priority: compare speed
        player_speed = self.player_pokemon.stats.speed
        enemy_speed = self.enemy_pokemon.stats.speed

        # Apply speed stat stage modifiers
        player_speed *= self.player_pokemon.stat_stages.get_multiplier("speed")
        enemy_speed *= self.enemy_pokemon.stat_stages.get_multiplier("speed")

        if player_speed > enemy_speed:
            return ["player", "enemy"]
        elif enemy_speed > player_speed:
            return ["enemy", "player"]
        else:
            # Speed tie: 50/50 random
            import random
            return random.choice([["player", "enemy"], ["enemy", "player"]])

    def _execute_attack(
        self,
        attacker: Pokemon,
        defender: Pokemon,
        move: Move,
        is_player: bool
    ) -> tuple[bool, bool]:
        """
        Execute an attack from attacker to defender.

        Args:
            attacker: Pokemon attacking
            defender: Pokemon defending
            move: Move being used
            is_player: True if attacker is player's Pokemon

        Returns:
            Tuple of (executed, flinched)
        """
        attacker_name = attacker.species.name.upper()
        prefix = "" if is_player else "Wild "

        blocked, status_messages = self._check_status_before_move(attacker)
        for message in status_messages:
            self._queue_message(message)
        if blocked:
            return (False, False)

        # Check accuracy
        if not self.damage_calculator.check_accuracy(attacker, defender, move):
            self._queue_message(f"{prefix}{attacker_name} used\n{move.name.upper()}!")
            self._queue_message(f"{attacker_name}'s\nattack missed!")
            return (True, False)

        # Check for critical hit
        is_crit = self.damage_calculator.check_critical_hit(attacker, move)

        # Calculate damage (multi-hit moves may strike multiple times)
        hit_count = self.damage_calculator.get_hit_count(move)
        total_damage = 0

        for _ in range(hit_count):
            damage = self.damage_calculator.calculate_damage(
                attacker,
                defender,
                move,
                is_crit
            )
            defender.take_damage(damage)
            total_damage += damage

            if defender.is_fainted():
                break

        # Queue attack messages
        self._queue_message(f"{prefix}{attacker_name} used\n{move.name.upper()}!")
        if is_crit:
            self._queue_message("Critical hit!")
        if hit_count > 1:
            self._queue_message(f"Hit {hit_count} times!")

        # Apply status condition to defender
        status_message = self._apply_status_after_hit(defender, move)
        if status_message:
            self._queue_message(status_message)

        # Apply stat changes (most moves affect the user)
        if move.stat_changes:
            for message in self._apply_stat_changes_messages(attacker, move.stat_changes):
                self._queue_message(message)

        # Drain/healing effects
        if move.meta:
            if move.meta.drain > 0 and total_damage > 0:
                heal_amount = int(total_damage * move.meta.drain / 100)
                attacker.current_hp = min(attacker.current_hp + heal_amount, attacker.stats.hp)
                self._queue_message(f"{attacker_name}\ndrained HP!")

            if move.meta.healing > 0:
                heal_amount = int(attacker.stats.hp * move.meta.healing / 100)
                attacker.current_hp = min(attacker.current_hp + heal_amount, attacker.stats.hp)
                self._queue_message(f"{attacker_name}\nregained health!")

        # Flinch (only matters if defender hasn't acted yet this turn)
        flinched = False
        if move.meta and move.meta.flinch_chance > 0 and not defender.is_fainted():
            import random
            if random.randint(1, 100) <= move.meta.flinch_chance:
                flinched = True

        return (True, flinched)

    def _execute_player_attack(self, move: Move):
        """
        Execute player's attack (with priority-based turn order).

        Args:
            move: Move to use
        """
        self.awaiting_input = False
        self.battle_menu.deactivate()
        if self.move_menu:
            self.move_menu.deactivate()

        if not self.player_pokemon.use_move_pp(move.move_id):
            self._start_sequence(
                [{"type": "message", "text": "No PP left!"}],
                "battle_menu"
            )
            return

        if move.move_id in self.player_move_pp:
            self.player_move_pp[move.move_id] -= 1

        if not self.enemy_pokemon.moves:
            self._start_sequence(
                [{"type": "message", "text": "Enemy has no moves!"}],
                "battle_menu"
            )
            return

        enemy_move_id = self.enemy_pokemon.moves[0]
        enemy_move = self.move_loader.get_move(enemy_move_id)
        turn_order = self._determine_turn_order(move, enemy_move)
        steps = self._build_turn_steps(turn_order, move, enemy_move)
        self._start_sequence(steps, "battle_menu")

    def _execute_enemy_attack(self):
        """
        Enemy attack (no longer used - attacks handled by turn order in _execute_player_attack).
        This method is kept for backward compatibility with the phase system.
        """
        # Both attacks are now executed in _execute_player_attack() based on priority
        # This phase should not be reached anymore, but if it is, just continue to next turn
        self.awaiting_input = False
        self.battle_menu.activate()
        self.phase = "battle_menu"
        self.awaiting_input = True

    def _end_battle(self):
        """End the battle and return to overworld."""
        self.game.pop_state()
