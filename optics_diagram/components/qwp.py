from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.transforms import Affine2D

from optics_diagram.beam import BeamPoint


@dataclass
class QWP:
    x: float = 0.0
    y: float = 0.0
    angle_deg: float = 0.0
    height: float = 1.2
    thickness: float = 0.18
    edgecolor: str = "black"
    linewidth: float = 1.0

    def draw(self, ax: Any) -> None:
        cx, cy = self.x, self.y
        h = self.height
        t = self.thickness

        tr = Affine2D().rotate_deg_around(cx, cy, self.angle_deg) + ax.transData

        border = patches.Rectangle(
            (cx - t / 2, cy - h / 2),
            t,
            h,
            linewidth=self.linewidth,
            edgecolor=self.edgecolor,
            facecolor="none",
            zorder=3,
        )
        border.set_transform(tr)
        ax.add_patch(border)

        rows = max(256, int(256 * h / max(t, 1e-6)))
        cols = 256
        grad_line = np.linspace(0.0, 1.0, cols)
        gradient = np.tile(grad_line, (rows, 1))
        # Strong green to indicate quarter-wave plate
        cmap = LinearSegmentedColormap.from_list(
            "qwp_fill", ["#2fab3a", "#e7ffdc", "#2fab3a"], N=256
        )
        img = ax.imshow(
            gradient,
            extent=[cx - t / 2, cx + t / 2, cy - h / 2, cy + h / 2],
            origin="lower",
            cmap=cmap,
            interpolation="bicubic",
            zorder=2,
        )
        img.set_transform(tr)
        img.set_clip_path(border)

    # Beam helpers (anchor center)
    def beam_contact_point(self) -> tuple[float, float]:
        return self.x, self.y

    def to_beam_point(self, point: BeamPoint) -> "QWP":
        dx, dy = point.x - self.x, point.y - self.y
        self.x += dx
        self.y += dy
        return self
