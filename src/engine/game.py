"""Core Game Engine managing loop lifecycle, event dispatch, and rendering."""

import os
from typing import Optional
import pygame

from src.config import (
    CENTER_PANEL_WIDTH,
    COLOR_ACCENT,
    COLOR_BG,
    COLOR_PANEL_BG,
    COLOR_PANEL_BORDER,
    COLOR_RED,
    COLOR_TEXT_GOLD,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    HAT_BUTTON_CENTER_X,
    HAT_BUTTON_CENTER_Y,
    HAT_BUTTON_RADIUS,
    LEFT_PANEL_WIDTH,
    RIGHT_PANEL_WIDTH,
    TARGET_FPS,
    WINDOW_HEIGHT,
    WINDOW_TITLE,
    WINDOW_WIDTH,
)
from src.engine.state import GameState
from src.models.generator import Generator, get_default_generators
from src.ui.hat_button import HatButton
from src.ui.store import StorePanel


class Game:
    """Primary game engine orchestrating Pygame subsystems, state, and rendering."""

    def __init__(
        self,
        headless: bool = False,
        width: int = WINDOW_WIDTH,
        height: int = WINDOW_HEIGHT,
        fps: int = TARGET_FPS,
    ):
        self.width = width
        self.height = height
        self.target_fps = fps
        self.headless = headless
        self.is_running = True

        self.state = GameState()
        self.catalog: dict[str, Generator] = get_default_generators()
        self.state.recalculate_hps(self.catalog)

        self.button = HatButton(
            x=HAT_BUTTON_CENTER_X,
            y=HAT_BUTTON_CENTER_Y,
            radius=HAT_BUTTON_RADIUS,
        )

        right_divider_x = LEFT_PANEL_WIDTH + CENTER_PANEL_WIDTH
        self.store = StorePanel(
            x=right_divider_x,
            y=0,
            width=RIGHT_PANEL_WIDTH,
            height=self.height,
        )

        # Initialize Pygame and audio/video subsystems gracefully
        if not pygame.get_init():
            if "DISPLAY" not in os.environ and "SDL_VIDEODRIVER" not in os.environ:
                os.environ["SDL_VIDEODRIVER"] = "dummy"
            if "SDL_AUDIODRIVER" not in os.environ:
                os.environ["SDL_AUDIODRIVER"] = "dummy"
            pygame.init()

        if not pygame.font.get_init():
            pygame.font.init()

        self.clock = pygame.time.Clock()

        # Set up display surface
        self.screen: Optional[pygame.Surface] = None
        if not self.headless:
            try:
                self.screen = pygame.display.set_mode((self.width, self.height))
                pygame.display.set_caption(WINDOW_TITLE)
            except pygame.error:
                self.headless = True
                self.screen = pygame.Surface((self.width, self.height))
        else:
            self.screen = pygame.Surface((self.width, self.height))

        # Fonts
        self.font_header = pygame.font.Font(None, 36)
        self.font_counter = pygame.font.Font(None, 46)
        self.font_subtitle = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 20)

    def handle_event(self, event: pygame.event.Event) -> None:
        """Process incoming Pygame events (window exit, mouse clicks, keyboard shortcuts)."""
        if event.type == pygame.QUIT:
            self.is_running = False
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.is_running = False
                return
            if event.key == pygame.K_SPACE:
                self.button.handle_click(self.state)
                return

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                self.button.is_pressed = False
                return

        self.button.handle_event(event, self.state)
        self.store.handle_event(event, self.state, self.catalog)

    def update(self, dt: float) -> None:
        """Update simulation state, animations, and economy generation per frame."""
        self.button.update(dt)
        self.store.update(dt)

        # Passive production accumulation
        if self.state.hps > 0:
            self.state.add_hats(self.state.hps * dt)

    def render(self, surface: Optional[pygame.Surface] = None) -> None:
        """Draw active scene, UI panels, central hat button, and counters."""
        target = surface or self.screen
        if target is None:
            return

        # 1. Fill background
        target.fill(COLOR_BG)

        # 2. Render Panel Outlines
        # Left Panel (Big Hat + Primary Counter)
        left_rect = pygame.Rect(0, 0, LEFT_PANEL_WIDTH, self.height)
        pygame.draw.rect(target, COLOR_PANEL_BG, left_rect)
        pygame.draw.line(target, COLOR_PANEL_BORDER, (LEFT_PANEL_WIDTH, 0), (LEFT_PANEL_WIDTH, self.height), 2)

        # Center Panel (News & Stats Wireframe)
        center_x = LEFT_PANEL_WIDTH
        center_rect = pygame.Rect(center_x, 0, CENTER_PANEL_WIDTH, self.height)
        pygame.draw.rect(target, COLOR_BG, center_rect)
        right_divider_x = center_x + CENTER_PANEL_WIDTH
        pygame.draw.line(target, COLOR_PANEL_BORDER, (right_divider_x, 0), (right_divider_x, self.height), 2)

        # Right Panel (Store Wireframe)
        right_rect = pygame.Rect(right_divider_x, 0, RIGHT_PANEL_WIDTH, self.height)
        pygame.draw.rect(target, COLOR_PANEL_BG, right_rect)

        # --- LEFT PANEL CONTENTS ---
        # Game Title Header
        title_surf = self.font_header.render(WINDOW_TITLE, True, COLOR_TEXT_PRIMARY)
        target.blit(title_surf, (LEFT_PANEL_WIDTH // 2 - title_surf.get_width() // 2, 28))

        # Currency Counter
        hats_int = int(self.state.total_hats)
        hat_text = f"{hats_int:,} Red Hat" if hats_int == 1 else f"{hats_int:,} Red Hats"
        counter_surf = self.font_counter.render(hat_text, True, COLOR_RED)
        target.blit(counter_surf, (LEFT_PANEL_WIDTH // 2 - counter_surf.get_width() // 2, 85))

        # HPS Rate
        hps_text = f"{self.state.hps:.1f} per second"
        hps_surf = self.font_subtitle.render(hps_text, True, COLOR_TEXT_SECONDARY)
        target.blit(hps_surf, (LEFT_PANEL_WIDTH // 2 - hps_surf.get_width() // 2, 138))

        # Central Hat Button
        self.button.draw(target, self.font_subtitle)

        # Interaction hint
        hint_surf = self.font_small.render("Click the Red Hat or press [Spacebar]", True, COLOR_TEXT_MUTED)
        target.blit(hint_surf, (LEFT_PANEL_WIDTH // 2 - hint_surf.get_width() // 2, 575))

        quit_hint = self.font_small.render("[ESC] to Exit", True, COLOR_TEXT_MUTED)
        target.blit(quit_hint, (LEFT_PANEL_WIDTH // 2 - quit_hint.get_width() // 2, 605))

        # --- CENTER PANEL CONTENTS (Architecture Wireframe) ---
        stats_header = self.font_header.render("Enterprise Stats", True, COLOR_TEXT_PRIMARY)
        target.blit(stats_header, (center_x + 24, 28))

        clicks_surf = self.font_subtitle.render(f"Total Clicks: {self.state.total_clicks:,}", True, COLOR_TEXT_SECONDARY)
        target.blit(clicks_surf, (center_x + 24, 90))

        life_surf = self.font_subtitle.render(
            f"Lifetime Production: {int(self.state.lifetime_hats):,} RH", True, COLOR_TEXT_SECONDARY
        )
        target.blit(life_surf, (center_x + 24, 125))

        news_box = pygame.Rect(center_x + 20, 190, CENTER_PANEL_WIDTH - 40, 480)
        pygame.draw.rect(target, COLOR_PANEL_BG, news_box, border_radius=6)
        pygame.draw.rect(target, COLOR_PANEL_BORDER, news_box, width=1, border_radius=6)

        news_title = self.font_subtitle.render("Enterprise News & Ticker", True, COLOR_TEXT_GOLD)
        target.blit(news_title, (center_x + 36, 210))

        news_placeholder = self.font_small.render("System operational. Hat demand surging across clouds.", True, COLOR_TEXT_MUTED)
        target.blit(news_placeholder, (center_x + 36, 245))

        # --- RIGHT PANEL CONTENTS (Store) ---
        self.store.draw(
            target,
            self.state,
            self.catalog,
            self.font_header,
            self.font_subtitle,
            self.font_small,
        )

    def run(self) -> None:
        """Execute the primary 60 FPS application game loop."""
        while self.is_running:
            dt = self.clock.tick(self.target_fps) / 1000.0
            for event in pygame.event.get():
                self.handle_event(event)

            self.update(dt)

            if not self.headless and self.screen:
                self.render()
                pygame.display.flip()

        pygame.quit()
