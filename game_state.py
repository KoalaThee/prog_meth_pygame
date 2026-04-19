from dataclasses import dataclass, fields


@dataclass
class GameState:
    """Persistent stats for the whole run (survives player swaps)."""

    health: int = 50
    happiness: int = 0
    intelligence: int = 0
    arts: int = 0
    social: int = 0

    def apply(self, effects: dict[str, int]) -> None:
        """Add ``effects`` to the matching stats. Unknown stat names raise ``KeyError``."""
        valid = {f.name for f in fields(self)}
        for stat, delta in effects.items():
            if stat not in valid:
                raise KeyError(f"Unknown stat: {stat!r}")
            setattr(self, stat, getattr(self, stat) + delta)