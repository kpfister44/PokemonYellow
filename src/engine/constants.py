# ABOUTME: Core game constants for Pokemon Yellow recreation
# ABOUTME: Defines screen resolution, tile size, FPS, colors, and input mappings

import pygame

# Display settings (Game Boy viewport at 20x18 tiles, no scaling)
GAME_WIDTH = 160
GAME_HEIGHT = 144
SCALE_FACTOR = 1
WINDOW_WIDTH = GAME_WIDTH * SCALE_FACTOR  # 160
WINDOW_HEIGHT = GAME_HEIGHT * SCALE_FACTOR  # 144

# UI scaling (1x for menus and dialog)
UI_SCALE = 1

# Tile and grid settings
TILE_SIZE = 8                    # Base tile for rendering (8x8 pixels)
METATILE_SIZE = 16               # Movement/collision grid (2x2 base tiles)
TILES_WIDE = GAME_WIDTH // TILE_SIZE    # 20 base tiles
TILES_HIGH = GAME_HEIGHT // TILE_SIZE   # 18 base tiles

# Movement operates on metatile grid
METATILES_WIDE = GAME_WIDTH // METATILE_SIZE   # 10 metatiles
METATILES_HIGH = GAME_HEIGHT // METATILE_SIZE  # 9 metatiles

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
