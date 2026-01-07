# ABOUTME: Input handling system for keyboard events
# ABOUTME: Maps keyboard keys to game actions and tracks key states

import pygame
from src.engine import constants


class Input:
    """Handles keyboard input and maps keys to game actions."""

    def __init__(self):
        """Initialize input state tracking."""
        # Track which keys are currently pressed
        self.keys_pressed = {
            "up": False,
            "down": False,
            "left": False,
            "right": False,
            "a": False,
            "b": False,
            "start": False,
            "select": False,
        }

        # Track keys that were just pressed this frame (for single press detection)
        self.keys_just_pressed = {
            "up": False,
            "down": False,
            "left": False,
            "right": False,
            "a": False,
            "b": False,
            "start": False,
            "select": False,
        }

    def update(self, events):
        """Process pygame events and update input state."""
        # Reset just_pressed states
        for key in self.keys_just_pressed:
            self.keys_just_pressed[key] = False

        # Get current key states
        keys = pygame.key.get_pressed()

        # Update held keys
        old_pressed = self.keys_pressed.copy()

        self.keys_pressed["up"] = keys[constants.KEY_UP]
        self.keys_pressed["down"] = keys[constants.KEY_DOWN]
        self.keys_pressed["left"] = keys[constants.KEY_LEFT]
        self.keys_pressed["right"] = keys[constants.KEY_RIGHT]
        self.keys_pressed["a"] = keys[constants.KEY_A]
        self.keys_pressed["b"] = keys[constants.KEY_B]
        self.keys_pressed["start"] = keys[constants.KEY_START]
        self.keys_pressed["select"] = keys[constants.KEY_SELECT]

        # Detect just pressed (was not pressed before, is pressed now)
        for key in self.keys_pressed:
            if self.keys_pressed[key] and not old_pressed[key]:
                self.keys_just_pressed[key] = True

    def is_pressed(self, action):
        """Check if an action key is currently held down."""
        return self.keys_pressed.get(action, False)

    def is_just_pressed(self, action):
        """Check if an action key was just pressed this frame."""
        return self.keys_just_pressed.get(action, False)

    def get_direction(self):
        """Get the current direction pressed, or None if no direction."""
        if self.keys_pressed["up"]:
            return constants.DIR_UP
        elif self.keys_pressed["down"]:
            return constants.DIR_DOWN
        elif self.keys_pressed["left"]:
            return constants.DIR_LEFT
        elif self.keys_pressed["right"]:
            return constants.DIR_RIGHT
        return None
