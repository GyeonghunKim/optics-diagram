from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Tuple


@dataclass
class Annotation:
    text: str
    xy: Tuple[float, float]
    xytext: Optional[Tuple[float, float]] = None
    arrow: bool = False
    fontsize: int = 10
    color: str | Tuple[float, float, float] = "black"

    def draw(self, ax: Any) -> None:
        import matplotlib.pyplot as plt  # deferred import

        if self.arrow and self.xytext is not None:
            ax.annotate(
                self.text,
                xy=self.xy,
                xytext=self.xytext,
                textcoords="data",
                fontsize=self.fontsize,
                color=self.color,
                arrowprops=dict(arrowstyle="->", color=self.color),
            )
        else:
            ax.text(
                self.xy[0],
                self.xy[1],
                self.text,
                fontsize=self.fontsize,
                color=self.color,
            )
