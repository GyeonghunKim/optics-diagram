from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Tuple


@dataclass
class Arrow:
    start: Tuple[float, float]
    end: Tuple[float, float]
    color: str | Tuple[float, float, float] = "black"
    linewidth: float = 1.5
    style: str = "->"

    def draw(self, ax: Any) -> None:
        import matplotlib.pyplot as plt  # deferred import

        ax.annotate(
            "",
            xy=self.end,
            xytext=self.start,
            arrowprops=dict(arrowstyle=self.style, color=self.color, lw=self.linewidth),
        )
