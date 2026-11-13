# Red Hat Clicker (Incremental Game)

An incremental / idle game inspired by classic clickers such as *Cookie Clicker*. Players collect **Red Hats** by clicking a giant Red Hat and reinvest their hats to deploy enterprise-grade **Red Hat products and platforms** as automated hat generators.

---

## Table of Contents

1. [Game Overview](#game-overview)
2. [Core Game Mechanics & Economy](#core-game-mechanics--economy)
   - [Currency & Generation](#currency--generation)
   - [Cost Scaling Formulas](#cost-scaling-formulas)
   - [Tick Mechanics & Offline Progress](#tick-mechanics--offline-progress)
3. [Red Hat Offerings Catalog (Generators)](#red-hat-offerings-catalog-generators)
   - [Generator Tiers](#generator-tiers)
   - [Upgrades & Synergies](#upgrades--synergies)
4. [Technical Architecture](#technical-architecture)
   - [Technology Stack](#technology-stack)
   - [Directory Structure](#directory-structure)
   - [Core Subsystems](#core-subsystems)
   - [Save State Specification](#save-state-specification)
5. [Development & Execution](#development--execution)
   - [Prerequisites](#prerequisites)
   - [Installation](#installation)
   - [Running the Game](#running-the-game)
   - [Running Tests](#running-tests)
6. [Implementation Roadmap](#implementation-roadmap)

---

## Game Overview

- **Genre:** Incremental / Idle / Clicker
- **Platform:** Desktop (cross-platform via Python & Pygame)
- **Theme:** Open source enterprise infrastructure and cloud solutions
- **Primary Objective:** Scale Red Hat production from a single manual terminal click into an automated, multi-cloud enterprise producing millions of Red Hats per second.

---

## Core Game Mechanics & Economy

### Currency & Generation

- **Primary Currency:** **Red Hats** ($\text{RH}$)
- **Secondary Statistic:** **Hats Per Second** ($\text{HPS}$)
- **Manual Click:**
  - Base production: $1\text{ RH}$ per click.
  - Scale with click upgrades and global production multipliers:
    $$\text{Click Value} = (1 + \text{Click Upgrades}) \times \text{Global Multiplier} + (\alpha \times \text{HPS})$$
    *(where $\alpha$ is a late-game bonus percentage of passive HPS added to each manual click).*
- **Passive Generation:**
  - Each generator tier produces a base rate of $\text{HPS}$.
  - Total passive production is calculated as:
    $$\text{Total HPS} = \sum_{i=1}^{M} \left( \text{count}_i \times \text{base\_hps}_i \times \text{multiplier}_i \right) \times \text{Global Multiplier}$$

### Cost Scaling Formulas

Generators follow standard geometric exponential cost scaling:

$$\text{Cost}(n) = \left\lfloor \text{BaseCost} \times r^n \right\rfloor$$

- $n$: Number of units currently owned of that generator.
- $r$: Price growth rate factor, set to **$1.15$** (standard incremental game standard).
- $\text{BaseCost}$: Initial purchase price for the first unit.

#### Bulk Purchases

To calculate the cost of buying $k$ units at once (e.g., 10x, 100x):

$$\text{Cost}(n, k) = \sum_{j=0}^{k-1} \text{Cost}(n + j) = \text{BaseCost} \times \frac{r^n \times (r^k - 1)}{r - 1}$$

To calculate the maximum affordable units $\text{Max}(n)$ with budget $B$:

$$k_{\max} = \left\lfloor \frac{\ln\left(1 + \frac{B \times (r - 1)}{\text{BaseCost} \times r^n}\right)}{\ln(r)} \right\rfloor$$

### Tick Mechanics & Offline Progress

- **Frame Rate & Tick Rate:**
  - Rendering Target: 60 FPS.
  - Simulation Tick: Delta-time ($\Delta t$) accumulated per frame to decouple logic from render framerate.
- **Production Update:**
  $$\Delta \text{Hats} = \text{Total HPS} \times \Delta t$$
- **Offline Progress:**
  - On application startup, compare current UNIX timestamp against the last saved timestamp.
  - Offline earnings credit:
    $$\text{Offline Hats} = \text{Total HPS} \times \min(\text{Elapsed Time}, \text{Max Offline Cap}) \times \text{Efficiency Factor}$$
  - Default cap: 8 hours; default efficiency: 100% (or configurable via upgrades).

---

## Red Hat Offerings Catalog (Generators)

Each generator represents an authentic Red Hat product or technology offering. As players progress, higher-tier offerings unlock based on lifetime hats produced or total generators owned.

### Generator Tiers

| Tier | Generator Name | Flavor / Description | Base Cost ($\text{RH}$) | Base Output ($\text{HPS}$) | Unlock Requirement |
| :---: | :--- | :--- | :---: | :---: | :--- |
| **1** | **Red Hat Enterprise Linux (RHEL)** | The world's leading enterprise Linux platform. Reliable workstation instances cranking out hats. | 15 | 0.1 | 0 RH produced |
| **2** | **Ansible Automation Platform** | Automation playbooks automating repetitive hat provisioning tasks across systems. | 100 | 1.0 | 50 RH produced |
| **3** | **Red Hat Satellite** | Scalable infrastructure management patching, provisioning, and auditing hat nodes. | 1,100 | 8.0 | 500 RH produced |
| **4** | **Red Hat OpenShift** | Enterprise Kubernetes container platform scaling hat microservices across pods. | 12,000 | 47.0 | 5,000 RH produced |
| **5** | **Red Hat OpenStack Platform** | Private cloud infrastructure orchestrating virtualized hat compute instances. | 130,000 | 260.0 | 50,000 RH produced |
| **6** | **Red Hat Ceph Storage** | Massively scalable, software-defined storage holding exabytes of Red Hats. | 1,400,000 | 1,400.0 | 500,000 RH produced |
| **7** | **Advanced Cluster Management (RHACM)** | Fleet-wide governance, security, and multi-cluster orchestration for distributed hats. | 20,000,000 | 7,800.0 | 8,000,000 RH produced |
| **8** | **Red Hat OpenShift AI** | Train and deploy generative foundation models designed to invent new Red Hats. | 330,000,000 | 44,000.0 | 100,000,000 RH produced |

### Upgrades & Synergies

Upgrades are one-time purchases that permanently enhance specific products, click power, or global multipliers.

1. **RHEL Hardening (SELinux Enforcement):** Doubles RHEL base HPS.
2. **Ansible Galaxy Collections:** Doubles Ansible base HPS.
3. **Satellite Smart Proxies:** Satellite output increased by +1% for every 10 RHEL instances.
4. **OpenShift Operators:** Doubles OpenShift base HPS and auto-clicks once every 5 seconds.
5. **Ceph CRUSH Map Optimization:** Ceph output increased by +5% per OpenStack instance.
6. **GitOps with ArgoCD:** Increases global HPS by 10%.
7. **Open Source Contribution:** Increases click value based on total buildings owned.

---

## Technical Architecture

### Technology Stack

- **Language:** Python 3.10+
- **Graphics & Audio Framework:** `pygame` (or `pygame-ce` for enhanced performance and modern platform support)
- **State Serialization:** Standard library `json` (human-readable, robust, zero external dependencies)
- **Packaging / Testing:** Standard Python virtual environments (`venv`), `pytest` for game economy & logic tests

### Directory Structure

```text
hemartin-incremental-game/
├── assets/
│   ├── fonts/               # UI fonts (e.g., Red Hat Text / Display open fonts)
│   ├── images/              # Hat graphics, product icons, UI sprites
│   └── sounds/              # Click SFX, purchase SFX, ambient audio
├── src/
│   ├── __init__.py
│   ├── main.py              # Application entry point; game loop lifecycle
│   ├── config.py            # Window constants, colors, target FPS, economy defaults
│   ├── engine/
│   │   ├── __init__.py
│   │   ├── game.py          # Primary Game class managing state transitions & loop
│   │   ├── economy.py       # Pure calculation functions: cost, HPS, offline gains
│   │   └── state.py         # GameState data model and JSON serialization/loading
│   ├── models/
│   │   ├── __init__.py
│   │   ├── generator.py     # Generator dataclass & product catalog definition
│   │   └── upgrade.py       # Upgrade dataclass, unlock conditions, modifier effects
│   └── ui/
│       ├── __init__.py
│       ├── renderer.py      # Display surfaces, layer composition, font rendering
│       ├── components.py    # Reusable UI widgets: buttons, progress bars, tooltips
│       ├── hat_button.py    # Interactive central Red Hat (scale animations, particle popups)
│       └── store.py         # Product catalog list, purchase buttons, price tags
├── tests/
│   ├── __init__.py
│   ├── test_economy.py      # Unit tests for geometric pricing, HPS math, bulk buying
│   └── test_state.py        # Unit tests for save/load serialization, backward compatibility
├── requirements.txt         # Runtime and development dependencies
└── README.md                # Project documentation and architectural plan
```

### Core Subsystems

```text
+-------------------------------------------------------------+
|                          main.py                            |
|             (Pygame Init, Event Loop, Clock Tick)           |
+-------------------------------------------------------------+
                               |
                               v
+-------------------------------------------------------------+
|                          Game Engine                        |
|                                                             |
|  +--------------------+             +--------------------+  |
|  |     GameState      |<----------->|      Economy       |  |
|  |  (Hat counts,      |             |  (HPS, Cost math,  |  |
|  |   Generators,      |             |   Multipliers,     |  |
|  |   Upgrades owned)  |             |   Offline calc)    |  |
|  +--------------------+             +--------------------+  |
+-------------------------------------------------------------+
           |                                       |
           v                                       v
+-----------------------+              +----------------------+
|     Save / Load       |              |      UI System       |
|  (JSON serialization, |              |  (Left: Big Hat      |
|   auto-save timer)    |              |   Center: Stats/News |
+-----------------------+              |   Right: Store UI)   |
                                       +----------------------+
```

1. **Game Engine (`src/engine/game.py`):**
   - Coordinates timing, user inputs, state updates, and rendering.
   - Fixed or delta-time updates to ensure consistent simulation across systems.
2. **Economy System (`src/engine/economy.py`):**
   - Pure, stateless math functions for costs, bulk purchases, and generation rates.
   - Easily covered by unit tests without requiring a Pygame display context.
3. **User Interface (`src/ui/`):**
   - **Left Panel:** Big clickable Red Hat, pulsing animations, floating click numbers (`+1`, `+50`), current Red Hats balance, and total HPS.
   - **Center Panel:** Recent achievements, active synergy bonuses, statistics (lifetime clicks, time played).
   - **Right Panel:** Scrollable store showing Red Hat offerings, current ownership count, calculated price, and purchase quantity toggle (`1x`, `10x`, `100x`, `Max`).
4. **Audio & Asset Manager:**
   - Pre-loads sound effects (clicking, purchasing, upgrade chimes) and graphical surfaces.
   - Graceful fallback: runs headlessly or with procedural shapes/colors if image/audio assets are absent.

### Save State Specification

Game progress is saved to a local JSON file (`savegame.json` in user data directory or local repository root):

```json
{
  "version": 1,
  "last_saved_timestamp": 1794561848,
  "total_hats": 14250.75,
  "lifetime_hats": 35890.0,
  "total_clicks": 420,
  "generators": {
    "rhel": 25,
    "ansible": 12,
    "satellite": 3,
    "openshift": 1,
    "openstack": 0,
    "ceph": 0,
    "rhacm": 0,
    "openshift_ai": 0
  },
  "upgrades_unlocked": [
    "rhel_hardening_selinux",
    "ansible_galaxy_collections"
  ],
  "settings": {
    "sfx_volume": 0.8,
    "music_volume": 0.5,
    "floating_numbers": true
  }
}
```

---

## Development & Execution

### Prerequisites

- Python 3.10 or higher
- `pip` (Python package installer)

### Installation

1. Clone the repository and navigate into the project directory:
   ```bash
   git clone https://github.com/ADLC-Day-Of-Learning/hemartin-incremental-game.git
   cd hemartin-incremental-game
   ```

2. Create and activate a Python virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   # On Windows: .venv\Scripts\activate
   ```

3. Install project dependencies:
   ```bash
   pip install -r requirements.txt
   ```

   *(Dependencies include `pygame-ce>=2.4.0` or `pygame>=2.5.0` and `pytest>=7.0.0` for testing).*

### Running the Game

Launch the game application via Python:

```bash
python -m src.main
```

### Running Tests

Execute the unit test suite to verify economic formulas, state saving/loading, and catalog integrity:

```bash
pytest
```

---

## Implementation Roadmap

The implementation is broken down into modular, sequential phases for development:

- [x] **Phase 1: Game Design & Architecture Plan** (Issue #2)
  - [x] Document core game loop and economic balance models.
  - [x] Define tiered Red Hat products catalog and scaling formulas.
  - [x] Design technical architecture, directory structure, and save specification.
  - [x] Publish implementation blueprint in `README.md`.
- [ ] **Phase 2: Project Scaffold & Minimal Pygame Loop**
  - [ ] Set up `requirements.txt` with Pygame and Pytest.
  - [ ] Initialize project directories and config modules (`src/config.py`).
  - [ ] Build basic 60 FPS Pygame loop with window handling in `src/main.py`.
  - [ ] Implement clickable central Red Hat button and basic click counter.
- [ ] **Phase 3: Economy Engine & Product Store**
  - [ ] Implement `src/engine/economy.py` with cost formulas and HPS calculation.
  - [ ] Create Red Hat product generator definitions in `src/models/generator.py`.
  - [ ] Build scrollable store UI panel with buy buttons (1x, 10x, 100x).
  - [ ] Implement delta-time passive income accumulation in the main loop.
  - [ ] Add unit tests for cost scaling and income mechanics.
- [ ] **Phase 4: Save / Load State Persistence**
  - [ ] Implement `src/engine/state.py` for JSON serialization and deserialization.
  - [ ] Implement auto-save on interval and save-on-exit.
  - [ ] Add offline earnings calculation based on elapsed timestamp.
  - [ ] Add unit tests for state serialization and corrupt file resilience.
- [ ] **Phase 5: Upgrades & Synergies System**
  - [ ] Create upgrade catalog and modifier system in `src/models/upgrade.py`.
  - [ ] Build upgrade store / shelf UI component.
  - [ ] Implement product synergy multipliers (e.g., Satellite boosting RHEL).
- [ ] **Phase 6: Audio, Visuals & UI Polish**
  - [ ] Add custom graphics for Red Hat products and themed hat sprites.
  - [ ] Implement particle effects, floating click texts (`+1`), and pulse animations.
  - [ ] Add sound effects for clicks, purchases, and achievements with volume settings.
- [ ] **Phase 7: Achievements, Statistics & Prestige**
  - [ ] Build statistics tracking (lifetime clicks, peak HPS, total play time).
  - [ ] Implement milestone achievements with cosmetic or bonus rewards.
  - [ ] Add "Enterprise Reorganization" prestige mechanic (soft reset with permanent multipliers).
