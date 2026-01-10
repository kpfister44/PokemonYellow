# ABOUTME: Overworld state for exploring towns and routes
# ABOUTME: Manages map rendering, player control, and camera following

from src.states.base_state import BaseState
from src.overworld.map import Map
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


class OverworldState(BaseState):
    """State for overworld exploration (towns, routes, etc)."""

    def __init__(self, game, map_path, player_start_x=5, player_start_y=5):
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
        self.player_was_moving = False  # Track movement state for encounter checking

        # Initialize party with starter Pokemon (Pikachu for Yellow)
        from src.party.party import Party
        self.party = Party()

        # Add starter Pokemon
        species_loader = SpeciesLoader()
        pikachu_species = species_loader.get_species("pikachu")
        self.player_pokemon = Pokemon(pikachu_species, 5)
        self.party.add(self.player_pokemon)

    def enter(self):
        """Called when entering this state."""
        # Skip initialization if already loaded (resuming from another state)
        if self.current_map is not None:
            return

        # Load the map
        self.current_map = Map(self.map_path, self.game.renderer)

        # Create player
        self.player = Player(self.player_start_x, self.player_start_y)

        # Load NPCs from map data
        self.npcs = []
        npc_data = self.current_map.map_data.get("npcs", [])
        for npc_info in npc_data:
            npc = NPC(
                npc_info["id"],
                npc_info["tile_x"],
                npc_info["tile_y"],
                npc_info.get("direction", "down"),
                npc_info.get("dialog", "..."),
                npc_info.get("is_trainer", False),
                npc_info.get("trainer")
            )
            self.npcs.append(npc)

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
        map_path = f"data/maps/{map_name}.json"

        # Load new map
        self.current_map = Map(map_path, self.game.renderer)

        # Load NPCs from new map
        self.npcs = []
        npc_data = self.current_map.map_data.get("npcs", [])
        for npc_info in npc_data:
            npc = NPC(
                npc_info["id"],
                npc_info["tile_x"],
                npc_info["tile_y"],
                npc_info.get("direction", "down"),
                npc_info.get("dialog", "..."),
                npc_info.get("is_trainer", False),
                npc_info.get("trainer")
            )
            self.npcs.append(npc)

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
            npc = self._get_npc_in_front()
            if npc:
                if npc.is_trainer and not npc.defeated:
                    self._start_trainer_battle(npc)
                else:
                    dialog_text = npc.interact()
                    self.active_dialog = DialogBox(dialog_text, npc.npc_id)
                return

        # Normal player movement
        self.player.handle_input(input_handler, self.current_map, self.npcs)

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
        if not self.player.is_moving:
            warp = self.current_map.get_warp_at(self.player.tile_x, self.player.tile_y)
            if warp:
                # Only process "route" warps for Phase 4 (ignore "door" warps)
                if warp.get("warp_type") == "route":
                    self.switch_map(
                        warp["target_map"],
                        warp["target_x"],
                        warp["target_y"]
                    )

        # Check for wild encounters after player finishes moving on grass
        if not self.player.is_moving and self.player_was_moving:
            # Player just stopped moving - check for encounter
            encounter_zone = encounter_zones.get_encounter_zone(self.current_map.map_name)
            if encounter_zone:
                # Get the ground tile the player is standing on
                ground_tile_id = self.current_map.ground_layer[self.player.tile_y][self.player.tile_x]

                if encounter_zone.is_grass_tile(ground_tile_id):
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

        self.game.push_state(battle_state)
        npc.defeated = True

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
        map_surface = self.current_map.render(camera_x, camera_y)
        renderer.draw_surface(map_surface, (0, 0))

        # Render NPCs (same layer as player)
        for npc in self.npcs:
            npc.render(renderer, camera_x, camera_y)

        # Render the player
        self.player.render(renderer, camera_x, camera_y)

        # Render dialog on top of everything
        if self.active_dialog:
            self.active_dialog.render(renderer)
