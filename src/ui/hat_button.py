"""Interactive central Red Hat button component."""

import math
from pathlib import Path
from typing import Optional, Union
import pygame

from src.config import (
    COLOR_BLACK,
    COLOR_DARK_RED,
    COLOR_PANEL_BG,
    COLOR_RED,
    COLOR_RED_HOVER,
    COLOR_RED_RIBBON,
    COLOR_WHITE,
    HAT_BUTTON_CENTER_X,
    HAT_BUTTON_CENTER_Y,
    HAT_BUTTON_RADIUS,
    HAT_LOGO_PATH,
)
from src.engine.state import GameState


class FloatingText:
    """Animated text popup displayed when clicking the hat."""

    def __init__(self, text: str, x: int, y: int, color: tuple[int, int, int] = COLOR_WHITE):
        self.text = text
        self.x = float(x)
        self.y = float(y)
        self.color = color
        self.lifetime = 0.8  # seconds
        self.elapsed = 0.0
        self.vy = -70.0  # pixels per second floating up

    def update(self, dt: float) -> bool:
        """Update popup position and lifetime. Returns False when expired."""
        self.elapsed += dt
        self.y += self.vy * dt
        return self.elapsed < self.lifetime

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """Render floating text with fade-out alpha."""
        if self.elapsed >= self.lifetime:
            return
        alpha = int(255 * (1.0 - (self.elapsed / self.lifetime)))
        text_surf = font.render(self.text, True, self.color)
        alpha_surf = pygame.Surface(text_surf.get_size(), pygame.SRCALPHA)
        alpha_surf.blit(text_surf, (0, 0))
        alpha_surf.set_alpha(alpha)
        surface.blit(alpha_surf, (int(self.x - text_surf.get_width() / 2), int(self.y)))


class HatButton:
    """Primary clickable Red Hat element with scaling animations and visual feedback."""

    def __init__(
        self,
        x: int = HAT_BUTTON_CENTER_X,
        y: int = HAT_BUTTON_CENTER_Y,
        radius: int = HAT_BUTTON_RADIUS,
        image_path: Optional[Union[str, Path]] = HAT_LOGO_PATH,
    ):
        self.x = x
        self.y = y
        self.radius = radius
        self.is_hovered: bool = False
        self.is_pressed: bool = False
        self.scale: float = 1.0
        self.click_animation_timer: float = 0.0
        self.popups: list[FloatingText] = []
        self.image_path: Optional[Path] = None
        self.image: Optional[pygame.Surface] = None
        self._cached_scaled_image: Optional[pygame.Surface] = None
        self._cached_size: Optional[tuple[int, int]] = None
        self.load_image(image_path)

    def load_image(self, path: Optional[Union[str, Path]]) -> None:
        """Load hat logo surface from image path, with graceful fallback if absent."""
        self.image_path = Path(path) if path is not None else None
        self._cached_scaled_image = None
        self._cached_size = None

        if self.image_path is None:
            self.image = None
            return

        if not self.image_path.is_file():
            self.image = None
            return

        try:
            surf = pygame.image.load(str(self.image_path))
            if pygame.display.get_init() and pygame.display.get_surface() is not None:
                try:
                    surf = surf.convert_alpha()
                except pygame.error:
                    pass
            self.image = surf
        except (pygame.error, OSError):
            self.image = None

    def is_point_inside(self, pos: tuple[int, int]) -> bool:
        """Determine if a screen coordinate falls within the circular button boundary."""
        dx = pos[0] - self.x
        dy = pos[1] - self.y
        return (dx * dx + dy * dy) <= (self.radius * self.radius)

    def handle_click(self, state: GameState) -> float:
        """Trigger click processing: updates game state and starts tactile click animation."""
        earned = state.click()

        # Immediate scale reduction for responsive tactile feel
        self.is_pressed = True
        self.scale = 0.90
        self.click_animation_timer = 0.12

        # Spawn floating click feedback
        popup_text = f"+{int(earned) if earned.is_integer() else f'{earned:.1f}'}"
        # Stagger slightly so rapid clicks don't perfectly overlap
        offset_x = (hash(state.total_clicks) % 30) - 15
        self.popups.append(FloatingText(popup_text, self.x + offset_x, self.y - 40))

        return earned

    def handle_event(self, event: pygame.event.Event, state: GameState) -> bool:
        """Process mouse interactions (hover, click, release)."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_point_inside(event.pos):
                self.handle_click(state)
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.is_pressed = False
        elif event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.is_point_inside(event.pos)
        return False

    def update(self, dt: float) -> None:
        """Update animation timers, scale interpolation, and floating popups."""
        if self.click_animation_timer > 0:
            self.click_animation_timer = max(0.0, self.click_animation_timer - dt)
            # Rebound back to normal scale
            t = 1.0 - (self.click_animation_timer / 0.12)
            self.scale = 0.90 + (0.10 * t)
            if self.click_animation_timer == 0.0:
                self.is_pressed = False
        else:
            # Subtle hover zoom
            target_scale = 1.04 if self.is_hovered else 1.0
            self.scale += (target_scale - self.scale) * min(1.0, dt * 15.0)

        # Update floating popups
        self.popups = [p for p in self.popups if p.update(dt)]

    def draw(
        self,
        surface: pygame.Surface,
        popup_font: Optional[pygame.font.Font] = None,
    ) -> None:
        """Render the Red Hat graphic procedurally with interactive lighting and animations."""
        r = int(self.radius * self.scale)
        cx, cy = self.x, self.y

        # Choose color tone based on interaction state
        if self.is_pressed:
            hat_color = COLOR_DARK_RED
        elif self.is_hovered:
            hat_color = COLOR_RED_HOVER
        else:
            hat_color = COLOR_RED

        # 1. Outer ambient glow ring on hover
        if self.is_hovered:
            glow_surf = pygame.Surface((r * 2 + 60, r * 2 + 60), pygame.SRCALPHA)
            pygame.draw.circle(
                glow_surf,
                (*COLOR_RED, 40),
                (r + 30, r + 30),
                r + 18,
            )
            surface.blit(glow_surf, (cx - (r + 30), cy - (r + 30)))

        # 2. Base pedestal shadow
        shadow_rect = pygame.Rect(cx - int(r * 0.95), cy + int(r * 0.45), int(r * 1.9), int(r * 0.45))
        shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (10, 10, 14, 130), shadow_surf.get_rect())
        surface.blit(shadow_surf, shadow_rect.topleft)

        # 3. Hat Graphic (Official logo image or procedural fallback)
        if self.image is not None:
            base_w = int(self.radius * 2.2)
            base_h = int(base_w * self.image.get_height() / self.image.get_width())
            w = max(1, int(base_w * self.scale))
            h = max(1, int(base_h * self.scale))

            if self._cached_scaled_image is None or self._cached_size != (w, h):
                self._cached_scaled_image = pygame.transform.smoothscale(self.image, (w, h))
                self._cached_size = (w, h)

            img_to_blit = self._cached_scaled_image
            if self.is_pressed:
                pressed_surf = img_to_blit.copy()
                pressed_surf.fill((210, 210, 210, 255), special_flags=pygame.BLEND_RGBA_MULT)
                img_to_blit = pressed_surf

            img_rect = img_to_blit.get_rect(center=(cx, cy))
            surface.blit(img_to_blit, img_rect.topleft)
        else:
            # 3a. Procedural Fedora Brim (curved wide base)
            brim_rect = pygame.Rect(cx - r, cy + int(r * 0.1), r * 2, int(r * 0.65))
            pygame.draw.ellipse(surface, hat_color, brim_rect)
            pygame.draw.ellipse(surface, COLOR_DARK_RED, brim_rect, width=3)

            # 3b. Procedural Fedora Crown (tapered top)
            crown_width = int(r * 1.15)
            crown_height = int(r * 1.05)
            crown_top_y = cy - int(r * 0.75)
            crown_rect = pygame.Rect(cx - crown_width // 2, crown_top_y, crown_width, crown_height)
            pygame.draw.ellipse(surface, hat_color, crown_rect)

            # Fedora crease highlight (crease along the crown top)
            crease_rect = pygame.Rect(cx - int(crown_width * 0.35), crown_top_y + 4, int(crown_width * 0.7), int(r * 0.25))
            crease_surf = pygame.Surface((crease_rect.width, crease_rect.height), pygame.SRCALPHA)
            pygame.draw.ellipse(crease_surf, (*COLOR_DARK_RED, 180), crease_surf.get_rect())
            surface.blit(crease_surf, crease_rect.topleft)

            # 3c. Black Ribbon Band
            band_height = int(r * 0.22)
            band_y = cy + int(r * 0.12)
            band_rect = pygame.Rect(cx - int(r * 0.58), band_y, int(r * 1.16), band_height)
            band_surf = pygame.Surface((band_rect.width, band_rect.height), pygame.SRCALPHA)
            pygame.draw.ellipse(band_surf, (*COLOR_RED_RIBBON, 240), band_surf.get_rect())
            surface.blit(band_surf, band_rect.topleft)

        # 6. Render floating text popups
        if popup_font:
            for popup in self.popups:
                popup.draw(surface, popup_font)
