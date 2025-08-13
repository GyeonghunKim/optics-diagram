from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional
from optics_diagram.beam import BeamPoint

import numpy as np
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.transforms import Affine2D
from math import cos, sin, radians


@dataclass
class FlatMirror:
    x: float = 0.0
    y: float = 0.0
    angle_deg: float = 0.0
    # Mirror body size (match lens-style API)
    height: float = 1.2
    thickness: float = 0.22
    # Back-compat: treat legacy length as height if provided
    length: Optional[float] = None

    frame_color: str = "black"
    edge_linewidth: float = 1.2  # thin stroke as in SVG
    border_fraction: float = 0.18  # kept for backward-compat; not used now
    right_bar_fraction: float = 0.285  # width of black bar on the right vs mirror width
    # Anchor on the mirror plane: 'center', 'left', or 'right' edge of the face
    anchor: str = "left"

    def draw(self, ax: Any) -> None:
        cx, cy = self.x, self.y
        h = self.length if self.length is not None else self.height
        t = self.thickness

        # Rotation around the mirror center
        tr = Affine2D().rotate_deg_around(cx, cy, self.angle_deg) + ax.transData

        # Mirror face rectangle (left area in the SVG)
        inner_w, inner_h = t, h

        # Create a subtle reflective gradient for the mirror face
        # Dark edges -> bright center -> dark edges
        gradient_cols = 256
        gradient_rows = max(256, int(gradient_cols * inner_h / max(inner_w, 1e-6)))
        grad_line = np.linspace(0.0, 1.0, gradient_cols, dtype=float)
        gradient = np.tile(grad_line, (gradient_rows, 1))
        # Dark blue-gray edges -> very light center for strong specular feel
        cmap = LinearSegmentedColormap.from_list(
            "mirror_reflection",
            ["#3f5864", "#f5fbff", "#3f5864"],
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

        # Add a narrow white specular highlight using per-pixel alpha
        # Construct a Gaussian-shaped alpha across width
        cols = gradient_cols
        rows = gradient_rows
        x = np.linspace(-1.0, 1.0, cols)
        sigma = 0.22  # narrower highlight
        alpha_profile = np.exp(-0.5 * (x / sigma) ** 2)
        alpha_profile = (alpha_profile - alpha_profile.min()) / (
            alpha_profile.max() - alpha_profile.min() + 1e-9
        )
        alpha_profile *= 0.55
        highlight_alpha = np.tile(alpha_profile, (rows, 1))
        white_img = np.ones((rows, cols, 3), dtype=float)
        hi = ax.imshow(
            white_img,
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

        # Solid black rectangle on the right side, aligned to the mirror edge
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
    def _anchor_local(self) -> tuple[float, float]:
        # Local coordinates with origin at face center
        inner_w = self.thickness
        if self.anchor == "left":
            return (-inner_w / 2.0, 0.0)
        if self.anchor == "right":
            return (inner_w / 2.0, 0.0)
        # default center
        return (0.0, 0.0)

    def beam_contact_point(self) -> tuple[float, float]:
        """Return the world-space anchor point on the mirror plane."""
        ax_local, ay_local = self._anchor_local()
        a = radians(self.angle_deg)
        dx = ax_local * cos(a) - ay_local * sin(a)
        dy = ax_local * sin(a) + ay_local * cos(a)
        return self.x + dx, self.y + dy

    def to_beam_point(self, point: BeamPoint) -> "FlatMirror":
        # Move so that the anchor point coincides with the given BeamPoint
        ax_w, ay_w = self.beam_contact_point()
        dx, dy = point.x - ax_w, point.y - ay_w
        self.x += dx
        self.y += dy
        return self


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")

    demo = FlatMirror(x=0.0, y=0.0, angle_deg=0.0, height=1.2, thickness=0.24)
    demo.draw(ax)

    ax.set_xlim(-2, 2)
    ax.set_ylim(-1.5, 1.5)
    plt.show()
    fig.savefig("flat_mirror_demo.png", dpi=200, bbox_inches="tight")
