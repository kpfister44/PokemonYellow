# ABOUTME: Tests for animated SpriteLoop frame selection and rendering
# ABOUTME: Validates frame advancement and sprite sheet slicing

import pygame

from src.overworld.sprite_loop import SpriteLoop


class FakeRenderer:
    def __init__(self):
        self.surface = None
        self.position = None

    def draw_surface(self, surface, position):
        self.surface = surface
        self.position = position


def setup_module(_module):
    pygame.init()
    pygame.display.set_mode((1, 1))


def teardown_module(_module):
    pygame.quit()


def _write_sprite_sheet(path):
    surface = pygame.Surface((64, 16), pygame.SRCALPHA)
    colors = [
        (255, 0, 0, 255),
        (0, 255, 0, 255),
        (0, 0, 255, 255),
        (255, 255, 0, 255)
    ]
    for index, color in enumerate(colors):
        frame_rect = pygame.Rect(index * 16, 0, 16, 16)
        surface.fill(color, frame_rect)
    pygame.image.save(surface, path)
    return colors


def test_sprite_loop_advances_frames(tmp_path):
    sheet_path = tmp_path / "sheet.png"
    colors = _write_sprite_sheet(sheet_path)

    sprite = SpriteLoop(
        (0, 0),
        {
            "src": str(sheet_path),
            "frame_width": 16,
            "frame_height": 16,
            "frame_count": 4,
            "mspf": 100
        }
    )
    renderer = FakeRenderer()

    sprite.render(renderer, 0, 0)
    assert renderer.surface is not None
    assert tuple(renderer.surface.get_at((0, 0))) == colors[0]

    sprite.update(100)
    sprite.render(renderer, 0, 0)
    assert tuple(renderer.surface.get_at((0, 0))) == colors[1]
