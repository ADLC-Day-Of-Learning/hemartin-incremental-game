"""Economy calculation engine for Red Hat Clicker.

Provides pure mathematical functions for exponential cost scaling, bulk purchasing,
maximum affordability estimation with stepwise refinement, and HPS accumulation.
"""

from collections.abc import Iterable
import math
from typing import Any, Optional, Union

from src.config import PRICE_GROWTH_RATE
from src.models.generator import Generator, get_default_generators


class MaxAffordableResult(int):
    """Result of calculate_max_affordable containing units and total cost.

    Subclasses int so it behaves as an integer count of affordable units,
    while also supporting tuple unpacking `(count, cost)`, indexing, and `.cost`.
    """

    cost: int

    def __new__(cls, quantity: int, cost: int) -> "MaxAffordableResult":
        obj = super().__new__(cls, quantity)
        obj.cost = int(cost)
        return obj

    def __iter__(self):
        yield int(self)
        yield self.cost

    def __len__(self) -> int:
        return 2

    def __getitem__(self, index: int) -> int:
        return (int(self), self.cost)[index]

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, tuple):
            return (int(self), self.cost) == other
        return super().__eq__(other)

    def __ne__(self, other: Any) -> bool:
        return not (self == other)


def calculate_generator_cost(
    base_cost: float,
    current_count: int,
    growth_rate: float = PRICE_GROWTH_RATE,
) -> int:
    """Calculate the purchase cost of the next single generator unit.

    Cost(n) = floor(BaseCost * r^n)
    """
    if current_count < 0:
        return 0
    return int(math.floor(base_cost * (growth_rate ** current_count)))


def calculate_bulk_cost(
    base_cost: float,
    current_count: int,
    quantity: int,
    growth_rate: float = PRICE_GROWTH_RATE,
) -> int:
    """Calculate the exact cost of purchasing `quantity` units in discrete batches.

    Sum of individual floored terms prevents overcharging players relative
    to sequential 1x purchases and avoids fractional hat amounts.
    """
    if quantity <= 0 or base_cost <= 0:
        return 0

    return sum(
        calculate_generator_cost(base_cost, current_count + i, growth_rate)
        for i in range(quantity)
    )


def calculate_max_affordable(
    base_cost: float,
    current_count: int,
    budget: float,
    growth_rate: float = PRICE_GROWTH_RATE,
) -> MaxAffordableResult:
    """Calculate the maximum affordable units and total cost given an available budget.

    Uses an inverted continuous geometric series as a baseline lower-bound estimate,
    then applies discrete stepwise refinement to find the exact affordable count.
    """
    if budget <= 0 or base_cost <= 0:
        return MaxAffordableResult(0, 0)

    # Check if player can afford at least 1 unit
    first_unit_cost = calculate_generator_cost(base_cost, current_count, growth_rate)
    if budget < first_unit_cost:
        return MaxAffordableResult(0, 0)

    # Inverted continuous formula:
    # k_est = floor( ln(1 + B * (r - 1) / (BaseCost * r^n)) / ln(r) )
    r = growth_rate
    denominator = base_cost * (r ** current_count)
    if denominator <= 0:
        return MaxAffordableResult(0, 0)

    term = 1.0 + (budget * (r - 1.0)) / denominator
    if term > 1.0:
        k_est = max(0, int(math.floor(math.log(term) / math.log(r))))
    else:
        k_est = 0

    k = k_est
    cost = calculate_bulk_cost(base_cost, current_count, k, growth_rate)

    # In rare numerical edge cases where k_est might exceed budget:
    while k > 0 and cost > budget:
        k -= 1
        cost = calculate_bulk_cost(base_cost, current_count, k, growth_rate)

    # Stepwise refinement upward: floored terms are <= continuous terms,
    # so k_est may underestimate affordable units by 1 or more.
    while True:
        next_cost = calculate_generator_cost(base_cost, current_count + k, growth_rate)
        if cost + next_cost <= budget:
            k += 1
            cost += next_cost
        else:
            break

    return MaxAffordableResult(k, cost)


def calculate_total_hps(
    generators: Union[dict[str, Any], Iterable[Any]],
    global_multiplier: float = 1.0,
    catalog: Optional[dict[str, Generator]] = None,
) -> float:
    """Calculate total passive Hats Per Second (HPS) across all generators.

    Supports:
    - Dict mapping generator IDs to Generator instances
    - Iterable of Generator instances
    - Dict mapping generator IDs to integer counts (using catalog or default catalog)
    """
    if isinstance(generators, dict):
        total = 0.0
        for gen_id, item in generators.items():
            if isinstance(item, (int, float)):
                # Integer count mode from GameState
                cat = catalog or get_default_generators()
                gen = cat.get(gen_id)
                if gen:
                    total += item * gen.base_hps * gen.multiplier
            else:
                count = getattr(item, "count", 0)
                base_hps = getattr(item, "base_hps", 0.0)
                multiplier = getattr(item, "multiplier", 1.0)
                total += count * base_hps * multiplier
        return total * global_multiplier

    total = sum(
        getattr(g, "count", 0) * getattr(g, "base_hps", 0.0) * getattr(g, "multiplier", 1.0)
        for g in generators
    )
    return total * global_multiplier


def calculate_offline_earnings(
    hps: float,
    elapsed_seconds: float,
    max_cap_seconds: float = 28800.0,
    efficiency: float = 1.0,
) -> float:
    """Calculate offline production credited since last saved timestamp.

    Caps maximum offline time (default 8 hours) and ensures non-negative earnings.
    """
    effective_seconds = max(0.0, min(elapsed_seconds, max_cap_seconds))
    return hps * effective_seconds * max(0.0, efficiency)
