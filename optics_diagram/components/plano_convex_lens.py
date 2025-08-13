from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from optics_diagram.beam import BeamPoint
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.transforms import Affine2D
from matplotlib.path import Path


@dataclass
class PlanoConvexLens:
    x: float = 0.0
    y: float = 0.0
    angle_deg: float = 0.0
    height: float = 1.2
    thickness: float = 0.05
    edgecolor: str = "black"
    facecolor: str = "#bfe6fb"
    linewidth: float = 1.0
    belly_factor: float = 12  # center width on convex side relative to thickness

    def draw(self, ax: Any) -> None:
        cx, cy = self.x, self.y
        h = self.height
        t = self.thickness

        tr = Affine2D().rotate_deg_around(cx, cy, self.angle_deg) + ax.transData

        top_y = cy + h / 2
        bot_y = cy - h / 2
        half_top = t / 2
        half_belly = (t * self.belly_factor) / 2

        # Always flat on the left; users can rotate 180° if needed
        left_top = (cx - half_top, top_y)
        right_top = (cx + half_top, top_y)
        left_bottom = (cx - half_top, bot_y)
        right_bottom = (cx + half_top, bot_y)

        # Convex bulge on the right side
        c1 = (cx + half_belly, cy + h * 0.35)
        c2 = (cx + half_belly, cy - h * 0.35)

        vertices = [
            left_top,  # M (flat side top)
            right_top,  # L (top edge)
            c1,  # C control 1 (convex)
            c2,  # C control 2 (convex)
            right_bottom,  # C end at bottom-right
            left_bottom,  # L bottom edge back to flat side
            left_top,  # L up the flat side
            left_top,  # CLOSEPOLY anchor
        ]
        codes = [
            Path.MOVETO,
            Path.LINETO,
            Path.CURVE4,
            Path.CURVE4,
            Path.CURVE4,
            Path.LINETO,
            Path.LINETO,
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
        """For lenses, the beam contact is the component center."""
        return self.x, self.y

    def to_beam_point(self, point: BeamPoint) -> "PlanoConvexLens":
        dx, dy = point.x - self.x, point.y - self.y
        self.x += dx
        self.y += dy
        return self


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")

    demo = PlanoConvexLens(
        x=0.0,
        y=0.0,
        angle_deg=0.0,
        thickness=0.05,
        height=1.2,
        belly_factor=12,
    )
    demo.draw(ax)

    ax.set_xlim(-2, 2)
    ax.set_ylim(-1.5, 1.5)
    plt.show()
    fig.savefig("plano_convex_lens_demo.png", dpi=200, bbox_inches="tight")
