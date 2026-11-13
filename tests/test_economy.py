"""Unit tests for the economy engine, product store, and generator catalog."""

import pytest
import pygame

from src.config import PRICE_GROWTH_RATE, WINDOW_HEIGHT, WINDOW_WIDTH
from src.engine.economy import (
    calculate_bulk_cost,
    calculate_generator_cost,
    calculate_max_affordable,
    calculate_offline_earnings,
    calculate_total_hps,
)
from src.engine.state import GameState
from src.models.generator import GENERATOR_CATALOG, Generator, get_default_generators
from src.ui.store import StorePanel


def test_cost_scaling_and_bulk_purchase():
    """Verify geometric cost scaling (r=1.15) and floored bulk purchase calculations."""
    base_cost = 15  # RHEL base cost
    assert calculate_generator_cost(base_cost, 0) == 15
    assert calculate_generator_cost(base_cost, 1) == 17  # floor(15 * 1.15) = 17
    assert calculate_generator_cost(base_cost, 2) == 19  # floor(15 * 1.15^2) = 19

    # Bulk cost for first 10 units must equal sum of individual costs (15 + 17 + 19 + ...)
    expected_sum = sum(int(base_cost * (1.15 ** i)) for i in range(10))
    assert calculate_bulk_cost(base_cost, current_count=0, quantity=10) == expected_sum


def test_passive_generation_and_delta_time():
    """Verify total HPS calculation and delta-time currency accumulation."""
    state = GameState()
    # 10 RHEL (0.1 HPS each = 1.0) and 2 Ansible (1.0 HPS each = 2.0)
    generators = {
        "rhel": Generator(id="rhel", name="RHEL", base_cost=15, base_hps=0.1, count=10),
        "ansible": Generator(id="ansible", name="Ansible", base_cost=100, base_hps=1.0, count=2),
    }
    total_hps = calculate_total_hps(generators)
    assert pytest.approx(total_hps, rel=1e-5) == 3.0

    # Simulate 0.5s elapsed time
    dt = 0.5
    state.add_hats(total_hps * dt)
    assert pytest.approx(state.total_hats, rel=1e-5) == 1.5


def test_bulk_cost_edge_cases():
    """Verify edge cases for bulk purchase cost calculations."""
    base_cost = 100
    # Zero or negative quantity should return 0 cost
    assert calculate_bulk_cost(base_cost, current_count=0, quantity=0) == 0
    assert calculate_bulk_cost(base_cost, current_count=5, quantity=-3) == 0
    assert calculate_bulk_cost(0, current_count=0, quantity=10) == 0

    # 1x bulk cost must equal single unit generator cost
    assert calculate_bulk_cost(base_cost, current_count=4, quantity=1) == calculate_generator_cost(base_cost, 4)

    # 100x bulk cost equals sum of 100 individual terms
    sum_100 = sum(calculate_generator_cost(base_cost, 2 + i) for i in range(100))
    assert calculate_bulk_cost(base_cost, current_count=2, quantity=100) == sum_100


def test_max_affordable_calculation():
    """Verify max affordable units calculation with inverted series and stepwise check."""
    base_cost = 15

    # Budget 0 or less than 1st unit cost
    assert calculate_max_affordable(base_cost, current_count=0, budget=0) == 0
    assert calculate_max_affordable(base_cost, current_count=0, budget=14) == 0

    # Exact budget for 1 unit (15)
    res_1 = calculate_max_affordable(base_cost, current_count=0, budget=15)
    assert res_1 == 1
    assert res_1.cost == 15

    # Budget 50: cost(0)=15, cost(1)=17 -> 32 <= 50. cost(2)=19 -> 32+19=51 > 50.
    res_2 = calculate_max_affordable(base_cost, current_count=0, budget=50)
    assert res_2 == 2
    assert res_2.cost == 32

    # Verify tuple unpacking and equality
    units, cost = calculate_max_affordable(base_cost, current_count=0, budget=50)
    assert units == 2
    assert cost == 32
    assert (units, cost) == (2, 32)
    assert res_2 == (2, 32)

    # Large budget test: verify cost(k) <= budget and cost(k+1) > budget
    large_budget = 50000.0
    current_count = 10
    k = calculate_max_affordable(base_cost, current_count, large_budget)
    assert k > 0
    k_cost = calculate_bulk_cost(base_cost, current_count, k)
    next_cost = calculate_bulk_cost(base_cost, current_count, k + 1)
    assert k_cost <= large_budget
    assert next_cost > large_budget


def test_generator_catalog_integrity():
    """Verify all 8 authentic Red Hat product tiers match game design specifications."""
    catalog = get_default_generators()
    assert len(catalog) == 8

    expected_tiers = [
        ("rhel", "Red Hat Enterprise Linux (RHEL)", 15, 0.1, 0.0),
        ("ansible", "Ansible Automation Platform", 100, 1.0, 50.0),
        ("satellite", "Red Hat Satellite", 1100, 8.0, 500.0),
        ("openshift", "Red Hat OpenShift", 12000, 47.0, 5000.0),
        ("openstack", "Red Hat OpenStack Platform", 130000, 260.0, 50000.0),
        ("ceph", "Red Hat Ceph Storage", 1400000, 1400.0, 500000.0),
        ("rhacm", "Advanced Cluster Management (RHACM)", 20000000, 7800.0, 8000000.0),
        ("openshift_ai", "Red Hat OpenShift AI", 330000000, 44000.0, 100000000.0),
    ]

    for gen_id, name, base_cost, base_hps, unlock_req in expected_tiers:
        assert gen_id in catalog
        gen = catalog[gen_id]
        assert gen.id == gen_id
        assert gen.name == name
        assert gen.base_cost == base_cost
        assert gen.base_hps == base_hps
        assert gen.unlock_requirement == unlock_req
        assert gen.count == 0
        assert gen.multiplier == 1.0


def test_generator_unlock_logic():
    """Verify generators unlock according to lifetime Red Hats produced."""
    catalog = get_default_generators()
    rhel = catalog["rhel"]
    ansible = catalog["ansible"]
    satellite = catalog["satellite"]

    # RHEL unlocked immediately
    assert rhel.is_unlocked(0) is True
    assert rhel.is_unlocked(10) is True

    # Ansible requires 50 lifetime RH
    assert ansible.is_unlocked(0) is False
    assert ansible.is_unlocked(49.9) is False
    assert ansible.is_unlocked(50.0) is True

    # Satellite requires 500 lifetime RH
    assert satellite.is_unlocked(499) is False
    assert satellite.is_unlocked(500) is True


def test_offline_earnings_calculation():
    """Verify offline production accumulation and cap clamping."""
    hps = 10.0
    # 1 hour (3600 seconds) offline
    assert calculate_offline_earnings(hps, 3600.0) == 36000.0

    # Negative elapsed time clamped to 0
    assert calculate_offline_earnings(hps, -100.0) == 0.0

    # Elapsed time exceeding 8h cap (28800s) is clamped
    assert calculate_offline_earnings(hps, 50000.0, max_cap_seconds=28800.0) == 288000.0

    # Efficiency factor
    assert calculate_offline_earnings(hps, 1000.0, efficiency=0.5) == 5000.0


def test_game_state_buy_generator_discrete():
    """Verify GameState buying 1x, 10x, and 100x generator units."""
    state = GameState()
    catalog = get_default_generators()

    # Attempt to buy RHEL without sufficient balance
    assert state.total_hats == 0
    assert state.buy_generator("rhel", quantity=1, catalog=catalog) is False
    assert state.get_generator_count("rhel") == 0
    assert state.hps == 0.0

    # Give player 500 hats
    state.add_hats(500.0)
    # Buy 1 RHEL (cost: 15)
    success = state.buy_generator("rhel", quantity=1, catalog=catalog)
    assert success is True
    assert state.total_hats == 485.0
    assert state.get_generator_count("rhel") == 1
    assert pytest.approx(state.hps, rel=1e-5) == 0.1

    # Buy 10 RHEL starting from count=1 (cost: sum(floor(15 * 1.15^i) for i in range(1, 11)))
    cost_10 = calculate_bulk_cost(15, current_count=1, quantity=10)
    assert state.total_hats >= cost_10
    success_10 = state.buy_generator("rhel", quantity=10, catalog=catalog)
    assert success_10 is True
    assert state.get_generator_count("rhel") == 11
    assert pytest.approx(state.hps, rel=1e-5) == 1.1


def test_game_state_buy_generator_max():
    """Verify GameState buying maximum affordable generator units."""
    state = GameState()
    catalog = get_default_generators()

    # Player has 50 hats, count=0 -> max affordable RHEL is 2 units (cost: 32)
    state.add_hats(50.0)
    success = state.buy_generator("rhel", quantity="max", catalog=catalog)
    assert success is True
    assert state.get_generator_count("rhel") == 2
    assert state.total_hats == 18.0  # 50 - 32 = 18 (cannot afford 3rd unit which costs 19)

    # Next attempt with 18 hats should fail (next costs 19)
    assert state.buy_generator("rhel", quantity="max", catalog=catalog) is False
    assert state.get_generator_count("rhel") == 2


def test_store_panel_interactions_and_rendering():
    """Verify StorePanel quantity toggles, scrolling, and rendering cycle."""
    if not pygame.font.get_init():
        pygame.font.init()

    panel = StorePanel(x=860, y=0, width=420, height=WINDOW_HEIGHT)
    state = GameState()
    catalog = get_default_generators()

    # Test quantity toggle clicks
    assert panel.selected_quantity == 1
    # Click 10x toggle button
    rect_10x = panel.get_quantity_toggle_rect(1)
    event_click_10 = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": rect_10x.center, "button": 1})
    handled = panel.handle_event(event_click_10, state, catalog)
    assert handled is True
    assert panel.selected_quantity == 10

    # Click Max toggle button
    rect_max = panel.get_quantity_toggle_rect(3)
    event_click_max = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": rect_max.center, "button": 1})
    handled = panel.handle_event(event_click_max, state, catalog)
    assert handled is True
    assert panel.selected_quantity == "Max"

    # Test mouse wheel scroll on a panel with constrained height
    small_panel = StorePanel(x=860, y=0, width=420, height=400)
    assert small_panel.scroll_y == 0.0
    scroll_down = pygame.event.Event(pygame.MOUSEWHEEL, {"y": -1, "x": 0, "pos": (900, 200)})
    small_panel.handle_event(scroll_down, state, catalog)
    assert small_panel.scroll_y > 0.0

    scroll_up = pygame.event.Event(pygame.MOUSEWHEEL, {"y": 2, "x": 0, "pos": (900, 200)})
    small_panel.handle_event(scroll_up, state, catalog)
    assert small_panel.scroll_y == 0.0

    # Test purchasing via clicking card in StorePanel
    state.add_hats(100.0)
    panel.selected_quantity = 1
    rhel_card_rect = panel.get_card_rect(0)
    click_rhel = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": rhel_card_rect.center, "button": 1})
    purchased = panel.handle_event(click_rhel, state, catalog)
    assert purchased is True
    assert state.get_generator_count("rhel") == 1
    assert state.total_hats == 85.0

    # Test drawing StorePanel
    surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    font_h = pygame.font.Font(None, 36)
    font_sub = pygame.font.Font(None, 24)
    font_sm = pygame.font.Font(None, 20)
    panel.draw(surface, state, catalog, font_h, font_sub, font_sm)
