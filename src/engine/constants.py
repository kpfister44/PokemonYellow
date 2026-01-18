# ABOUTME: Core game constants for Pokemon Yellow recreation
# ABOUTME: Defines screen resolution, tile size, FPS, colors, and input mappings

import pygame

# Display settings (expanded viewport at 32x32 tiles)
GAME_WIDTH = 480
GAME_HEIGHT = 416
SCALE_FACTOR = 2
WINDOW_WIDTH = GAME_WIDTH * SCALE_FACTOR  # 960
WINDOW_HEIGHT = GAME_HEIGHT * SCALE_FACTOR  # 832

# UI scaling (2x for menus and dialog)
UI_SCALE = 2

# Tile and grid settings
TILE_SIZE = 32
TILES_WIDE = GAME_WIDTH // TILE_SIZE  # 15 tiles
TILES_HIGH = GAME_HEIGHT // TILE_SIZE  # 13 tiles

# Frame rate
FPS = 60

# Game Boy color palette (grayscale for authentic look)
COLOR_DARKEST = (15, 56, 15)      # Dark green (GB darkest)
COLOR_DARK = (48, 98, 48)         # Medium-dark green
COLOR_LIGHT = (139, 172, 15)      # Light green
COLOR_LIGHTEST = (155, 188, 15)   # Lightest green (GB white)
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)

# Additional colors for UI and debugging
COLOR_RED = (255, 0, 0)
COLOR_BLUE = (0, 0, 255)
COLOR_DEBUG = (255, 0, 255)  # Magenta for debug visuals

# Input key mappings
KEY_UP = pygame.K_UP
KEY_DOWN = pygame.K_DOWN
KEY_LEFT = pygame.K_LEFT
KEY_RIGHT = pygame.K_RIGHT
KEY_A = pygame.K_z          # Confirm/Interact
KEY_B = pygame.K_x          # Cancel/Back
KEY_START = pygame.K_s       # Menu
KEY_SELECT = pygame.K_LSHIFT # Future use

# Movement speed (pixels per frame when moving)
# Player moves one tile (32 pixels) over 8 frames
MOVEMENT_SPEED = 4  # 32 pixels / 8 frames = 4 pixels per frame

# Directions (for entity facing and movement)
DIR_UP = 0
DIR_DOWN = 1
DIR_LEFT = 2
DIR_RIGHT = 3

# Animation settings
ANIMATION_FRAME_DURATION = 8  # Frames per animation frame
