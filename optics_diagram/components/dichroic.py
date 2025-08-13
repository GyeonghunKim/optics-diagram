from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional
from optics_diagram.beam import BeamPoint

import numpy as np
import matplotlib.patches as patches
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.transforms import Affine2D


@dataclass
class DichroicMirror:
    x: float = 0.0
    y: float = 0.0
    angle_deg: float = 0.0
    height: float = 1.2
    thickness: float = 0.22
    length: Optional[float] = None

    frame_color: str = "black"
    edge_linewidth: float = 1.2
    right_bar_fraction: float = 0.285  # 2.835 / 9.921 from the SVG

    def draw(self, ax: Any) -> None:
        cx, cy = self.x, self.y
        h = self.length if self.length is not None else self.height
        t = self.thickness

        tr = Affine2D().rotate_deg_around(cx, cy, self.angle_deg) + ax.transData

        # Mirror face rectangle (green dichroic look)
        inner_w, inner_h = t, h

        # Vertical gradient: green edges to white center to green
        gradient_cols = 256
        gradient_rows = max(256, int(gradient_cols * inner_h / max(inner_w, 1e-6)))
        grad_line = np.linspace(0.0, 1.0, gradient_cols, dtype=float)
        gradient = np.tile(grad_line, (gradient_rows, 1))
        # Stronger green tint for clearer distinction from regular mirrors
        cmap = LinearSegmentedColormap.from_list(
            "dichroic_green",
            ["#2fab3a", "#d9ffd0", "#2fab3a"],
        )

        img = ax.imshow(
            gradient,
            extent=[
                cx - inner_w / 2,
                cx + inner_w / 2,
                cy - inner_h / 2,
                cy + inner_h / 2,
            ],
            origin="lower",
            cmap=cmap,
            interpolation="bicubic",
            alpha=1.0,
            zorder=3,
        )
        img.set_transform(tr)

        # Lightweight highlight in the center to emphasize coating
        cols = gradient_cols
        rows = gradient_rows
        x = np.linspace(-1.0, 1.0, cols)
        sigma = 0.27
        alpha_profile = np.exp(-0.5 * (x / sigma) ** 2)
        alpha_profile = (alpha_profile - alpha_profile.min()) / (
            alpha_profile.max() - alpha_profile.min() + 1e-9
        )
        alpha_profile *= 0.25
        highlight_alpha = np.tile(alpha_profile, (rows, 1))
        # Light-green highlight instead of pure white to keep the green feel
        green_img = np.ones((rows, cols, 3), dtype=float)
        green_img[..., 0] *= 0.85
        green_img[..., 1] *= 1.00
        green_img[..., 2] *= 0.85
        hi = ax.imshow(
            green_img,
            extent=[
                cx - inner_w / 2,
                cx + inner_w / 2,
                cy - inner_h / 2,
                cy + inner_h / 2,
            ],
            origin="lower",
            interpolation="bicubic",
            alpha=highlight_alpha,
            zorder=4,
        )
        hi.set_transform(tr)

        # Thin black stroke around the mirror face
        face_border = patches.Rectangle(
            (cx - inner_w / 2, cy - inner_h / 2),
            inner_w,
            inner_h,
            linewidth=self.edge_linewidth,
            edgecolor=self.frame_color,
            facecolor="none",
            zorder=5,
        )
        face_border.set_transform(tr)
        ax.add_patch(face_border)

        # Solid black rectangle on the right side (bar), SVG proportion
        right_bar_w = inner_w * self.right_bar_fraction
        right_bar = patches.Rectangle(
            (cx + inner_w / 2 - right_bar_w, cy - inner_h / 2),
            right_bar_w,
            inner_h,
            linewidth=self.edge_linewidth,
            edgecolor=self.frame_color,
            facecolor=self.frame_color,
            zorder=6,
        )
        right_bar.set_transform(tr)
        ax.add_patch(right_bar)

    # Beam helpers
    def beam_contact_point(self) -> tuple[float, float]:
        """For dichroic (plate), use the component center as contact point."""
        return self.x, self.y

    def to_beam_point(self, point: BeamPoint) -> "DichroicMirror":
        dx, dy = point.x - self.x, point.y - self.y
        self.x += dx
        self.y += dy
        return self


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")

    demo = DichroicMirror(x=0.0, y=0.0, angle_deg=0.0, height=1.2, thickness=0.24)
    demo.draw(ax)

    ax.set_xlim(-2, 2)
    ax.set_ylim(-1.5, 1.5)
    plt.show()
    fig.savefig("dichroic_mirror_demo.png", dpi=200, bbox_inches="tight")
