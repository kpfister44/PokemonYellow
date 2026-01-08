# ABOUTME: Overworld state for exploring towns and routes
# ABOUTME: Manages map rendering, player control, and camera following

from src.states.base_state import BaseState
from src.overworld.map import Map
from src.overworld.camera import Camera
from src.overworld.player import Player
from src.engine import constants


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
        self.player_start_x = player_start_x
        self.player_start_y = player_start_y

    def enter(self):
        """Called when entering this state."""
        # Load the map
        self.current_map = Map(self.map_path, self.game.renderer)

        # Create player
        self.player = Player(self.player_start_x, self.player_start_y)

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

    def handle_input(self, input_handler):
        """
        Handle player input.

        Args:
            input_handler: Input instance with current input state
        """
        # Let player handle input
        self.player.handle_input(input_handler, self.current_map)

    def update(self, dt):
        """
        Update overworld state.

        Args:
            dt: Delta time in seconds
        """
        # Update player
        self.player.update()

        # Update camera to follow player
        player_pixel_x, player_pixel_y = self.player.get_pixel_position()
        self.camera.center_on(
            player_pixel_x + constants.TILE_SIZE // 2,
            player_pixel_y + constants.TILE_SIZE // 2
        )

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

        # Render the player
        self.player.render(renderer, camera_x, camera_y)
