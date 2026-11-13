"""Unit tests for Game engine loop, event dispatch, and display configurations."""

import pygame
from src.config import HAT_LOGO_PATH, TARGET_FPS, WINDOW_HEIGHT, WINDOW_TITLE, WINDOW_WIDTH
from src.engine.game import Game


def test_engine_initialization_and_exit():
    """Verify Pygame loop configuration and graceful quit handling as proposed in Phase 2."""
    game = Game()
    assert game.target_fps == 60
    assert game.is_running is True

    game.handle_event(pygame.event.Event(pygame.QUIT))
    assert game.is_running is False


def test_game_escape_key_exit():
    """Verify pressing ESC terminates the game loop."""
    game = Game()
    assert game.is_running is True

    key_event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_ESCAPE, "mod": 0})
    game.handle_event(key_event)
    assert game.is_running is False


def test_game_spacebar_click():
    """Verify pressing Spacebar triggers a manual click on the hat and resets pressed state."""
    game = Game()
    assert game.state.total_hats == 0

    key_event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_SPACE, "mod": 0})
    game.handle_event(key_event)
    assert game.state.total_hats == 1
    assert game.state.total_clicks == 1
    assert game.button.is_pressed is True

    # After simulation tick past animation duration, pressed state resets to False
    game.update(0.15)
    assert game.button.is_pressed is False


def test_game_spacebar_keyup():
    """Verify releasing Spacebar clears button pressed state."""
    game = Game()
    key_down = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_SPACE, "mod": 0})
    game.handle_event(key_down)
    assert game.button.is_pressed is True

    key_up = pygame.event.Event(pygame.KEYUP, {"key": pygame.K_SPACE, "mod": 0})
    game.handle_event(key_up)
    assert game.button.is_pressed is False


def test_game_update_and_render():
    """Verify game engine simulation tick and render cycle execute cleanly."""
    game = Game()
    game.state.hps = 10.0
    game.update(0.1)  # 0.1 seconds * 10 HPS = 1.0 hat
    assert abs(game.state.total_hats - 1.0) < 1e-4

    # Render on internal screen surface
    surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    game.render(surface)


def test_config_values():
    """Verify standard display and configuration constants."""
    assert TARGET_FPS == 60
    assert WINDOW_WIDTH == 1280
    assert WINDOW_HEIGHT == 720
    assert WINDOW_TITLE == "Red Hat Clicker"
    assert HAT_LOGO_PATH.exists()
    assert HAT_LOGO_PATH.is_file()


def test_game_store_purchase_and_passive_accumulation():
    """Verify purchasing a generator via game state drives passive generation in the loop."""
    game = Game()
    assert game.state.hps == 0.0

    # Give player hats and buy 1 RHEL
    game.state.add_hats(50.0)
    card_rect = game.store.get_card_rect(0)
    click_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": card_rect.center, "button": 1})
    game.handle_event(click_event)

    assert game.state.get_generator_count("rhel") == 1
    assert abs(game.state.hps - 0.1) < 1e-4

    # Tick 10 seconds: 10 * 0.1 HPS = 1.0 RH
    initial_hats = game.state.total_hats
    game.update(10.0)
    assert abs((game.state.total_hats - initial_hats) - 1.0) < 1e-4
