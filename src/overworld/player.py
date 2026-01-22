# ABOUTME: Player character class with movement and collision
# ABOUTME: Handles player input, grid-based movement, and pylletTown-style animation

import os
import pygame
from src.engine import constants
from src.overworld.entity import Entity, SpriteSheet


PLAYER_SPRITE_PATH = os.path.join("assets", "sprites", "player", "red.png")


class Player(Entity):
    """Player character controlled by user input (pylletTown-style animation)."""

    def __init__(self, tile_x, tile_y):
        """
        Initialize the player.

        Args:
            tile_x: Starting tile X coordinate
            tile_y: Starting tile Y coordinate
        """
        super().__init__(tile_x, tile_y, sprite_surface=None)
        self.sprite_sheet = SpriteSheet(PLAYER_SPRITE_PATH)
        self.sprite_sheet.set_orientation(self.direction)

    def render(self, renderer, camera_x, camera_y):
        """Render the player using the current sprite frame."""
        frame = self.sprite_sheet.get_current_frame()
        screen_x = self.pixel_x - camera_x
        screen_y = self.pixel_y - camera_y
        renderer.draw_surface(frame, (screen_x, screen_y))

    def handle_input(self, input_handler, current_map, npcs=None, item_pickups=None):
        """
        Handle player input for movement (pylletTown-style with hold delay).

        Args:
            input_handler: Input instance with current input state
            current_map: Map instance for collision checking
            npcs: Optional list of NPCs to check for collision
            item_pickups: Optional list of item pickups to check for collision

        Returns:
            True if player attempted to move, False otherwise
        """
        # Get direction from input
        direction = input_handler.get_direction()

        # No direction key pressed
        if direction is None:
            self.hold_time = 0
            self.step = 'right_foot'
            return False

        # Don't accept new direction input while walking
        if self.is_moving:
            return False

        # Turn to face direction if different
        if self.direction != direction:
            self.direction = direction
            self.sprite_sheet.set_orientation(direction)
            self.hold_time = 0  # Reset hold counter on direction change

        # Accumulate hold frames
        self.hold_time += 1

        # Start walking after hold threshold
        if self.hold_time >= self.HOLD_FRAMES_THRESHOLD:
            target_x, target_y = self._get_target_tile(direction)

            # Check collisions
            if not self._can_move_to(target_x, target_y, current_map, npcs, item_pickups):
                return False

            # Start moving
            self.start_move(direction)
            return True

        return False

    def _can_move_to(self, target_x, target_y, current_map, npcs, item_pickups):
        """Check if player can move to target position."""
        if not current_map.is_walkable(target_x, target_y):
            return False

        if npcs:
            for npc in npcs:
                if npc.tile_x == target_x and npc.tile_y == target_y:
                    return False

        if item_pickups:
            for pickup in item_pickups:
                if pickup.tile_x == target_x and pickup.tile_y == target_y:
                    return False

        return True

    def _get_target_tile(self, direction):
        """Get the target tile position for a given direction."""
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
        """Update player state (movement, animation) pylletTown-style."""
        if not self.is_moving:
            return

        # Move pixels
        self.update_movement(speed=constants.MOVEMENT_SPEED)

        # Switch to walking sprite at halfway point
        if self.move_progress == constants.METATILE_SIZE // 2:
            # Alternate feet for up/down directions
            if (self.direction == constants.DIR_UP or
                    self.direction == constants.DIR_DOWN) and self.step == 'left_foot':
                self.sprite_sheet.flip_horizontal()
                self.step = 'right_foot'
            else:
                self.sprite_sheet.set_walking_frame()
                self.step = 'left_foot'

        # Reset sprite when movement completes
        if not self.is_moving:
            self.sprite_sheet.set_orientation(self.direction)

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
        player.pixel_x = player.tile_x * constants.METATILE_SIZE
        player.pixel_y = player.tile_y * constants.METATILE_SIZE
        player.is_moving = False
        player.move_progress = 0
        player.target_tile_x = player.tile_x
        player.target_tile_y = player.tile_y
        return player
