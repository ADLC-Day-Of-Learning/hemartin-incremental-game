"""Data models and catalog structures for generators and upgrades."""

from src.models.generator import (
    GENERATOR_CATALOG,
    GENERATOR_DEFINITIONS,
    Generator,
    get_default_generators,
)

__all__ = [
    "GENERATOR_CATALOG",
    "GENERATOR_DEFINITIONS",
    "Generator",
    "get_default_generators",
]
