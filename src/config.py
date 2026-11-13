"""Configuration constants and display settings for Red Hat Clicker."""

# Window & display settings
WINDOW_WIDTH: int = 1280
WINDOW_HEIGHT: int = 720
WINDOW_TITLE: str = "Red Hat Clicker"
TARGET_FPS: int = 60

# Layout dimensions
LEFT_PANEL_WIDTH: int = 440
CENTER_PANEL_WIDTH: int = 420
RIGHT_PANEL_WIDTH: int = 420

# UI Colors (RGB)
# Authentic Red Hat Red palette and dark modern theme
COLOR_RED: tuple[int, int, int] = (238, 0, 0)          # Red Hat standard #EE0000
COLOR_DARK_RED: tuple[int, int, int] = (186, 0, 0)     # Shadow / pressed state
COLOR_RED_HOVER: tuple[int, int, int] = (255, 48, 48)  # Hover highlight
COLOR_RED_RIBBON: tuple[int, int, int] = (20, 20, 20)  # Hat ribbon band

COLOR_BG: tuple[int, int, int] = (24, 24, 27)          # Main window background
COLOR_PANEL_BG: tuple[int, int, int] = (32, 32, 38)    # Panel background
COLOR_PANEL_BORDER: tuple[int, int, int] = (45, 45, 52)# Panel divider border

COLOR_TEXT_PRIMARY: tuple[int, int, int] = (250, 250, 250)
COLOR_TEXT_SECONDARY: tuple[int, int, int] = (160, 160, 168)
COLOR_TEXT_MUTED: tuple[int, int, int] = (115, 115, 125)
COLOR_TEXT_GOLD: tuple[int, int, int] = (255, 204, 0)

COLOR_WHITE: tuple[int, int, int] = (255, 255, 255)
COLOR_BLACK: tuple[int, int, int] = (0, 0, 0)
COLOR_ACCENT: tuple[int, int, int] = (0, 102, 204)

# Central Hat Button placement
HAT_BUTTON_CENTER_X: int = LEFT_PANEL_WIDTH // 2
HAT_BUTTON_CENTER_Y: int = 410
HAT_BUTTON_RADIUS: int = 110

# Economy defaults
BASE_CLICK_VALUE: float = 1.0
PRICE_GROWTH_RATE: float = 1.15
SAVE_FILE_NAME: str = "savegame.json"
