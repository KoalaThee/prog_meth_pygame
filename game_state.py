from dataclasses import dataclass


@dataclass
class GameState:
    """Persistent stats for the whole run (survives player swaps)."""

    health: int = 0
    happiness: int = 0
    social: int = 0
    intelligence: int = 0
    arts: int = 0
