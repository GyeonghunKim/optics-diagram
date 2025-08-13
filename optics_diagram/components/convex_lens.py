from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from optics_diagram.beam import BeamPoint
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.transforms import Affine2D
from matplotlib.path import Path


@dataclass
class ConvexLens:
    x: float = 0.0
    y: float = 0.0
    angle_deg: float = 0.0
    height: float = 1.2
    thickness: float = 0.05
    edgecolor: str = "black"
    facecolor: str = "#bfe6fb"
    linewidth: float = 2.0
    belly_factor: float = 6  # center width = thickness * belly_factor

    def draw(self, ax: Any) -> None:
        cx, cy = self.x, self.y
        h = self.height
        t = self.thickness

        tr = Affine2D().rotate_deg_around(cx, cy, self.angle_deg) + ax.transData

        top_y = cy + h / 2
        bot_y = cy - h / 2
        half_top = t / 2
        half_belly = (t * self.belly_factor) / 2

        left_top = (cx - half_top, top_y)
        right_top = (cx + half_top, top_y)
        left_bottom = (cx - half_top, bot_y)
        right_bottom = (cx + half_top, bot_y)

        # Outward bulge controls
        r_ctrl1 = (cx + half_belly, cy + h * 0.35)
        r_ctrl2 = (cx + half_belly, cy - h * 0.35)
        l_ctrl1 = (cx - half_belly, cy - h * 0.35)
        l_ctrl2 = (cx - half_belly, cy + h * 0.35)

        vertices = [
            left_top,  # M
            right_top,  # L
            r_ctrl1,  # C c1
            r_ctrl2,  # C c2
            right_bottom,  # C end
            left_bottom,  # L
            l_ctrl1,  # C c1
            l_ctrl2,  # C c2
            left_top,  # C end
            left_top,  # CLOSEPOLY anchor
        ]
        codes = [
            Path.MOVETO,
            Path.LINETO,
            Path.CURVE4,
            Path.CURVE4,
            Path.CURVE4,
            Path.LINETO,
            Path.CURVE4,
            Path.CURVE4,
            Path.CURVE4,
            Path.CLOSEPOLY,
        ]

        lens_path = Path(vertices, codes)
        lens_patch = patches.PathPatch(
            lens_path,
            facecolor=self.facecolor,
            edgecolor=self.edgecolor,
            lw=self.linewidth,
            alpha=0.6,
            joinstyle="round",
        )
        lens_patch.set_transform(tr)
        ax.add_patch(lens_patch)

    # Beam helpers
    def beam_contact_point(self) -> tuple[float, float]:
        """For lenses, the beam contact is at the component center."""
        return self.x, self.y

    def to_beam_point(self, point: BeamPoint) -> "ConvexLens":
        dx, dy = point.x - self.x, point.y - self.y
        self.x += dx
        self.y += dy
        return self


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")

    demo = ConvexLens(
        x=0.0, y=0.0, angle_deg=0.0, thickness=0.05, height=1.2, belly_factor=6
    )
    demo.draw(ax)

    ax.set_xlim(-2, 2)
    ax.set_ylim(-1.5, 1.5)
    plt.show()
    fig.savefig("convex_lens_demo.png", dpi=200, bbox_inches="tight")
