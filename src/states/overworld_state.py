# ABOUTME: Overworld state for exploring towns and routes
# ABOUTME: Manages map rendering, player control, and camera following

from src.states.base_state import BaseState
from src.overworld.map import Map
from src.overworld.camera import Camera
from src.engine import constants


class OverworldState(BaseState):
    """State for overworld exploration (towns, routes, etc)."""

    def __init__(self, game, map_path):
        """
        Initialize the overworld state.

        Args:
            game: Reference to the Game instance
            map_path: Path to the map JSON file to load
        """
        super().__init__(game)
        self.map_path = map_path
        self.current_map = None
        self.camera = None

        # Camera control (for testing, will be player-controlled later)
        self.camera_x = 0
        self.camera_y = 0

    def enter(self):
        """Called when entering this state."""
        # Load the map
        self.current_map = Map(self.map_path, self.game.renderer)

        # Create camera
        map_width = self.current_map.get_width_pixels()
        map_height = self.current_map.get_height_pixels()
        self.camera = Camera(map_width, map_height)

        # Start camera centered on map (or at 0,0 if map is small)
        self.camera.center_on(map_width // 2, map_height // 2)

        print(f"Loaded map: {self.map_path}")
        print(f"Map size: {self.current_map.width}x{self.current_map.height} tiles")
        print(f"Map size: {map_width}x{map_height} pixels")

    def exit(self):
        """Called when exiting this state."""
        pass

    def handle_input(self, input_handler):
        """
        Handle input for camera control (temporary - will be player control).

        Args:
            input_handler: Input instance with current input state
        """
        # Camera movement for testing (2 pixels per frame)
        camera_speed = 2

        if input_handler.is_pressed("up"):
            self.camera.y -= camera_speed
        if input_handler.is_pressed("down"):
            self.camera.y += camera_speed
        if input_handler.is_pressed("left"):
            self.camera.x -= camera_speed
        if input_handler.is_pressed("right"):
            self.camera.x += camera_speed

        # Clamp camera to bounds
        self.camera.clamp_to_bounds()

    def update(self, dt):
        """
        Update overworld state.

        Args:
            dt: Delta time in seconds
        """
        # Nothing to update yet (player movement will go here in Phase 3)
        pass

    def render(self, renderer):
        """
        Render the overworld.

        Args:
            renderer: Renderer instance
        """
        # Clear screen
        renderer.clear(constants.COLOR_BLACK)

        # Render the map with camera offset
        camera_x, camera_y = self.camera.get_offset()
        map_surface = self.current_map.render(camera_x, camera_y)
        renderer.draw_surface(map_surface, (0, 0))
