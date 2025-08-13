from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from optics_diagram.beam import BeamPoint
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.transforms import Affine2D
from matplotlib.path import Path


@dataclass
class ConcaveLens:
    x: float = 0.0
    y: float = 0.0
    angle_deg: float = 0.0
    height: float = 1.2
    thickness: float = 0.6
    edgecolor: str = "black"
    facecolor: str = "#bfe6fb"
    linewidth: float = 2.0
    waist_factor: float = 0.45  # center width = thickness * waist_factor

    def draw(self, ax: Any) -> None:
        cx, cy = self.x, self.y
        h = self.height
        t = self.thickness
        tr = Affine2D().rotate_deg_around(cx, cy, self.angle_deg) + ax.transData

        top_y = cy + h / 2
        bot_y = cy - h / 2
        half_top = t / 2
        half_waist = (t * self.waist_factor) / 2

        # Key points
        right_top = (cx + half_top, top_y)
        right_bottom = (cx + half_top, bot_y)
        left_top = (cx - half_top, top_y)
        left_bottom = (cx - half_top, bot_y)

        # Single cubic Bezier per side (no mid cusp)
        # Controls pull inward to the waist near the center
        r_ctrl1 = (cx + half_waist, cy + h * 0.35)
        r_ctrl2 = (cx + half_waist, cy - h * 0.35)
        l_ctrl1 = (cx - half_waist, cy - h * 0.35)
        l_ctrl2 = (cx - half_waist, cy + h * 0.35)

        vertices = [
            left_top,  # M
            right_top,  # L
            r_ctrl1,  # C control1
            r_ctrl2,  # C control2
            right_bottom,  # C end
            left_bottom,  # L
            l_ctrl1,  # C control1
            l_ctrl2,  # C control2
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
        """Return the coordinate where a beam would contact the component.

        For lenses, this is the center of the component.
        """
        return self.x, self.y

    def to_beam_point(self, point: BeamPoint) -> "ConcaveLens":
        """Translate so the beam contact aligns with the given BeamPoint."""
        dx, dy = point.x - self.x, point.y - self.y
        self.x += dx
        self.y += dy
        return self


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")

    demo = ConcaveLens(x=0.0, y=0.0, angle_deg=30.0, thickness=0.6, height=1.2)
    demo.draw(ax)

    ax.set_xlim(-2, 2)
    ax.set_ylim(-1.5, 1.5)
    plt.show()
    fig.savefig("concave_lens_demo.png", dpi=200, bbox_inches="tight")
