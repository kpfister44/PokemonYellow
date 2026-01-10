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
from src.battle.catch_calculator import CatchCalculator


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
        self.phase = "intro"  # intro, showing_message, battle_menu, move_selection, enemy_turn, throwing_ball, catch_result, level_up, end
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
            elif self.phase == "level_up":
                self._handle_level_up()
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
            # Open party screen in switch mode
            if hasattr(self, 'party'):
                from src.states.party_state import PartyState
                party_state = PartyState(self.game, self.party, mode="switch")
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
                # For now, use catch flow as placeholder for RUN
                self._attempt_catch()

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
            self._handle_victory()
            return

        if self.player_pokemon.is_fainted():
            self._queue_message(f"{self.player_pokemon.species.name.upper()}\nfainted!")
            self._show_next_message()
            self.phase = "end"
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
        if self.is_trainer_battle and self.trainer_pokemon_remaining:
            self.enemy_pokemon = self.trainer_pokemon_remaining.pop(0)

            if self.enemy_pokemon.species.sprites and self.enemy_pokemon.species.sprites.front:
                self.enemy_sprite = self.game.renderer.load_sprite(
                    self.enemy_pokemon.species.sprites.front
                )

            self._queue_message(
                f"{self.trainer.name} sent out\n{self.enemy_pokemon.species.name.upper()}!"
            )
            self._show_next_message()

            self.battle_menu.activate()
            self.phase = "battle_menu"
            self.awaiting_input = True
            return

        from src.battle.experience_calculator import ExperienceCalculator

        calc = ExperienceCalculator()
        exp_gain = calc.calculate_exp_gain(
            defeated=self.enemy_pokemon,
            is_wild=not self.is_trainer_battle,
            participated=1
        )

        self._queue_message(f"{self.player_pokemon.species.name.upper()}\ngained {exp_gain} EXP!")

        if self.player_pokemon.gain_experience(exp_gain):
            self.phase = "level_up"
            self._show_next_message()
        else:
            self._show_next_message()
            self.phase = "end"

    def _handle_level_up(self):
        """Handle level up sequence."""
        old_stats = self.player_pokemon.level_up()

        self._queue_message(
            f"{self.player_pokemon.species.name.upper()}\ngrew to Lv.{self.player_pokemon.level}!"
        )

        self._show_next_message()
        self.phase = "end"

    def _attempt_catch(self):
        """Attempt to catch wild Pokemon."""
        self.phase = "throwing_ball"
        self._queue_message("Used POKE BALL!")

        calc = CatchCalculator()
        caught, shakes = calc.calculate_catch_chance(self.enemy_pokemon, ball_bonus=1)

        for _ in range(shakes):
            self._queue_message("...")

        if caught:
            self._queue_message(
                f"Gotcha!\n{self.enemy_pokemon.species.name.upper()} was caught!"
            )
            self.post_message_phase = "end"
        else:
            self._queue_message(
                f"{self.enemy_pokemon.species.name.upper()}\nbroke free!"
            )
            self.post_message_phase = "enemy_turn"

        self._show_next_message()

    def _apply_status_condition(self, target: Pokemon, move: Move) -> bool:
        """
        Roll chance and apply status if successful.

        Returns:
            True if status was applied
        """
        if not move.meta or not move.meta.ailment or move.meta.ailment == "none":
            return False

        # Check if target already has status
        from src.battle.status_effects import StatusCondition
        if target.status is not None and target.status != StatusCondition.NONE:
            return False

        # Roll for ailment chance (if not 100%)
        if move.meta.ailment_chance > 0:
            import random
            if random.randint(1, 100) > move.meta.ailment_chance:
                return False

        # Apply status
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
            self._queue_message(f"{target.species.name.upper()} was\n{status_name}!")
            return True

        return False

    def _apply_status_effects_before_move(self, pokemon: Pokemon) -> bool:
        """
        Check if status prevents move (paralysis, sleep, freeze).

        Returns:
            True if move is blocked
        """
        from src.battle.status_effects import StatusCondition

        if pokemon.status == StatusCondition.PARALYSIS:
            # 25% chance to be fully paralyzed
            import random
            if random.randint(1, 4) == 1:
                self._queue_message(f"{pokemon.species.name.upper()} is\nparalyzed!")
                return True

        elif pokemon.status == StatusCondition.SLEEP:
            pokemon.status_turns -= 1
            if pokemon.status_turns > 0:
                self._queue_message(f"{pokemon.species.name.upper()} is\nfast asleep!")
                return True
            else:
                pokemon.status = None
                self._queue_message(f"{pokemon.species.name.upper()} woke up!")

        elif pokemon.status == StatusCondition.FREEZE:
            # Gen 1: freeze is permanent unless hit by fire move
            self._queue_message(f"{pokemon.species.name.upper()} is\nfrozen solid!")
            return True

        return False

    def _apply_stat_changes(self, target: Pokemon, stat_changes: list, target_name: str):
        """Apply stat stage modifications from move."""
        from src.battle.move import StatChange

        for stat_change in stat_changes:
            changed, msg = target.apply_stat_change(stat_change.stat, stat_change.change)

            if changed:
                # Format stat name for display
                stat_display = stat_change.stat.upper()

                # Gen 1 messages
                if abs(stat_change.change) >= 2:
                    modifier = "sharply "
                else:
                    modifier = ""

                direction = "rose" if stat_change.change > 0 else "fell"

                self._queue_message(f"{target_name}'s\n{stat_display} {modifier}{direction}!")
            else:
                # Already at limit
                if stat_change.change > 0:
                    self._queue_message(f"{target_name}'s {stat_display}\nwon't go higher!")
                else:
                    self._queue_message(f"{target_name}'s {stat_display}\nwon't go lower!")

    def _apply_status_effects_end_of_turn(self, pokemon: Pokemon):
        """Apply poison/burn damage at end of turn."""
        from src.battle.status_effects import StatusCondition

        if pokemon.status == StatusCondition.BURN:
            damage = pokemon.stats.hp // 16
            pokemon.take_damage(max(1, damage))
            self._queue_message(f"{pokemon.species.name.upper()} was\nhurt by burn!")

        elif pokemon.status == StatusCondition.POISON:
            damage = pokemon.stats.hp // 16
            pokemon.take_damage(max(1, damage))
            self._queue_message(f"{pokemon.species.name.upper()} was\nhurt by poison!")

        elif pokemon.status == StatusCondition.BADLY_POISON:
            # Toxic: damage increases each turn (1/16, 2/16, 3/16, etc.)
            pokemon.status_turns += 1
            damage = (pokemon.stats.hp // 16) * pokemon.status_turns
            pokemon.take_damage(max(1, damage))
            self._queue_message(f"{pokemon.species.name.upper()} was\nbadly poisoned!")

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

        # Check if status prevents move (paralysis, sleep, freeze)
        if self._apply_status_effects_before_move(attacker):
            return (False, False)  # Move blocked by status

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
        self._apply_status_condition(defender, move)

        # Apply stat changes (most moves affect the user)
        if move.stat_changes:
            self._apply_stat_changes(attacker, move.stat_changes, attacker_name)

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

        # Deduct PP
        if not self.player_pokemon.use_move_pp(move.move_id):
            self._queue_message("No PP left!")
            self._show_next_message()
            return

        # Also deduct from local tracking for move menu display
        if move.move_id in self.player_move_pp:
            self.player_move_pp[move.move_id] -= 1

        # Get enemy's move
        enemy_move_id = self.enemy_pokemon.moves[0]
        enemy_move = self.move_loader.get_move(enemy_move_id)

        # Determine turn order based on priority and speed
        turn_order = self._determine_turn_order(move, enemy_move)

        # Execute attacks in order
        flinch_target = None
        for index, attacker_name in enumerate(turn_order):
            if attacker_name == "player":
                if flinch_target == "player":
                    self._queue_message(f"{self.player_pokemon.species.name.upper()} flinched!")
                    flinch_target = None
                    continue

                _, flinched = self._execute_attack(
                    self.player_pokemon,
                    self.enemy_pokemon,
                    move,
                    is_player=True
                )

                if index == 0 and flinched:
                    flinch_target = "enemy"
            else:
                if flinch_target == "enemy":
                    self._queue_message(f"{self.enemy_pokemon.species.name.upper()} flinched!")
                    flinch_target = None
                    continue

                _, flinched = self._execute_attack(
                    self.enemy_pokemon,
                    self.player_pokemon,
                    enemy_move,
                    is_player=False
                )

                if index == 0 and flinched:
                    flinch_target = "player"

            # Check for fainting after each attack
            if self.enemy_pokemon.is_fainted() or self.player_pokemon.is_fainted():
                break

        # Apply end-of-turn status effects (poison/burn damage)
        if not self.player_pokemon.is_fainted():
            self._apply_status_effects_end_of_turn(self.player_pokemon)
        if not self.enemy_pokemon.is_fainted():
            self._apply_status_effects_end_of_turn(self.enemy_pokemon)

        # Show messages
        self._show_next_message()

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
