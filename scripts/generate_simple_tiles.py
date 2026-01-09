#!/usr/bin/env python3
# ABOUTME: Generate simple tile sprites as a quick win until Phase 9
# ABOUTME: Creates basic patterned tiles that look better than solid colors

import pygame
from pathlib import Path

# Initialize pygame for surface creation
pygame.init()

TILE_SIZE = 16
OUTPUT_DIR = Path(__file__).parent.parent / "assets" / "tiles"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def create_grass_tile():
    """Create a grass tile with a simple pattern."""
    surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
    # Light green base
    surf.fill((139, 172, 15))
    # Add some darker green dots for texture
    dark_green = (107, 142, 35)
    for y in range(0, TILE_SIZE, 4):
        for x in range(0, TILE_SIZE, 4):
            if (x + y) % 8 == 0:
                pygame.draw.rect(surf, dark_green, (x, y, 2, 2))
    return surf

def create_building_tile():
    """Create a building/wall tile."""
    surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
    # Gray base
    surf.fill((100, 100, 100))
    # Add darker grid lines
    dark = (70, 70, 70)
    pygame.draw.rect(surf, dark, (0, 0, TILE_SIZE, 1))  # Top
    pygame.draw.rect(surf, dark, (0, 0, 1, TILE_SIZE))  # Left
    return surf

def create_path_tile():
    """Create a dirt path tile."""
    surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
    # Tan base
    surf.fill((180, 180, 150))
    # Add some darker spots for texture
    darker = (160, 160, 130)
    for y in range(0, TILE_SIZE, 5):
        for x in range(0, TILE_SIZE, 5):
            if (x * y) % 3 == 0:
                pygame.draw.circle(surf, darker, (x, y), 1)
    return surf

def create_water_tile():
    """Create a water tile."""
    surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
    # Blue base
    surf.fill((50, 100, 200))
    # Add lighter blue horizontal lines for waves
    light_blue = (70, 120, 220)
    pygame.draw.line(surf, light_blue, (0, 6), (TILE_SIZE, 6), 1)
    pygame.draw.line(surf, light_blue, (0, 12), (TILE_SIZE, 12), 1)
    return surf

def create_tree_tile():
    """Create a tree tile."""
    surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
    # Dark green base
    surf.fill((34, 139, 34))
    # Add some lighter green spots
    light_green = (50, 160, 50)
    pygame.draw.circle(surf, light_green, (4, 4), 2)
    pygame.draw.circle(surf, light_green, (12, 8), 2)
    pygame.draw.circle(surf, light_green, (8, 12), 2)
    return surf

def create_sign_tile():
    """Create a sign post tile."""
    surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
    # Brown base
    surf.fill((139, 69, 19))
    # Add lighter wood grain
    lighter = (180, 100, 40)
    pygame.draw.line(surf, lighter, (4, 0), (4, TILE_SIZE), 1)
    pygame.draw.line(surf, lighter, (12, 0), (12, TILE_SIZE), 1)
    return surf

def main():
    """Generate all tile sprites."""
    print("Generating simple tile sprites...")

    tiles = {
        "grass": create_grass_tile(),
        "building": create_building_tile(),
        "path": create_path_tile(),
        "water": create_water_tile(),
        "tree": create_tree_tile(),
        "sign": create_sign_tile(),
    }

    for name, surf in tiles.items():
        filepath = OUTPUT_DIR / f"{name}.png"
        pygame.image.save(surf, str(filepath))
        print(f"  ✅ Created {filepath}")

    print(f"\n✅ Generated {len(tiles)} tile sprites in {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
