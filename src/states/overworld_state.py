# ABOUTME: Overworld state for exploring towns and routes
# ABOUTME: Manages map rendering, player control, and camera following

from src.states.base_state import BaseState
from src.overworld.map import MapManager
from src.overworld.camera import Camera
from src.overworld.player import Player
from src.overworld.npc import NPC
from src.ui.dialog_box import DialogBox
from src.engine import constants
from src.overworld import encounter_zones
from src.states.battle_state import BattleState
from src.battle.pokemon import Pokemon
from src.battle.species_loader import SpeciesLoader
from src.battle.trainer import Trainer
from src.items.bag import Bag
from src.items.item_loader import ItemLoader
from src.overworld.item_pickup import ItemPickup


class OverworldState(BaseState):
    """State for overworld exploration (towns, routes, etc)."""

    def __init__(
        self,
        game,
        map_path,
        player_start_x=5,
        player_start_y=5,
        party=None,
        bag=None,
        collected_items=None,
        defeated_trainers=None,
        player_direction=None,
        pokedex_seen=None,
        pokedex_caught=None
    ):
        """
        Initialize the overworld state.

        Args:
            game: Reference to the Game instance
            map_path: Path to the map JSON file to load
            player_start_x: Player starting tile X coordinate
            player_start_y: Player starting tile Y coordinate
        """
        super().__init__(game)
        self.map_path = map_path
        self.current_map = None
        self.camera = None
        self.player = None
        self.npcs = []
        self.active_dialog = None
        self.player_start_x = player_start_x
        self.player_start_y = player_start_y
        self.player_direction = player_direction
        self.player_was_moving = False  # Track movement state for encounter checking
        self.pokedex_seen = set(pokedex_seen or [])
        self.pokedex_caught = set(pokedex_caught or [])

        # Initialize party with starter Pokemon (Pikachu for Yellow)
        from src.party.party import Party
        if party is None:
            self.party = Party()
        else:
            self.party = party
        self.bag = bag if bag is not None else Bag()
        self.item_loader = ItemLoader()
        self.item_pickups = []
        self.collected_items = set(collected_items or [])
        self.defeated_trainers = set(defeated_trainers or [])

        if party is None:
            # Add starter Pokemon
            species_loader = SpeciesLoader()
            pikachu_species = species_loader.get_species("pikachu")
            self.player_pokemon = Pokemon(pikachu_species, 5)
            self.party.add(self.player_pokemon)
            if not self.pokedex_seen and not self.pokedex_caught:
                self.pokedex_seen.add("pikachu")
                self.pokedex_caught.add("pikachu")

        for pokemon in self.party.pokemon:
            self.pokedex_seen.add(pokemon.species.species_id)
            self.pokedex_caught.add(pokemon.species.species_id)

    def enter(self):
        """Called when entering this state."""
        # Skip initialization if already loaded (resuming from another state)
        if self.current_map is not None:
            return

        # Load the map
        self.current_map = MapManager(self.map_path)

        # Use map's player_start if no explicit start position provided
        start_x = self.player_start_x
        start_y = self.player_start_y
        if self.current_map.player_start is not None:
            if start_x < 0 or start_y < 0:
                start_x, start_y = self.current_map.player_start

        # Create player
        self.player = Player(start_x, start_y)
        if self.player_direction is not None:
            direction_map = {
                "up": constants.DIR_UP,
                "down": constants.DIR_DOWN,
                "left": constants.DIR_LEFT,
                "right": constants.DIR_RIGHT
            }
            if isinstance(self.player_direction, str):
                self.player.direction = direction_map.get(self.player_direction, constants.DIR_DOWN)
            else:
                self.player.direction = self.player_direction

        # Load NPCs from TMX object layer
        self.npcs = list(self.current_map.npcs)

        self._apply_defeated_trainers()
        self._load_item_pickups()

        # Create camera
        map_width = self.current_map.get_width_pixels()
        map_height = self.current_map.get_height_pixels()
        self.camera = Camera(map_width, map_height)

        # Center camera on player
        player_pixel_x, player_pixel_y = self.player.get_pixel_position()
        self.camera.center_on(
            player_pixel_x + constants.TILE_SIZE // 2,
            player_pixel_y + constants.TILE_SIZE // 2
        )

        print(f"Loaded map: {self.map_path}")
        print(f"Map size: {self.current_map.width}x{self.current_map.height} tiles")
        print(f"Player starting position: ({self.player_start_x}, {self.player_start_y})")

    def exit(self):
        """Called when exiting this state."""
        pass

    def switch_map(self, map_name, spawn_x, spawn_y):
        """
        Switch to a different map and reposition player.

        Args:
            map_name: Name of map file (without .json extension)
            spawn_x: Tile X coordinate to spawn player
            spawn_y: Tile Y coordinate to spawn player
        """
        # Build path to new map
        map_path = self._map_path_from_name(map_name)

        # Load new map
        self.current_map = MapManager(map_path)
        self.map_path = map_path

        # Load NPCs from new map
        self.npcs = list(self.current_map.npcs)

        self._apply_defeated_trainers()
        self._load_item_pickups()

        # Reposition player (update both tile and pixel positions)
        self.player.tile_x = spawn_x
        self.player.tile_y = spawn_y
        self.player.pixel_x = spawn_x * constants.TILE_SIZE
        self.player.pixel_y = spawn_y * constants.TILE_SIZE

        # Reset movement state (safety)
        self.player.is_moving = False
        self.player.move_progress = 0
        self.player.target_tile_x = spawn_x
        self.player.target_tile_y = spawn_y

        # Update camera boundaries for new map
        map_width = self.current_map.get_width_pixels()
        map_height = self.current_map.get_height_pixels()
        self.camera.map_width = map_width
        self.camera.map_height = map_height

        # Center camera on player's new position
        player_pixel_x, player_pixel_y = self.player.get_pixel_position()
        self.camera.center_on(
            player_pixel_x + constants.TILE_SIZE // 2,
            player_pixel_y + constants.TILE_SIZE // 2
        )

    def handle_input(self, input_handler):
        """
        Handle player input.

        Args:
            input_handler: Input instance with current input state
        """
        # Open start menu
        if input_handler.is_just_pressed("start"):
            from src.states.start_menu_state import StartMenuState
            start_menu = StartMenuState(self.game, self)
            self.game.push_state(start_menu)
            return

        # If dialog is active, A button closes it
        if self.active_dialog:
            if input_handler.is_just_pressed("a"):
                self.active_dialog.close()
                self.active_dialog = None
            return  # Block other input during dialog

        # Check for NPC interaction
        if input_handler.is_just_pressed("a"):
            item_pickup = self._get_item_in_front()
            if item_pickup:
                self._collect_item(item_pickup)
                return
            npc = self._get_npc_in_front()
            if npc:
                if npc.is_trainer and not npc.defeated:
                    self._start_trainer_battle(npc)
                else:
                    dialog_text = npc.interact()
                    self.active_dialog = DialogBox(dialog_text, npc.npc_id)
                return

        # Normal player movement
        self.player.handle_input(input_handler, self.current_map, self.npcs, self.item_pickups)

    def _get_npc_in_front(self):
        """Get NPC in tile player is facing."""
        facing_x = self.player.tile_x
        facing_y = self.player.tile_y

        if self.player.direction == constants.DIR_UP:
            facing_y -= 1
        elif self.player.direction == constants.DIR_DOWN:
            facing_y += 1
        elif self.player.direction == constants.DIR_LEFT:
            facing_x -= 1
        elif self.player.direction == constants.DIR_RIGHT:
            facing_x += 1

        for npc in self.npcs:
            if npc.tile_x == facing_x and npc.tile_y == facing_y:
                return npc
        return None

    def _get_item_in_front(self):
        """Get item pickup in the tile player is facing."""
        facing_x = self.player.tile_x
        facing_y = self.player.tile_y

        if self.player.direction == constants.DIR_UP:
            facing_y -= 1
        elif self.player.direction == constants.DIR_DOWN:
            facing_y += 1
        elif self.player.direction == constants.DIR_LEFT:
            facing_x -= 1
        elif self.player.direction == constants.DIR_RIGHT:
            facing_x += 1

        for pickup in self.item_pickups:
            if pickup.tile_x == facing_x and pickup.tile_y == facing_y:
                return pickup
        return None

    def _load_item_pickups(self):
        """Load item pickups from the current map data."""
        self.item_pickups = []
        for pickup in self.current_map.item_pickups:
            key = f"{self.current_map.map_name}:{pickup.pickup_id}"
            if key in self.collected_items:
                continue
            self.item_pickups.append(pickup)

    def _map_path_from_name(self, map_name: str) -> str:
        if map_name.lower().endswith(".tmx"):
            filename = map_name
        else:
            filename = f"{map_name}.tmx"
        return f"assets/maps/{filename}"

    def _trainer_key(self, npc_id: str) -> str:
        if self.current_map:
            map_name = self.current_map.map_name
        else:
            import os
            map_name = os.path.splitext(os.path.basename(self.map_path))[0]
        return f"{map_name}:{npc_id}"

    def _apply_defeated_trainers(self):
        if not self.defeated_trainers:
            return
        for npc in self.npcs:
            if npc.is_trainer and self._trainer_key(npc.npc_id) in self.defeated_trainers:
                npc.defeated = True

    def _collect_item(self, pickup: ItemPickup):
        """Collect an item pickup and add it to the bag."""
        item = self.item_loader.get_item(pickup.item_id)

        added, reason = self.bag.add_item_with_reason(pickup.item_id)
        if not added:
            if reason == "stack_full":
                self.active_dialog = DialogBox("No more room for that item.", pickup.pickup_id)
            else:
                self.active_dialog = DialogBox("Bag is full.", pickup.pickup_id)
            return

        self.item_pickups.remove(pickup)
        key = f"{self.current_map.map_name}:{pickup.pickup_id}"
        self.collected_items.add(key)
        message = f"NAME found\n{item.name.upper()}!"
        self.active_dialog = DialogBox(message)

    def update(self, dt):
        """
        Update overworld state.

        Args:
            dt: Delta time in seconds
        """
        # Update player
        self.player.update()

        # Update NPCs
        for npc in self.npcs:
            npc.update()

        # Check for warps after player finishes moving
        if not self.player.is_moving and self.player_was_moving:
            warp = self.current_map.get_warp_at(self.player.tile_x, self.player.tile_y)
            if warp:
                self.switch_map(
                    warp["dest_map"],
                    warp["dest_x"],
                    warp["dest_y"]
                )

        # Check for wild encounters after player finishes moving on grass
        if not self.player.is_moving and self.player_was_moving:
            # Player just stopped moving - check for encounter
            encounter_zone = encounter_zones.get_encounter_zone(self.current_map.map_name)
            if encounter_zone:
                if self.current_map.is_grass(self.player.tile_x, self.player.tile_y):
                    if encounter_zone.should_encounter():
                        self._trigger_wild_battle(encounter_zone)

        # Update movement tracking
        self.player_was_moving = self.player.is_moving

        # Update camera to follow player
        player_pixel_x, player_pixel_y = self.player.get_pixel_position()
        self.camera.center_on(
            player_pixel_x + constants.TILE_SIZE // 2,
            player_pixel_y + constants.TILE_SIZE // 2
        )

    def _trigger_wild_battle(self, encounter_zone):
        """
        Trigger a wild Pokemon battle.

        Args:
            encounter_zone: EncounterZone instance
        """
        # Get random encounter
        species_id, level = encounter_zone.get_random_encounter()

        # Load species data
        species_loader = SpeciesLoader()
        species = species_loader.get_species(species_id)

        # Create wild Pokemon
        wild_pokemon = Pokemon(species, level)

        # Get player's active Pokemon from party
        player_pokemon = self.party.get_active()
        if not player_pokemon:
            # Fallback if party empty (shouldn't happen)
            player_species = species_loader.get_species("pikachu")
            player_pokemon = Pokemon(player_species, 5)

        # Push battle state
        battle_state = BattleState(self.game, player_pokemon, wild_pokemon)
        battle_state.party = self.party
        battle_state.bag = self.bag
        battle_state.pokedex_seen = self.pokedex_seen
        battle_state.pokedex_caught = self.pokedex_caught
        self.game.push_state(battle_state)

    def _start_trainer_battle(self, npc: NPC):
        """Start a trainer battle when interacting with a trainer NPC."""
        trainer_info = npc.trainer_data or {}

        trainer = Trainer(
            name=trainer_info.get("name", "Trainer"),
            trainer_class=trainer_info.get("class", "Trainer"),
            team=trainer_info.get("team", []),
            prize_money=trainer_info.get("prize_money", 0)
        )

        species_loader = SpeciesLoader()
        trainer_party = trainer.get_party(species_loader)

        # Get player's active Pokemon from party
        player_pokemon = self.party.get_active()
        if not player_pokemon:
            # Fallback if party empty (shouldn't happen)
            player_species = species_loader.get_species("pikachu")
            player_pokemon = Pokemon(player_species, 5)

        battle_state = BattleState(
            self.game,
            player_pokemon,
            trainer_party[0],
            is_trainer_battle=True,
            trainer=trainer,
            trainer_pokemon_remaining=trainer_party[1:]
        )
        battle_state.party = self.party
        battle_state.bag = self.bag
        battle_state.pokedex_seen = self.pokedex_seen
        battle_state.pokedex_caught = self.pokedex_caught

        self.game.push_state(battle_state)
        npc.defeated = True
        if npc.is_trainer:
            self.defeated_trainers.add(self._trainer_key(npc.npc_id))

    def render(self, renderer):
        """
        Render the overworld.

        Args:
            renderer: Renderer instance
        """
        # Clear screen
        renderer.clear(constants.COLOR_BLACK)

        # Get camera offset
        camera_x, camera_y = self.camera.get_offset()

        # Render the map with camera offset
        self.current_map.draw_base(renderer, camera_x, camera_y)

        renderables = []
        renderables.extend(self.item_pickups)
        renderables.extend(self.npcs)
        renderables.append(self.player)

        for entity in sorted(renderables, key=lambda item: item.get_rect().bottom):
            entity.render(renderer, camera_x, camera_y)

        self.current_map.draw_fringe(renderer, camera_x, camera_y)

        # Render dialog on top of everything
        if self.active_dialog:
            self.active_dialog.render(renderer)
