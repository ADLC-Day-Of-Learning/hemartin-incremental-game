"""Product Store UI Panel for Red Hat Offerings."""

from typing import Optional, Union
import pygame

from src.config import (
    COLOR_BG,
    COLOR_DARK_RED,
    COLOR_PANEL_BG,
    COLOR_PANEL_BORDER,
    COLOR_RED,
    COLOR_RED_HOVER,
    COLOR_TEXT_GOLD,
    COLOR_TEXT_MUTED,
    COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY,
    COLOR_WHITE,
    RIGHT_PANEL_WIDTH,
    WINDOW_HEIGHT,
)
from src.engine.economy import (
    calculate_bulk_cost,
    calculate_generator_cost,
    calculate_max_affordable,
)
from src.engine.state import GameState
from src.models.generator import Generator, get_default_generators


class StorePanel:
    """Right-hand UI panel rendering product offerings, quantities, and purchase buttons."""

    QUANTITY_OPTIONS: list[Union[int, str]] = [1, 10, 100, "Max"]

    def __init__(
        self,
        x: int = 860,
        y: int = 0,
        width: int = RIGHT_PANEL_WIDTH,
        height: int = WINDOW_HEIGHT,
    ):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.selected_quantity: Union[int, str] = 1
        self.scroll_y: float = 0.0
        self.hovered_card_id: Optional[str] = None
        self.hovered_toggle: Optional[Union[int, str]] = None

        # Dimensions
        self.header_y = 24
        self.toggle_y = 82
        self.toggle_btn_width = 80
        self.toggle_btn_height = 28
        self.toggle_spacing = 8

        self.list_top = 124
        self.list_bottom = self.height - 12
        self.card_height = 64
        self.card_spacing = 6
        self.card_width = self.width - 32

    def get_quantity_toggle_rect(self, index: int) -> pygame.Rect:
        """Calculate screen rectangle for a quantity toggle button."""
        start_x = self.x + 24
        bx = start_x + index * (self.toggle_btn_width + self.toggle_spacing)
        return pygame.Rect(bx, self.toggle_y, self.toggle_btn_width, self.toggle_btn_height)

    def get_card_rect(self, index: int) -> pygame.Rect:
        """Calculate screen rectangle for a generator card."""
        cx = self.x + 16
        cy = self.list_top + index * (self.card_height + self.card_spacing) - int(self.scroll_y)
        return pygame.Rect(cx, cy, self.card_width, self.card_height)

    def handle_event(
        self,
        event: pygame.event.Event,
        state: GameState,
        catalog: dict[str, Generator],
    ) -> bool:
        """Process mouse interactions: quantity toggling, scrolling, and product purchases."""
        # Handle mouse scroll
        if event.type == pygame.MOUSEWHEEL:
            mouse_x = getattr(event, "mouse_x", None)
            if mouse_x is None:
                mouse_pos = getattr(event, "pos", None)
                if mouse_pos is not None:
                    mouse_x = mouse_pos[0]
                elif pygame.display.get_init():
                    try:
                        mouse_x = pygame.mouse.get_pos()[0]
                    except pygame.error:
                        mouse_x = self.x + 10
                else:
                    mouse_x = self.x + 10

            if mouse_x >= self.x:
                total_content_height = len(catalog) * (self.card_height + self.card_spacing)
                visible_height = self.list_bottom - self.list_top
                max_scroll = max(0.0, float(total_content_height - visible_height))
                self.scroll_y = max(0.0, min(self.scroll_y - event.y * 30, max_scroll))
                return True

        # Handle mouse motion for hover highlights
        if event.type == pygame.MOUSEMOTION:
            pos = event.pos
            self.hovered_toggle = None
            self.hovered_card_id = None

            # Check toggle hover
            for idx, opt in enumerate(self.QUANTITY_OPTIONS):
                if self.get_quantity_toggle_rect(idx).collidepoint(pos):
                    self.hovered_toggle = opt
                    break

            # Check card hover (only within list viewport)
            viewport_rect = pygame.Rect(self.x, self.list_top, self.width, self.list_bottom - self.list_top)
            if viewport_rect.collidepoint(pos):
                for idx, gen in enumerate(catalog.values()):
                    card_rect = self.get_card_rect(idx)
                    if card_rect.collidepoint(pos):
                        self.hovered_card_id = gen.id
                        break
            return False

        # Handle clicks
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            # 1. Check quantity toggles
            for idx, opt in enumerate(self.QUANTITY_OPTIONS):
                if self.get_quantity_toggle_rect(idx).collidepoint(pos):
                    self.selected_quantity = opt
                    return True

            # 2. Check generator purchase clicks
            viewport_rect = pygame.Rect(self.x, self.list_top, self.width, self.list_bottom - self.list_top)
            if viewport_rect.collidepoint(pos):
                for idx, gen in enumerate(catalog.values()):
                    card_rect = self.get_card_rect(idx)
                    if card_rect.collidepoint(pos):
                        if not gen.is_unlocked(state.lifetime_hats):
                            return False

                        if self.selected_quantity == "Max":
                            return state.buy_generator(gen.id, quantity="max", catalog=catalog)
                        else:
                            qty = int(self.selected_quantity)
                            return state.buy_generator(gen.id, quantity=qty, catalog=catalog)

        return False

    def update(self, dt: float) -> None:
        """Update animations or panel state per simulation frame."""
        pass

    def draw(
        self,
        surface: pygame.Surface,
        state: GameState,
        catalog: dict[str, Generator],
        font_header: pygame.font.Font,
        font_subtitle: pygame.font.Font,
        font_small: pygame.font.Font,
    ) -> None:
        """Render product store UI panel, toggles, cards, and affordability states."""
        # 1. Panel Background
        panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, COLOR_PANEL_BG, panel_rect)
        pygame.draw.line(surface, COLOR_PANEL_BORDER, (self.x, 0), (self.x, self.height), 2)

        # 2. Header and Subtitle
        header_surf = font_header.render("Offerings Catalog", True, COLOR_TEXT_PRIMARY)
        surface.blit(header_surf, (self.x + 24, self.header_y))

        sub_text = "Automate Red Hat production"
        sub_surf = font_small.render(sub_text, True, COLOR_TEXT_MUTED)
        surface.blit(sub_surf, (self.x + 24, self.header_y + 34))

        # 3. Quantity Toggles
        for idx, opt in enumerate(self.QUANTITY_OPTIONS):
            btn_rect = self.get_quantity_toggle_rect(idx)
            is_active = self.selected_quantity == opt
            is_hovered = self.hovered_toggle == opt

            if is_active:
                btn_bg = COLOR_RED
                btn_border = COLOR_DARK_RED
                text_color = COLOR_WHITE
            elif is_hovered:
                btn_bg = (48, 48, 56)
                btn_border = COLOR_TEXT_MUTED
                text_color = COLOR_TEXT_PRIMARY
            else:
                btn_bg = COLOR_BG
                btn_border = COLOR_PANEL_BORDER
                text_color = COLOR_TEXT_SECONDARY

            pygame.draw.rect(surface, btn_bg, btn_rect, border_radius=4)
            pygame.draw.rect(surface, btn_border, btn_rect, width=1, border_radius=4)

            label = f"{opt}x" if isinstance(opt, int) else str(opt)
            lbl_surf = font_small.render(label, True, text_color)
            surface.blit(
                lbl_surf,
                (
                    btn_rect.centerx - lbl_surf.get_width() // 2,
                    btn_rect.centery - lbl_surf.get_height() // 2,
                ),
            )

        # 4. Scrollable List Viewport
        viewport_rect = pygame.Rect(self.x, self.list_top, self.width, self.list_bottom - self.list_top)
        surface.set_clip(viewport_rect)

        try:
            for idx, gen in enumerate(catalog.values()):
                card_rect = self.get_card_rect(idx)
                # Skip rendering if fully outside viewport
                if card_rect.bottom < self.list_top or card_rect.top > self.list_bottom:
                    continue

                is_unlocked = gen.is_unlocked(state.lifetime_hats)
                owned_count = state.get_generator_count(gen.id)
                is_hovered = self.hovered_card_id == gen.id

                if not is_unlocked:
                    # Locked card presentation
                    pygame.draw.rect(surface, (22, 22, 26), card_rect, border_radius=5)
                    pygame.draw.rect(surface, (36, 36, 42), card_rect, width=1, border_radius=5)

                    name_surf = font_subtitle.render(f"??? ({gen.name.split(' (')[0]})", True, COLOR_TEXT_MUTED)
                    req_text = f"Unlocks at {int(gen.unlock_requirement):,} lifetime RH"
                    req_surf = font_small.render(req_text, True, (90, 90, 100))

                    surface.blit(name_surf, (card_rect.x + 14, card_rect.y + 12))
                    surface.blit(req_surf, (card_rect.x + 14, card_rect.y + 36))
                    continue

                # Calculate price and purchase count for current quantity toggle
                if self.selected_quantity == "Max":
                    max_res = calculate_max_affordable(gen.base_cost, owned_count, state.total_hats)
                    units_to_buy = int(max_res)
                    if units_to_buy > 0:
                        cost = max_res.cost
                        can_afford = True
                    else:
                        units_to_buy = 1
                        cost = calculate_generator_cost(gen.base_cost, owned_count)
                        can_afford = False
                else:
                    units_to_buy = int(self.selected_quantity)
                    cost = calculate_bulk_cost(gen.base_cost, owned_count, units_to_buy)
                    can_afford = state.total_hats >= cost

                # Determine card styling
                if can_afford:
                    if is_hovered:
                        card_bg = (46, 46, 58)
                        border_color = COLOR_RED
                    else:
                        card_bg = (36, 36, 46)
                        border_color = (60, 60, 75)
                    cost_color = COLOR_TEXT_GOLD
                    name_color = COLOR_TEXT_PRIMARY
                else:
                    if is_hovered:
                        card_bg = (30, 30, 38)
                        border_color = (48, 48, 60)
                    else:
                        card_bg = (24, 24, 30)
                        border_color = COLOR_PANEL_BORDER
                    cost_color = COLOR_TEXT_MUTED
                    name_color = COLOR_TEXT_SECONDARY

                pygame.draw.rect(surface, card_bg, card_rect, border_radius=5)
                pygame.draw.rect(surface, border_color, card_rect, width=1, border_radius=5)

                # Card Texts
                # 1. Product Name (left)
                display_name = gen.name
                if len(display_name) > 28:
                    display_name = display_name[:26] + "..."
                name_surf = font_subtitle.render(display_name, True, name_color)
                surface.blit(name_surf, (card_rect.x + 12, card_rect.y + 10))

                # 2. Owned count badge (right)
                count_text = f"x{owned_count}"
                count_surf = font_subtitle.render(count_text, True, COLOR_RED if owned_count > 0 else COLOR_TEXT_MUTED)
                surface.blit(
                    count_surf,
                    (card_rect.right - count_surf.get_width() - 14, card_rect.y + 10),
                )

                # 3. Cost & Quantity (bottom left)
                if self.selected_quantity == "Max":
                    if can_afford:
                        cost_str = f"Buy {units_to_buy} for {cost:,} RH"
                    else:
                        cost_str = f"Max (0) | Next: {cost:,} RH"
                else:
                    cost_str = f"Cost: {cost:,} RH"
                cost_surf = font_small.render(cost_str, True, cost_color)
                surface.blit(cost_surf, (card_rect.x + 12, card_rect.y + 36))

                # 4. HPS Generation (bottom right)
                hps_gain = gen.base_hps * units_to_buy * gen.multiplier
                hps_str = f"+{hps_gain:.1f} HPS"
                hps_surf = font_small.render(hps_str, True, COLOR_TEXT_SECONDARY)
                surface.blit(
                    hps_surf,
                    (card_rect.right - hps_surf.get_width() - 14, card_rect.y + 36),
                )
        finally:
            surface.set_clip(None)

        # 5. Scrollbar indicator if content overflows
        total_content_height = len(catalog) * (self.card_height + self.card_spacing)
        visible_height = self.list_bottom - self.list_top
        if total_content_height > visible_height:
            bar_height = max(24, int(visible_height * (visible_height / total_content_height)))
            max_scroll = total_content_height - visible_height
            scroll_pct = self.scroll_y / max_scroll if max_scroll > 0 else 0.0
            bar_y = self.list_top + int(scroll_pct * (visible_height - bar_height))
            bar_rect = pygame.Rect(self.x + self.width - 6, bar_y, 4, bar_height)
            pygame.draw.rect(surface, (70, 70, 85), bar_rect, border_radius=2)
