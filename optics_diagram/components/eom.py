from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.transforms import Affine2D
from optics_diagram.beam import BeamPoint
from math import cos, sin, radians


@dataclass
class EOM:
    x: float = 0.0
    y: float = 0.0
    angle_deg: float = 0.0
    width: float = 0.8
    height: float = 0.6
    edgecolor: str = "black"
    linewidth: float = 1.0

    def draw(self, ax: Any) -> None:
        cx, cy = self.x, self.y
        w, h = self.width, self.height
        tr = Affine2D().rotate_deg_around(cx, cy, self.angle_deg) + ax.transData

        # Top and bottom brown caps
        cap_h = h * 0.24
        for y0 in (cy + h / 2 - cap_h, cy - h / 2):
            cap = patches.Rectangle(
                (cx - w / 2, y0),
                w,
                cap_h,
                linewidth=self.linewidth,
                edgecolor=self.edgecolor,
                facecolor="#8a644a",
                zorder=4,
            )
            cap.set_transform(tr)
            ax.add_patch(cap)

        # Middle yellow-ish gradient body
        body_h = h - 2 * cap_h
        body = patches.Rectangle(
            (cx - w / 2, cy - body_h / 2),
            w,
            body_h,
            linewidth=self.linewidth,
            edgecolor=self.edgecolor,
            facecolor="none",
            zorder=3,
        )
        body.set_transform(tr)
        ax.add_patch(body)

        cols = 256
        rows = max(128, int(cols * body_h / max(w, 1e-6)))
        grad_line = np.linspace(0.0, 1.0, rows)
        gradient = np.tile(grad_line[:, None], (1, cols))
        cmap = LinearSegmentedColormap.from_list(
            "eom_body",
            [
                "#ffffff",
                "#ffff99",
                "#ffff58",
                "#ffff3e",
                "#ffff58",
                "#ffffe0",
                "#ffffff",
            ],
        )
        img = ax.imshow(
            gradient,
            extent=[cx - w / 2, cx + w / 2, cy - body_h / 2, cy + body_h / 2],
            origin="lower",
            cmap=cmap,
            interpolation="bicubic",
            zorder=2,
        )
        img.set_transform(tr)
        img.set_clip_path(body)

    # Beam helpers (anchor center)
    def beam_contact_point(self) -> tuple[float, float]:
        return self.x, self.y

    def to_beam_point(self, point: BeamPoint) -> "EOM":
        dx, dy = point.x - self.x, point.y - self.y
        self.x += dx
        self.y += dy
        return self

    # RF contact points (centers of the top and bottom caps in world coords)
    def _rotate_local(self, lx: float, ly: float) -> tuple[float, float]:
        a = radians(self.angle_deg)
        rx = lx * cos(a) - ly * sin(a)
        ry = lx * sin(a) + ly * cos(a)
        return self.x + rx, self.y + ry

    def rf_contact_top(self) -> tuple[float, float]:
        h = self.height
        cap_h = h * 0.24
        y_local = (h / 2.0) - (cap_h / 2.0)
        return self._rotate_local(0.0, y_local)

    def rf_contact_bottom(self) -> tuple[float, float]:
        h = self.height
        cap_h = h * 0.24
        y_local = -((h / 2.0) - (cap_h / 2.0))
        return self._rotate_local(0.0, y_local)

    def rf_contact_point(self) -> tuple[float, float]:
        """Primary RF contact (top)."""
        return self.rf_contact_top()


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")

    demo = EOM(x=0.0, y=0.0, angle_deg=0.0, width=1.0, height=0.6)
    demo.draw(ax)

    ax.set_xlim(-2, 2)
    ax.set_ylim(-1.5, 1.5)
    fig.savefig("eom_demo.png", dpi=200, bbox_inches="tight")
