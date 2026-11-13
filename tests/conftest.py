"""Pytest fixtures and environment setup for Red Hat Clicker test suite."""

import os
import pygame
import pytest


@pytest.fixture(autouse=True)
def pygame_headless_setup():
    """Ensure headless Pygame drivers and clean subsystem teardown for all tests."""
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    if not pygame.get_init():
        pygame.init()
    if not pygame.font.get_init():
        pygame.font.init()
    yield
    pygame.quit()
