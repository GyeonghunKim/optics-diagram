from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from optics_diagram.beam import BeamPoint
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.transforms import Affine2D


@dataclass
class PBS:
    x: float = 0.0
    y: float = 0.0
    angle_deg: float = 45.0
    size: float = 0.8
    edgecolor: str = "black"
    linewidth: float = 1.0

    def draw(self, ax: Any) -> None:
        cx, cy = self.x, self.y
        s = self.size
        tr = Affine2D().rotate_deg_around(cx, cy, self.angle_deg) + ax.transData

        # Outline square (no facecolor; we'll paint a clipped gradient under it)
        square = patches.Rectangle(
            (cx - s / 2, cy - s / 2),
            s,
            s,
            linewidth=self.linewidth,
            edgecolor=self.edgecolor,
            facecolor="none",
            zorder=5,
        )
        square.set_transform(tr)
        ax.add_patch(square)

        # Diagonal gradient (top-left white -> bottom-right blue-gray)
        rows = cols = 256
        gx = np.linspace(0.0, 1.0, cols)
        gy = np.linspace(0.0, 1.0, rows)
        xv, yv = np.meshgrid(gx, gy)
        diag = (xv + (1 - yv)) / 2.0  # TL to BR ramp
        cmap = LinearSegmentedColormap.from_list(
            "npbs_fill", ["#ffffff", "#89A4B6"], N=256
        )
        img = ax.imshow(
            diag,
            extent=[cx - s / 2, cx + s / 2, cy - s / 2, cy + s / 2],
            origin="lower",
            cmap=cmap,
            interpolation="bicubic",
            zorder=3,
        )
        img.set_transform(tr)
        img.set_clip_path(square)

        # Diagonal line from top-left to bottom-right
        (line,) = ax.plot(
            [cx - s / 2, cx + s / 2],
            [cy + s / 2, cy - s / 2],
            color=self.edgecolor,
            lw=self.linewidth,
            zorder=4,
        )
        line.set_transform(tr)

    # Beam helpers (anchor at component center)
    def beam_contact_point(self) -> tuple[float, float]:
        return self.x, self.y

    def to_beam_point(self, point: BeamPoint) -> "NPBS":
        dx, dy = point.x - self.x, point.y - self.y
        self.x += dx
        self.y += dy
        return self


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")

    demo = NPBS(x=0.0, y=0.0, angle_deg=45.0, size=1.0)
    demo.draw(ax)

    ax.set_xlim(-2, 2)
    ax.set_ylim(-1.5, 1.5)
    fig.savefig("npbs_demo.png", dpi=200, bbox_inches="tight")
