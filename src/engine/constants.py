# ABOUTME: Core game constants for Pokemon Yellow recreation
# ABOUTME: Defines screen resolution, tile size, FPS, colors, and input mappings

import pygame

# Display settings (expanded viewport at 16x16 tiles, no scaling)
GAME_WIDTH = 480
GAME_HEIGHT = 416
SCALE_FACTOR = 1
WINDOW_WIDTH = GAME_WIDTH * SCALE_FACTOR  # 480
WINDOW_HEIGHT = GAME_HEIGHT * SCALE_FACTOR  # 416

# UI scaling (2x for menus and dialog)
UI_SCALE = 2

# Tile and grid settings
TILE_SIZE = 8                    # Base tile for rendering (8x8 pixels)
METATILE_SIZE = 16               # Movement/collision grid (2x2 base tiles)
TILES_WIDE = GAME_WIDTH // TILE_SIZE    # 60 base tiles
TILES_HIGH = GAME_HEIGHT // TILE_SIZE   # 52 base tiles

# Movement operates on metatile grid
METATILES_WIDE = GAME_WIDTH // METATILE_SIZE   # 30 metatiles
METATILES_HIGH = GAME_HEIGHT // METATILE_SIZE  # 26 metatiles

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
# Player moves one metatile (16 pixels) over 8 frames
MOVEMENT_SPEED = 2  # 16 pixels / 8 frames = 2 pixels per frame

# Directions (for entity facing and movement)
DIR_UP = 0
DIR_DOWN = 1
DIR_LEFT = 2
DIR_RIGHT = 3

# Animation settings
ANIMATION_FRAME_DURATION = 8  # Frames per animation frame
