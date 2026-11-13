"""Game state data model and lifecycle for Red Hat Clicker."""

from dataclasses import dataclass, field
import time
from typing import Any

from src.config import BASE_CLICK_VALUE


@dataclass
class GameState:
    """Tracks active game progress, currency, generator counts, and statistics."""

    total_hats: float = 0.0
    lifetime_hats: float = 0.0
    total_clicks: int = 0
    hps: float = 0.0
    click_power: float = BASE_CLICK_VALUE
    generators: dict[str, int] = field(default_factory=dict)
    upgrades_unlocked: list[str] = field(default_factory=list)
    last_saved_timestamp: float = field(default_factory=time.time)

    def click(self) -> float:
        """Process a manual click on the Red Hat.

        Increments click statistics, updates accumulated currency, and returns
        the amount of Red Hats earned from this click.
        """
        earned = self.click_power
        self.total_hats += earned
        self.lifetime_hats += earned
        self.total_clicks += 1
        return earned

    def add_hats(self, amount: float) -> None:
        """Add hats to both the current spendable balance and lifetime accumulation."""
        if amount > 0:
            self.total_hats += amount
            self.lifetime_hats += amount

    def to_dict(self) -> dict[str, Any]:
        """Serialize state according to the save state specification."""
        return {
            "version": 1,
            "last_saved_timestamp": self.last_saved_timestamp,
            "total_hats": self.total_hats,
            "lifetime_hats": self.lifetime_hats,
            "total_clicks": self.total_clicks,
            "hps": self.hps,
            "generators": dict(self.generators),
            "upgrades_unlocked": list(self.upgrades_unlocked),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GameState":
        """Reconstruct GameState from a serialized dictionary."""
        return cls(
            total_hats=float(data.get("total_hats", 0.0)),
            lifetime_hats=float(data.get("lifetime_hats", 0.0)),
            total_clicks=int(data.get("total_clicks", 0)),
            hps=float(data.get("hps", 0.0)),
            click_power=float(data.get("click_power", BASE_CLICK_VALUE)),
            generators=dict(data.get("generators", {})),
            upgrades_unlocked=list(data.get("upgrades_unlocked", [])),
            last_saved_timestamp=float(data.get("last_saved_timestamp", time.time())),
        )
