"""Game state data model and lifecycle for Red Hat Clicker."""

from dataclasses import dataclass, field
import time
from typing import Any, Optional, Union

from src.config import BASE_CLICK_VALUE
from src.engine.economy import (
    calculate_bulk_cost,
    calculate_max_affordable,
    calculate_total_hps,
)
from src.models.generator import Generator, get_default_generators


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

    def can_afford(self, cost: float) -> bool:
        """Check whether current balance can cover a given cost."""
        return self.total_hats >= cost

    def spend_hats(self, amount: float) -> bool:
        """Deduct hats from spendable balance if affordable."""
        if amount <= 0:
            return True
        if self.total_hats >= amount:
            self.total_hats -= amount
            return True
        return False

    def get_generator_count(self, gen_id: str) -> int:
        """Get the count of owned generators for a specific product ID."""
        return self.generators.get(gen_id, 0)

    def recalculate_hps(
        self,
        catalog: Optional[dict[str, Generator]] = None,
        global_multiplier: float = 1.0,
    ) -> float:
        """Recalculate passive HPS from owned generators and update state."""
        self.hps = calculate_total_hps(
            self.generators,
            global_multiplier=global_multiplier,
            catalog=catalog,
        )
        return self.hps

    def buy_generator(
        self,
        gen_id: str,
        quantity: Union[int, str] = 1,
        catalog: Optional[dict[str, Generator]] = None,
    ) -> bool:
        """Attempt to purchase units of a generator offering.

        Supports discrete quantities (e.g. 1, 10, 100) or 'max' to buy all affordable.
        Returns True if purchase succeeded, False otherwise.
        """
        cat = catalog or get_default_generators()
        gen = cat.get(gen_id)
        if gen is None:
            return False

        current_count = self.get_generator_count(gen_id)

        if str(quantity).lower() == "max":
            max_res = calculate_max_affordable(gen.base_cost, current_count, self.total_hats)
            units_to_buy = int(max_res)
            if units_to_buy <= 0:
                return False
            cost = max_res.cost
        else:
            try:
                units_to_buy = int(quantity)
            except (ValueError, TypeError):
                return False

            if units_to_buy <= 0:
                return False

            cost = calculate_bulk_cost(gen.base_cost, current_count, units_to_buy)

        if self.spend_hats(cost):
            self.generators[gen_id] = current_count + units_to_buy
            self.recalculate_hps(catalog=cat)
            return True

        return False

    def to_dict(self) -> dict[str, Any]:
        """Serialize state according to the save state specification."""
        return {
            "version": 1,
            "last_saved_timestamp": self.last_saved_timestamp,
            "total_hats": self.total_hats,
            "lifetime_hats": self.lifetime_hats,
            "total_clicks": self.total_clicks,
            "hps": self.hps,
            "click_power": self.click_power,
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
