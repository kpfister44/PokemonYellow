# ABOUTME: Core game constants for Pokemon Yellow recreation
# ABOUTME: Defines screen resolution, tile size, FPS, colors, and input mappings

import pygame

# Display settings (Game Boy screen size: 160x144)
GAME_WIDTH = 160
GAME_HEIGHT = 144
SCALE_FACTOR = 3
WINDOW_WIDTH = GAME_WIDTH * SCALE_FACTOR  # 480
WINDOW_HEIGHT = GAME_HEIGHT * SCALE_FACTOR  # 432

# Tile and grid settings
TILE_SIZE = 16
TILES_WIDE = GAME_WIDTH // TILE_SIZE  # 10 tiles
TILES_HIGH = GAME_HEIGHT // TILE_SIZE  # 9 tiles

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
# Player moves one tile (16 pixels) over this many frames
MOVEMENT_SPEED = 8  # 16 pixels / 8 frames = 2 pixels per frame

# Directions (for entity facing and movement)
DIR_UP = 0
DIR_DOWN = 1
DIR_LEFT = 2
DIR_RIGHT = 3

# Animation settings
ANIMATION_FRAME_DURATION = 8  # Frames per animation frame
