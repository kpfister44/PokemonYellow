# Phase 7: Advanced Battle Mechanics - Implementation Plan

## Overview
Implement complete battle system with menus, status effects, stat changes, accuracy, critical hits, priority, experience/leveling, catching, and trainer battles. All data is fetched from PokéAPI.

**Total Tasks:** 30
**Completed:** 30 (100%)
**Remaining:** 0 (0%)

**Status (2026-01-09):** Phase 7 complete. Catching is wired to `RUN` as a placeholder, and trainer battles currently trigger on A-button interaction (not line-of-sight).

---

## Status Summary

### ✅ Completed Phases

#### Phase 7.1: Data Hydration & Data Structures
- [x] Update hydration script to fetch move meta and stat_changes from PokéAPI
- [x] Update Move dataclass with MoveMeta and StatChange
- [x] Update MoveLoader to parse new meta fields
- [x] Create status_effects.py with StatusCondition enum
- [x] Create stat_stages.py with StatStages class
- [x] Update Pokemon class with status and stat_stages fields
- [x] Run hydration script and verify YAML output

**Files Modified:**
- `scripts/hydrate_data.py` - Fetches meta object and stat_changes array
- `src/battle/move.py` - Added MoveMeta and StatChange dataclasses
- `src/battle/status_effects.py` - StatusCondition enum
- `src/battle/stat_stages.py` - Gen 1 stat stage tracking
- `src/battle/pokemon.py` - Added status, status_turns, stat_stages, apply_status(), apply_stat_change()
- `data/moves/moves.yaml` - Regenerated with meta and stat_changes for all 165 Gen 1 moves

#### Phase 7.2: Battle Menu & Move Selection UI
- [x] Create battle_menu.py with BattleMenu component
- [x] Create move_menu.py with MoveMenu component
- [x] Update BattleState with menu integration

**Files Created:**
- `src/ui/battle_menu.py` - FIGHT/ITEM/PKM/RUN 2x2 grid menu
- `src/ui/move_menu.py` - Move selection with PP display

**Files Modified:**
- `src/states/battle_state.py` - Integrated menus, PP tracking, menu navigation

#### Phase 7.8: Message Queue System
- [x] Add message queue system to BattleState

**Implementation:**
- Message queue for sequential messages
- `_queue_message()` and `_show_next_message()` methods
- Proper phase transitions after messages
- A button advances through messages

---

## ✅ Completed Phases (7.3–7.7)

### Phase 7.3: Core Battle Mechanics (6 tasks)

#### Task 1: Implement accuracy system in damage_calculator
**File:** `src/battle/damage_calculator.py`

Add method:
```python
def check_accuracy(self, attacker: Pokemon, defender: Pokemon, move: Move) -> bool:
    """
    Roll accuracy check considering move accuracy and stat stages.

    Returns:
        True if attack hits, False if misses
    """
    if move.accuracy is None:
        return True  # Never-miss moves (e.g., Swift)

    # Get stat stage modifiers
    acc_stage = attacker.stat_stages.accuracy
    eva_stage = defender.stat_stages.evasion

    # Gen 1: Accuracy = move_accuracy * acc_multiplier / eva_multiplier
    acc_mult = attacker.stat_stages.get_multiplier("accuracy")
    eva_mult = defender.stat_stages.get_multiplier("evasion")

    threshold = int(move.accuracy * acc_mult / eva_mult)

    # Roll 0-99, hit if roll < threshold
    import random
    return random.randint(0, 99) < threshold
```

Update `_execute_player_attack()` and `_execute_enemy_attack()` in BattleState:
```python
# Before calculating damage
if not self.damage_calculator.check_accuracy(attacker, defender, move):
    self._queue_message(f"{attacker.species.name.upper()}'s\nattack missed!")
    self._show_next_message()
    return
```

#### Task 2: Implement critical hit system
**File:** `src/battle/damage_calculator.py`

Add method:
```python
def check_critical_hit(self, attacker: Pokemon, move: Move) -> bool:
    """
    Gen 1 critical hit mechanics based on speed and move crit_rate.

    Returns:
        True if critical hit
    """
    crit_rate_boost = move.meta.crit_rate if move.meta else 0

    # Gen 1: base_rate = speed / 512, high-crit moves = speed / 64
    if crit_rate_boost > 0:
        threshold = attacker.stats.speed / 64
    else:
        threshold = attacker.stats.speed / 512

    import random
    return random.random() < min(threshold, 0.255)  # Cap at 255/256
```

Update `calculate_damage()` signature:
```python
def calculate_damage(self, attacker: Pokemon, defender: Pokemon, move: Move, is_critical: bool = False) -> int:
```

In damage formula:
```python
if is_critical:
    # Critical hits ignore attacker's negative stages and defender's positive stages
    # Use max(stage, 0) for attacker, min(stage, 0) for defender
    # Also double damage in Gen 1 (2x multiplier)
    damage = int(damage * 2)
```

Update battle attacks:
```python
is_crit = self.damage_calculator.check_critical_hit(attacker, move)
damage = self.damage_calculator.calculate_damage(attacker, defender, move, is_crit)

if is_crit:
    self._queue_message("Critical hit!")
```

#### Task 3: Implement priority-based turn order
**File:** `src/states/battle_state.py`

Add method:
```python
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
```

Refactor attack execution to use turn order:
```python
# In _execute_player_attack(), store player's move
self.player_selected_move = move

# After move selection, get enemy's move and determine order
enemy_move_id = self.enemy_pokemon.moves[0]
enemy_move = self.move_loader.get_move(enemy_move_id)

turn_order = self._determine_turn_order(move, enemy_move)

# Execute attacks in order
for attacker_name in turn_order:
    if attacker_name == "player":
        # Execute player attack logic
    else:
        # Execute enemy attack logic

    # Check for fainting after each attack
    if self.enemy_pokemon.is_fainted() or self.player_pokemon.is_fainted():
        break
```

#### Task 4: Implement status effect application and checks
**File:** `src/states/battle_state.py`

Add methods:
```python
def _apply_status_condition(self, target: Pokemon, move: Move) -> bool:
    """
    Roll chance and apply status if successful.

    Returns:
        True if status was applied
    """
    if not move.meta or not move.meta.ailment or move.meta.ailment == "none":
        return False

    # Check if target already has status
    if target.status is not None and target.status != StatusCondition.NONE:
        return False

    # Roll for ailment chance (if not 100%)
    if move.meta.ailment_chance > 0:
        import random
        if random.randint(1, 100) > move.meta.ailment_chance:
            return False

    # Apply status
    from src.battle.status_effects import StatusCondition

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
```

Update attack execution:
```python
# Before executing move
if self._apply_status_effects_before_move(attacker):
    return  # Move blocked

# After dealing damage
self._apply_status_condition(defender, move)

# At end of turn (after both Pokemon have moved)
self._apply_status_effects_end_of_turn(self.player_pokemon)
self._apply_status_effects_end_of_turn(self.enemy_pokemon)
```

Also update damage calculation for burn:
```python
# In DamageCalculator.calculate_damage()
if attacker.status == StatusCondition.BURN and move.is_physical():
    damage = damage // 2  # Burn halves physical attack damage
```

#### Task 5: Implement stat stage changes system
**File:** `src/states/battle_state.py`

Add method:
```python
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
```

Update attack execution:
```python
# After dealing damage and applying status
if move.stat_changes:
    # Determine target (most moves affect user, some affect opponent)
    # For now, assume all stat changes affect the user
    self._apply_stat_changes(attacker, move.stat_changes, attacker.species.name.upper())
```

Update damage calculation to use stat stages:
```python
# In DamageCalculator.calculate_damage()
# Apply stat stage multipliers
attack_stat = attacker.stats.attack * attacker.stat_stages.get_multiplier("attack")
defense_stat = defender.stats.defense * defender.stat_stages.get_multiplier("defense")
special_stat = attacker.stats.special * attacker.stat_stages.get_multiplier("special")

# Use modified stats in damage formula
```

#### Task 6: Update DamageCalculator to support all mechanics
**File:** `src/battle/damage_calculator.py`

The damage calculator needs to be updated throughout Tasks 1-5 to support:
- Accuracy checks (Task 1)
- Critical hits (Task 2)
- Stat stage modifiers (Task 5)
- Status effect damage modifiers (Task 4)

---

### Phase 7.4: Advanced Move Effects (3 tasks)

#### Task 7: Implement drain and healing move effects
**File:** `src/states/battle_state.py`

Update attack execution:
```python
# After dealing damage
if move.meta:
    if move.meta.drain > 0:
        # Drain HP (e.g., Absorb, Mega Drain)
        heal_amount = int(damage * move.meta.drain / 100)
        attacker.current_hp = min(attacker.current_hp + heal_amount, attacker.stats.hp)
        self._queue_message(f"{attacker.species.name.upper()}\ndrained HP!")

    if move.meta.healing > 0:
        # Self-healing (e.g., Recover, Softboiled)
        heal_amount = int(attacker.stats.hp * move.meta.healing / 100)
        attacker.current_hp = min(attacker.current_hp + heal_amount, attacker.stats.hp)
        self._queue_message(f"{attacker.species.name.upper()}\nregained health!")
```

#### Task 8: Implement multi-hit moves
**File:** `src/battle/damage_calculator.py`

Add method:
```python
def get_hit_count(self, move: Move) -> int:
    """
    Determine number of hits for multi-hit moves.

    Returns:
        Number of hits (1 for normal moves)
    """
    if not move.meta or move.meta.min_hits is None:
        return 1

    # 2-hit moves always hit 2x
    if move.meta.min_hits == 2 and move.meta.max_hits == 2:
        return 2

    # 2-5 hit moves use Gen 1 distribution
    if move.meta.min_hits == 2 and move.meta.max_hits == 5:
        # 37.5% 2 hits, 37.5% 3 hits, 12.5% 4 hits, 12.5% 5 hits
        import random
        roll = random.randint(0, 7)
        if roll < 3:
            return 2
        elif roll < 6:
            return 3
        elif roll == 6:
            return 4
        else:
            return 5

    return 1
```

Update attack execution:
```python
hit_count = self.damage_calculator.get_hit_count(move)

for hit in range(hit_count):
    damage = self.damage_calculator.calculate_damage(attacker, defender, move, is_crit)
    defender.take_damage(damage)

    # Check for fainting after each hit
    if defender.is_fainted():
        break

if hit_count > 1:
    self._queue_message(f"Hit {hit_count} times!")
```

#### Task 9: Implement flinch mechanic
**File:** `src/states/battle_state.py`

Add field to `__init__`:
```python
self.player_flinched = False
self.enemy_flinched = False
```

After attack execution:
```python
# Check for flinch
if move.meta and move.meta.flinch_chance > 0:
    import random
    if random.randint(1, 100) <= move.meta.flinch_chance:
        if defender == self.player_pokemon:
            self.player_flinched = True
        else:
            self.enemy_flinched = True
```

Before executing move:
```python
# Check flinch
if attacker == self.player_pokemon and self.player_flinched:
    self._queue_message(f"{attacker.species.name.upper()} flinched!")
    self.player_flinched = False
    return  # Skip turn

if attacker == self.enemy_pokemon and self.enemy_flinched:
    self._queue_message(f"{attacker.species.name.upper()} flinched!")
    self.enemy_flinched = False
    return  # Skip turn
```

---

### Phase 7.5: Experience & Leveling (3 tasks)

#### Task 10: Create experience_calculator.py
**File:** `src/battle/experience_calculator.py` (NEW)

```python
# ABOUTME: Experience calculation for Pokemon battles
# ABOUTME: Implements Gen 1 experience formulas and level-up requirements

from src.battle.pokemon import Pokemon
from src.battle.species import Species


class ExperienceCalculator:
    """Calculate experience gain and level-up requirements."""

    def calculate_exp_gain(self, defeated: Pokemon, is_wild: bool, participated: int) -> int:
        """
        Calculate experience gain using Gen 1 formula.

        Args:
            defeated: Defeated Pokemon
            is_wild: True for wild battles, False for trainer battles
            participated: Number of Pokemon that participated

        Returns:
            Experience points gained
        """
        base = defeated.species.base_experience
        level = defeated.level

        # Gen 1: Trainer battles give 1.5x
        trainer_mod = 1.5 if not is_wild else 1.0

        # Divide by participants (if exp share is implemented later)
        exp = int((base * level / 7) * trainer_mod / participated)

        return exp

    def get_exp_for_level(self, growth_rate: str, level: int) -> int:
        """
        Calculate total EXP needed to reach level.

        Args:
            growth_rate: Growth rate name (fast, medium-fast, medium-slow, slow)
            level: Target level

        Returns:
            Total experience required
        """
        n = level

        if growth_rate == "fast":
            return int((4 * n ** 3) / 5)
        elif growth_rate == "medium-fast" or growth_rate == "medium":
            return n ** 3
        elif growth_rate == "medium-slow":
            return int((6 * n ** 3 / 5) - (15 * n ** 2) + (100 * n) - 140)
        elif growth_rate == "slow":
            return int((5 * n ** 3) / 4)
        else:
            # Default to medium-fast
            return n ** 3
```

#### Task 11: Add experience tracking to Pokemon
**File:** `src/battle/pokemon.py`

Update `__init__`:
```python
# Experience tracking
self.experience: int = 0
self._update_exp_requirements()
```

Add methods:
```python
def _update_exp_requirements(self):
    """Update experience required for next level."""
    from src.battle.experience_calculator import ExperienceCalculator

    calc = ExperienceCalculator()
    current_level_exp = calc.get_exp_for_level(self.species.growth_rate, self.level)
    next_level_exp = calc.get_exp_for_level(self.species.growth_rate, self.level + 1)

    # Set experience to minimum for current level if not set
    if self.experience == 0:
        self.experience = current_level_exp

    self.exp_to_next_level = next_level_exp

def gain_experience(self, amount: int) -> bool:
    """
    Add experience and check for level up.

    Args:
        amount: Experience points to add

    Returns:
        True if Pokemon leveled up
    """
    self.experience += amount

    if self.experience >= self.exp_to_next_level:
        return True

    return False

def level_up(self):
    """Increase level and recalculate stats."""
    self.level += 1

    # Recalculate stats with new level
    old_stats = self.stats
    self.stats = self._calculate_stats()

    # Full heal on level up
    self.current_hp = self.stats.hp

    # Update exp requirements
    self._update_exp_requirements()

    # Learn new moves at this level
    # TODO: Implement move learning in Phase 8

    return old_stats  # Return for displaying stat increases
```

#### Task 12: Add level-up sequence to BattleState
**File:** `src/states/battle_state.py`

Add phase: `"level_up"` to phase list

Update `_advance_turn()`:
```python
def _handle_victory(self):
    """Handle victory and award experience."""
    from src.battle.experience_calculator import ExperienceCalculator

    calc = ExperienceCalculator()
    exp_gain = calc.calculate_exp_gain(
        defeated=self.enemy_pokemon,
        is_wild=True,
        participated=1
    )

    # Queue experience message
    self._queue_message(f"{self.player_pokemon.species.name.upper()}\ngained {exp_gain} EXP!")

    # Check for level up
    if self.player_pokemon.gain_experience(exp_gain):
        self.phase = "level_up"
        self._show_next_message()
    else:
        self._show_next_message()
        self.phase = "end"

def _handle_level_up(self):
    """Handle level up sequence."""
    old_stats = self.player_pokemon.level_up()

    # Show level up message
    self._queue_message(f"{self.player_pokemon.species.name.upper()}\ngrew to Lv.{self.player_pokemon.level}!")

    # Show stat increases (optional - can be detailed or simple)
    stat_increases = [
        f"HP +{self.player_pokemon.stats.hp - old_stats.hp}",
        f"ATK +{self.player_pokemon.stats.attack - old_stats.attack}",
        f"DEF +{self.player_pokemon.stats.defense - old_stats.defense}",
    ]

    # Queue stat increase messages if desired
    # self._queue_message("\n".join(stat_increases[:2]))

    self._show_next_message()
    self.phase = "end"
```

Update input handling for level_up phase:
```python
elif self.phase == "level_up":
    if input_handler.is_just_pressed("a"):
        self._handle_level_up()
```

Call `_handle_victory()` when enemy faints:
```python
if self.enemy_pokemon.is_fainted():
    self._queue_message(f"Wild {self.enemy_pokemon.species.name.upper()}\nfainted!")
    self._handle_victory()
    return
```

---

### Phase 7.6: Catching Mechanics (2 tasks)

#### Task 13: Create catch_calculator.py
**File:** `src/battle/catch_calculator.py` (NEW)

```python
# ABOUTME: Pokemon catching calculation for wild battles
# ABOUTME: Implements Gen 1 catch rate formula with status modifiers

from src.battle.pokemon import Pokemon
from src.battle.status_effects import StatusCondition
import random


class CatchCalculator:
    """Gen 1 catch rate formula."""

    def calculate_catch_chance(self, pokemon: Pokemon, ball_bonus: int = 1) -> tuple[bool, int]:
        """
        Calculate catch success using Gen 1 formula.

        Args:
            pokemon: Wild Pokemon to catch
            ball_bonus: Pokeball type modifier (1 = regular, 1.5 = Great, 2 = Ultra)

        Returns:
            Tuple of (caught: bool, shakes: int)
            - caught: True if Pokemon was caught
            - shakes: Number of shakes before breaking free (0-4)
        """
        catch_rate = pokemon.species.capture_rate

        # HP factor: lower HP = easier to catch
        hp_factor = (pokemon.stats.hp * 255 * 4) // (pokemon.current_hp * 12)

        # Status modifiers (Gen 1)
        status_bonus = 0
        if pokemon.status in [StatusCondition.SLEEP, StatusCondition.FREEZE]:
            status_bonus = 25
        elif pokemon.status in [StatusCondition.PARALYSIS, StatusCondition.BURN, StatusCondition.POISON]:
            status_bonus = 12

        # Calculate catch value
        a = min(int((catch_rate + status_bonus) * hp_factor * ball_bonus / 255), 255)

        # Gen 1: 4 shake checks
        shakes = 0
        for shake in range(4):
            if random.randint(0, 255) >= a:
                return (False, shakes)
            shakes += 1

        return (True, 4)
```

#### Task 14: Add catching sequence to BattleState
**File:** `src/states/battle_state.py`

Add phases: `"throwing_ball"`, `"catch_result"`

Update battle menu to show BALL option in wild battles:
```python
# In _handle_battle_menu_selection()
elif selection == "RUN":
    # Instead of always running, show options
    # For now, just add catch option when implemented
    # TODO: Create sub-menu for RUN/BALL options
    pass
```

Add catch methods:
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
        self._queue_message("...")  # Shake animation placeholder

    if caught:
        self._queue_message(f"Gotcha!\n{self.enemy_pokemon.species.name.upper()} was caught!")
        # TODO: Add to party (Phase 8)
        self.phase = "end"
    else:
        self._queue_message(f"{self.enemy_pokemon.species.name.upper()}\nbroke free!")
        # Continue to enemy turn
        self.phase = "enemy_turn"

    self._show_next_message()
```

Note: Full catching requires party management (Phase 8), so for now just show messages.

---

### Phase 7.7: Trainer Battles (5 tasks)

#### Task 15: Create trainer.py
**File:** `src/battle/trainer.py` (NEW)

```python
# ABOUTME: Trainer data structure for NPC battles
# ABOUTME: Defines trainer info and Pokemon teams

from dataclasses import dataclass
from src.battle.pokemon import Pokemon
from src.battle.species_loader import SpeciesLoader


@dataclass
class Trainer:
    """NPC trainer with Pokemon team."""
    name: str
    trainer_class: str  # "Bug Catcher", "Lass", "Youngster", etc.
    team: list[dict]  # [{species_id: str, level: int}, ...]
    prize_money: int

    def get_party(self, species_loader: SpeciesLoader) -> list[Pokemon]:
        """
        Build Pokemon instances from team data.

        Args:
            species_loader: SpeciesLoader instance

        Returns:
            List of Pokemon instances
        """
        party = []
        for pokemon_data in self.team:
            species = species_loader.get_species(pokemon_data['species_id'])
            pokemon = Pokemon(species, pokemon_data['level'])
            party.append(pokemon)

        return party
```

#### Task 16: Update NPC to support trainer battles
**File:** `src/overworld/npc.py`

Add fields:
```python
self.is_trainer: bool = False
self.trainer_data: Optional[dict] = None
self.defeated: bool = False  # Track if trainer has been beaten
```

Update `__init__` to accept trainer data:
```python
def __init__(self, npc_id, x, y, dialog=None, facing="down", is_trainer=False, trainer_data=None):
    # ... existing code ...
    self.is_trainer = is_trainer
    self.trainer_data = trainer_data
    self.defeated = False
```

#### Task 17: Update BattleState with trainer battle support
**File:** `src/states/battle_state.py`

Update `__init__` signature:
```python
def __init__(self, game, player_pokemon: Pokemon, enemy_pokemon: Pokemon,
             is_trainer_battle: bool = False, trainer = None,
             trainer_pokemon_remaining: list[Pokemon] = None):
```

Add fields:
```python
self.is_trainer_battle = is_trainer_battle
self.trainer = trainer
self.trainer_pokemon_remaining = trainer_pokemon_remaining or []
```

Update intro message:
```python
if self.is_trainer_battle:
    self.message = f"{self.trainer.trainer_class}\n{self.trainer.name} wants to fight!"
else:
    self.message = f"Wild {enemy_pokemon.species.name.upper()}\nappeared!"
```

Update RUN handling:
```python
elif selection == "RUN":
    if self.is_trainer_battle:
        self._queue_message("Can't run from a\ntrainer battle!")
        self._show_next_message()
        self.battle_menu.activate()
        self.phase = "battle_menu"
    else:
        self._queue_message("Got away safely!")
        self._show_next_message()
        self.phase = "end"
```

Update victory handling:
```python
def _handle_victory(self):
    """Handle victory and switch Pokemon if trainer battle."""
    if self.is_trainer_battle and self.trainer_pokemon_remaining:
        # Trainer sends out next Pokemon
        self.enemy_pokemon = self.trainer_pokemon_remaining.pop(0)

        # Load new sprite
        if self.enemy_pokemon.species.sprites and self.enemy_pokemon.species.sprites.front:
            self.enemy_sprite = self.game.renderer.load_sprite(
                self.enemy_pokemon.species.sprites.front
            )

        self._queue_message(f"{self.trainer.name} sent out\n{self.enemy_pokemon.species.name.upper()}!")
        self._show_next_message()

        # Reset to battle menu
        self.battle_menu.activate()
        self.phase = "battle_menu"
        self.awaiting_input = True
    else:
        # Award experience and end battle
        # ... existing victory code ...
        pass
```

#### Task 18: Update overworld to trigger trainer battles
**File:** `src/states/overworld_state.py`

Update NPC interaction:
```python
def _check_npc_interaction(self):
    """Check for NPC interaction when A is pressed."""
    # ... existing dialog code ...

    # Check if NPC is trainer
    if npc.is_trainer and not npc.defeated:
        from src.battle.trainer import Trainer
        from src.battle.species_loader import SpeciesLoader

        # Build trainer
        trainer = Trainer(
            name=npc.trainer_data['name'],
            trainer_class=npc.trainer_data['class'],
            team=npc.trainer_data['team'],
            prize_money=npc.trainer_data.get('prize_money', 0)
        )

        # Build trainer's party
        species_loader = SpeciesLoader()
        trainer_party = trainer.get_party(species_loader)

        # Start trainer battle
        from src.states.battle_state import BattleState

        battle_state = BattleState(
            self.game,
            self.player_pokemon,  # Player's first Pokemon
            trainer_party[0],  # Trainer's first Pokemon
            is_trainer_battle=True,
            trainer=trainer,
            trainer_pokemon_remaining=trainer_party[1:]
        )

        self.game.push_state(battle_state)
        npc.defeated = True
```

#### Task 19: Add trainer NPCs to route_1.json
**File:** `data/maps/route_1.json`

Add trainer NPCs to the map data:
```json
{
  "npcs": [
    {
      "id": "youngster_1",
      "x": 5,
      "y": 15,
      "facing": "down",
      "is_trainer": true,
      "trainer": {
        "name": "Timmy",
        "class": "Youngster",
        "team": [
          {"species_id": "rattata", "level": 3},
          {"species_id": "rattata", "level": 3}
        ],
        "prize_money": 60
      }
    },
    {
      "id": "bug_catcher_1",
      "x": 5,
      "y": 20,
      "facing": "left",
      "is_trainer": true,
      "trainer": {
        "name": "Rick",
        "class": "Bug Catcher",
        "team": [
          {"species_id": "weedle", "level": 4},
          {"species_id": "kakuna", "level": 4}
        ],
        "prize_money": 40
      }
    }
  ]
}
```

---

## Testing Checklist

### What Can Be Tested Now (Completed Features)

✅ **Phase 7.1 Data:**
- [ ] Run `uv run python -c "from src.battle.move_loader import MoveLoader; ml = MoveLoader(); m = ml.get_move('thunder-wave'); print(f'✓ Thunder Wave ailment: {m.meta.ailment}')"`
- [ ] Run `uv run python -c "from src.battle.move_loader import MoveLoader; ml = MoveLoader(); m = ml.get_move('swords-dance'); print(f'✓ Swords Dance stat changes: {m.stat_changes}')"`
- [ ] Run `uv run python -c "from src.battle.pokemon import Pokemon; from src.battle.species_loader import SpeciesLoader; sl = SpeciesLoader(); s = sl.get_species('pikachu'); p = Pokemon(s, 5); print(f'✓ Pokemon status: {p.status}, stat_stages: {p.stat_stages}')"`

✅ **Phase 7.2 & 7.8 Battle Menus:**
- [ ] Run game: `uv run python -m src.main`
- [ ] Walk on grass in Route 1 until encounter triggers
- [ ] **Verify intro:** See "Wild [POKEMON] appeared!" message
- [ ] Press Z to dismiss message
- [ ] **Verify battle menu:** See 2x2 grid with FIGHT/ITEM/PKM/RUN
- [ ] **Test navigation:** Use arrow keys to move cursor (should wrap around)
- [ ] **Test ITEM:** Select ITEM, see "Items not implemented yet!" message
- [ ] **Test PKM:** Select PKM, see "Party switching not implemented yet!" message
- [ ] **Test RUN:** Select RUN, see "Got away safely!", battle ends
- [ ] **Test FIGHT:** Select FIGHT, see move selection menu
- [ ] **Verify move menu:** Shows move name, type, and PP (e.g., "TACKLE PP 35/35")
- [ ] Press up/down arrows to change move selection
- [ ] Press B to cancel, should return to battle menu
- [ ] Select FIGHT again, select a move
- [ ] **Verify attack:** See "[POKEMON] used [MOVE]!" message
- [ ] Press Z to dismiss
- [ ] **Verify enemy turn:** See "Wild [POKEMON] used [MOVE]!" message
- [ ] **Verify turn flow:** After enemy attack, battle menu reappears
- [ ] Continue attacking until Pokemon faints
- [ ] **Verify faint:** See "[POKEMON] fainted!" message, battle ends

### What to Test After Each Remaining Phase

**Phase 7.3 (Core Mechanics):**
- [ ] Accuracy: Use low-accuracy moves (Sand Attack), verify misses occur
- [ ] Critical hits: Attack repeatedly, see "Critical hit!" message occasionally
- [ ] Priority: Use Quick Attack, verify it goes first even when slower
- [ ] Status - Paralysis: Use Thunder Wave, see paralysis message, verify 25% move failure
- [ ] Status - Burn: Use Ember, see burn message, verify end-of-turn damage
- [ ] Status - Sleep: Use Hypnosis, verify Pokemon sleeps 1-7 turns
- [ ] Stat changes: Use Swords Dance, see "ATTACK rose!", verify increased damage

**Phase 7.4 (Move Effects):**
- [ ] Drain: Use Absorb, verify attacker heals
- [ ] Multi-hit: Use Double Kick, see "Hit 2 times!" message
- [ ] Flinch: Use Stomp, verify occasional flinch (prevents next move)

**Phase 7.5 (Experience):**
- [ ] Win battle, see "[POKEMON] gained [X] EXP!" message
- [ ] Win multiple battles until level up
- [ ] See "grew to Lv.[X]!" message
- [ ] Verify stats increased after level up

**Phase 7.6 (Catching):**
- [ ] In wild battle, use BALL option (when implemented)
- [ ] See "Used POKE BALL!" message
- [ ] See shake messages ("...")
- [ ] Verify low HP increases catch rate
- [ ] Verify status conditions improve catch rate

**Phase 7.7 (Trainers):**
- [ ] Walk near trainer NPC, battle triggers automatically
- [ ] See "[CLASS] [NAME] wants to fight!" intro
- [ ] Try to RUN, see "Can't run from a trainer battle!"
- [ ] Defeat first Pokemon
- [ ] See "[NAME] sent out [POKEMON]!" message
- [ ] Continue until all trainer Pokemon defeated
- [ ] Verify experience awarded after final Pokemon

---

## Current Code Patterns to Follow

### Battle State Phases
```python
# Valid phases:
"intro" → "showing_message" → "battle_menu" → "move_selection" →
"showing_message" → "enemy_turn" → "showing_message" → "battle_menu" ...
→ "end"
```

### Message Queue Usage
```python
# Add messages
self._queue_message("Message text here")
self._queue_message("Second message")

# Show first message (automatically advances through queue)
self._show_next_message()

# User presses A to see next message
# When queue is empty, _advance_turn() is called automatically
```

### Move Execution Pattern
```python
def _execute_player_attack(self, move: Move):
    self.awaiting_input = False

    # 1. Deduct PP
    # 2. Check accuracy (Phase 7.3)
    # 3. Check critical hit (Phase 7.3)
    # 4. Calculate damage
    # 5. Apply damage
    # 6. Queue attack message
    # 7. Apply status effects (Phase 7.3)
    # 8. Apply stat changes (Phase 7.3)
    # 9. Apply drain/healing (Phase 7.4)
    # 10. Show messages

    self._show_next_message()
```

### Accessing Move Data
```python
# Move has meta and stat_changes
if move.meta:
    ailment = move.meta.ailment  # "paralysis", "burn", etc.
    drain = move.meta.drain  # 50 for Absorb (50% drain)
    crit_rate = move.meta.crit_rate  # 0 or higher

if move.stat_changes:
    for stat_change in move.stat_changes:
        stat_name = stat_change.stat  # "attack", "defense", etc.
        change_amount = stat_change.change  # -6 to +6
```

### Pokemon Status and Stat Stages
```python
# Apply status
from src.battle.status_effects import StatusCondition
if pokemon.apply_status(StatusCondition.PARALYSIS):
    print("Status applied!")

# Apply stat change
changed, msg = pokemon.apply_stat_change("attack", 2)
if changed:
    print(f"Attack {msg}")  # "sharply rose"

# Get stat multiplier
multiplier = pokemon.stat_stages.get_multiplier("attack")
modified_attack = pokemon.stats.attack * multiplier
```

---

## Key Files Reference

### Core Battle Files
- `src/states/battle_state.py` - Main battle state (364 lines)
- `src/battle/damage_calculator.py` - Damage calculation
- `src/battle/pokemon.py` - Pokemon instances
- `src/battle/move.py` - Move data structures
- `src/battle/species.py` - Species data structures

### New Data Structures
- `src/battle/status_effects.py` - StatusCondition enum
- `src/battle/stat_stages.py` - Stat stage tracking
- `src/ui/battle_menu.py` - Battle menu component
- `src/ui/move_menu.py` - Move selection component

### Data Files
- `data/moves/moves.yaml` - 165 moves with meta and stat_changes
- `data/pokemon/species.yaml` - 151 Pokemon with complete data

---

## Implementation Notes

### Gen 1 Accuracy
- **Status permanence:** Paralysis, burn, poison, freeze are permanent (no turn limit except sleep)
- **Stat stages:** Use numerator/denominator ratios (not percentages)
  - Stage +1 = 3/2 = 1.5x, Stage -1 = 2/3 = 0.67x
- **Critical hits:** Ignore attacker's negative stages and defender's positive stages
- **Speed ties:** 50/50 random choice
- **Type chart:** Has bugs (e.g., Psychic has no weaknesses due to Ghost immunity bug)

### Priority Ranges
- -7: Roar, Whirlwind
- -6: Teleport
- -1: Vital Throw (Gen 2+)
- 0: Most moves
- +1: Quick Attack, Mach Punch
- +2: Extreme Speed (Gen 2+)

### Catch Rate Formula
Uses 4 shake checks (not the modern single-check formula)

---

## Development Workflow

1. **Test imports:** After creating new files, test imports work
2. **Implement incrementally:** Complete one task at a time
3. **Test after each task:** Use manual testing checklist
4. **Commit frequently:** Small atomic commits after each completed task
5. **Run the game:** Test in-game after UI changes

---

## Commands Reference

```bash
# Run game
uv run python -m src.main

# Test imports
uv run python -c "from src.states.battle_state import BattleState; print('✓ OK')"

# Test move loading
uv run python -c "from src.battle.move_loader import MoveLoader; ml = MoveLoader(); print(ml.get_move('thunder-wave').meta)"

# Check data structure
uv run python scripts/check_encounter_data.py
```

---

## Next Session Checklist

1. Read this file
2. Review current git status
3. Test completed features (Phase 7.1, 7.2, 7.8)
4. Start with Phase 7.3 Task 1 (accuracy system)
5. Work through tasks sequentially
6. Test after each task
7. Commit after each completed phase

Good luck! The foundation is solid. 🎮
