from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import matplotlib.patches as patches


@dataclass
class FiberEOM:
    x: float
    y: float
    width: float = 0.9
    height: float = 0.4

    def draw(self, ax: Any) -> None:
        rect = patches.Rectangle(
            (self.x - self.width / 2, self.y - self.height / 2),
            self.width,
            self.height,
            linewidth=1.2,
            edgecolor="#b2641a",
            facecolor="#f8e7d6",
        )
        ax.add_patch(rect)
        ax.text(self.x, self.y, "FEOM", ha="center", va="center")


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")

    demo = FiberEOM(x=0.0, y=0.0)
    demo.draw(ax)

    ax.set_xlim(-2, 2)
    ax.set_ylim(-1.5, 1.5)
    fig.savefig("fiber_eom_demo.png", dpi=200, bbox_inches="tight")
