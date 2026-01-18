# ABOUTME: Player character class with movement and collision
# ABOUTME: Handles player input, grid-based movement, and map collision detection

import pygame
from src.engine import constants
from src.overworld.entity import Entity


class Player(Entity):
    """Player character controlled by user input."""

    def __init__(self, tile_x, tile_y):
        """
        Initialize the player.

        Args:
            tile_x: Starting tile X coordinate
            tile_y: Starting tile Y coordinate
        """
        # Create placeholder sprite (will be replaced with actual sprite later)
        sprite = self._create_placeholder_sprite()
        super().__init__(tile_x, tile_y, sprite)

    def _create_placeholder_sprite(self):
        """Create a simple placeholder sprite for the player."""
        sprite = pygame.Surface((constants.TILE_SIZE, constants.TILE_SIZE))
        sprite.fill(constants.COLOR_LIGHTEST)  # Light background

        # Draw a simple character shape
        pygame.draw.circle(
            sprite,
            (255, 200, 0),  # Yellow (Pikachu-ish)
            (constants.TILE_SIZE // 2, constants.TILE_SIZE // 2),
            constants.TILE_SIZE // 3
        )

        return sprite

    def handle_input(self, input_handler, current_map, npcs=None, item_pickups=None):
        """
        Handle player input for movement.

        Args:
            input_handler: Input instance with current input state
            current_map: Map instance for collision checking
            npcs: Optional list of NPCs to check for collision
            item_pickups: Optional list of item pickups to check for collision

        Returns:
            True if player attempted to move, False otherwise
        """
        # Don't accept input while moving
        if self.is_moving:
            return False

        # Get direction from input
        direction = input_handler.get_direction()
        if direction is None:
            return False

        # Check if we can move in that direction
        target_x, target_y = self._get_target_tile(direction)

        # Check map collision
        if not current_map.is_walkable(target_x, target_y):
            # Just turn to face that direction
            self.direction = direction
            return False

        # Check NPC collision
        if npcs:
            for npc in npcs:
                if npc.tile_x == target_x and npc.tile_y == target_y:
                    # Just turn to face that direction
                    self.direction = direction
                    return False

        # Check item pickup collision
        if item_pickups:
            for pickup in item_pickups:
                if pickup.tile_x == target_x and pickup.tile_y == target_y:
                    # Just turn to face that direction
                    self.direction = direction
                    return False

        # All clear, start moving
        self.start_move(direction)
        return True

    def _get_target_tile(self, direction):
        """
        Get the target tile position for a given direction.

        Args:
            direction: Direction constant

        Returns:
            Tuple of (target_x, target_y)
        """
        target_x = self.tile_x
        target_y = self.tile_y

        if direction == constants.DIR_UP:
            target_y -= 1
        elif direction == constants.DIR_DOWN:
            target_y += 1
        elif direction == constants.DIR_LEFT:
            target_x -= 1
        elif direction == constants.DIR_RIGHT:
            target_x += 1

        return (target_x, target_y)

    def update(self):
        """Update player state (movement, animation)."""
        if self.is_moving:
            self.update_movement(speed=constants.MOVEMENT_SPEED)
            self.update_animation()

    def to_dict(self) -> dict:
        """Serialize player position and direction."""
        direction_map = {
            constants.DIR_UP: "up",
            constants.DIR_DOWN: "down",
            constants.DIR_LEFT: "left",
            constants.DIR_RIGHT: "right"
        }
        return {
            "tile_x": self.tile_x,
            "tile_y": self.tile_y,
            "direction": direction_map.get(self.direction, "down")
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Player":
        """Deserialize player position and direction."""
        player = cls(data.get("tile_x", 0), data.get("tile_y", 0))
        direction_map = {
            "up": constants.DIR_UP,
            "down": constants.DIR_DOWN,
            "left": constants.DIR_LEFT,
            "right": constants.DIR_RIGHT
        }
        player.direction = direction_map.get(data.get("direction"), constants.DIR_DOWN)
        player.pixel_x = player.tile_x * constants.TILE_SIZE
        player.pixel_y = player.tile_y * constants.TILE_SIZE
        player.is_moving = False
        player.move_progress = 0
        player.target_tile_x = player.tile_x
        player.target_tile_y = player.tile_y
        return player
