"""Application entry point and primary Pygame execution loop."""

import sys
from src.engine.game import Game


def main() -> int:
    """Initialize and run the Red Hat Clicker main game loop."""
    game = Game()
    game.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
