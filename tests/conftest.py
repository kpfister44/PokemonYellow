# ABOUTME: Pytest configuration and shared fixtures
# ABOUTME: Initializes pygame for tests that need it

import pygame
import pytest


@pytest.fixture(autouse=True)
def init_pygame():
    """Initialize pygame before each test that needs it."""
    pygame.init()
    pygame.display.set_mode((1, 1), pygame.HIDDEN)
    yield
    pygame.quit()
