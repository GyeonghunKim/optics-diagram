from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.transforms import Affine2D
from optics_diagram.beam import BeamPoint
from math import cos, sin, radians


@dataclass
class FiberCollimator:
    x: float = 0.0
    y: float = 0.0
    width: float = 1.0  # longer body
    height: float = 0.45
    edgecolor: str = "black"
    linewidth: float = 1.0
    angle_deg: float = 0.0

    def draw(self, ax: Any) -> None:
        cx, cy = self.x, self.y
        w, h = self.width, self.height
        tr = Affine2D().rotate_deg_around(cx, cy, self.angle_deg) + ax.transData

        # Map proportions from the SVG: total width 23.428, block width 5.668
        total_w_ref = 23.427979
        block_w_ref = 5.6680002
        block_w = w * (block_w_ref / total_w_ref)

        # Grayscale metallic gradient helper
        def draw_grad_rect(
            x0: float,
            y0: float,
            rw: float,
            rh: float,
            cmap: LinearSegmentedColormap,
            z: int,
        ) -> None:
            rows = max(128, int(256 * rh / max(rw, 1e-6)))
            cols = 256
            gy = np.linspace(0.0, 1.0, rows)
            gradient = np.tile(gy[:, None], (1, cols))
            rect = patches.Rectangle(
                (x0, y0),
                rw,
                rh,
                linewidth=self.linewidth,
                edgecolor=self.edgecolor,
                facecolor="none",
                zorder=z,
            )
            rect.set_transform(tr)
            ax.add_patch(rect)
            img = ax.imshow(
                gradient,
                extent=[x0, x0 + rw, y0, y0 + rh],
                origin="lower",
                cmap=cmap,
                interpolation="bicubic",
                zorder=z - 1,
            )
            img.set_transform(tr)
            img.set_clip_path(rect)

        metal_cmap_tall = LinearSegmentedColormap.from_list(
            "metal_tall",
            [
                "#ffffff",
                "#c4c4c4",
                "#5c5c5c",
                "#1a1a1a",
                "#000000",
                "#4c4c4c",
                "#a2a2a2",
                "#ffffff",
            ],
        )

        # Left rectangle (wider and longer)
        gap = 0.0  # ensure no gaps between rectangles
        left_w = block_w * 1.20
        left_h = h * 1.30
        left_x = cx - w / 2
        draw_grad_rect(left_x, cy - left_h / 2, left_w, left_h, metal_cmap_tall, z=5)

        # Center rectangle (slightly wider than left, and 1.3x longer than left)
        center_w = left_w * 1.50
        center_h = h * 1.10
        center_x = left_x + left_w + gap
        draw_grad_rect(
            center_x, cy - center_h / 2, center_w, center_h, metal_cmap_tall, z=5
        )

        # Right rectangle (bit shorter)
        right_w = block_w * 0.7
        right_h = h * 0.25
        right_x = center_x + center_w + gap
        draw_grad_rect(
            right_x, cy - right_h / 2, right_w, right_h, metal_cmap_tall, z=6
        )

        # Remaining body intentionally left blank per request (no blue slats)

    # Contacts: left = beam (free-space), right = fiber
    def _rotate_local(self, lx: float, ly: float) -> tuple[float, float]:
        a = radians(self.angle_deg)
        rx = lx * cos(a) - ly * sin(a)
        ry = lx * sin(a) + ly * cos(a)
        return self.x + rx, self.y + ry

    def beam_contact_point(self) -> tuple[float, float]:
        # Left end of the body
        return self._rotate_local(-self.width / 2.0, 0.0)

    def fiber_contact_point(self) -> tuple[float, float]:
        # Slightly inside at the LEFT edge of the center rectangle
        # Recompute layout proportions to mirror draw()
        total_w_ref = 23.427979
        block_w_ref = 5.6680002
        block_w = self.width * (block_w_ref / total_w_ref)

        left_w = block_w * 1.20
        center_w = left_w * 1.50  # not used for position, only for clarity
        gap = 0.0

        # Local coordinates along x with origin at component center
        left_x_local = -self.width / 2.0
        center_left_x_local = (
            left_x_local + 2.5 * left_w + gap
        )  # LEFT edge of center rect

        # Nudge a tiny bit to the right (inside the center rectangle)
        nudge = min(self.width, self.height) * 0.003
        return self._rotate_local(center_left_x_local + nudge, 0.0)

    def to_beam_point(self, point: BeamPoint) -> "FiberCollimator":
        # Move so left end coincides with given BeamPoint
        bx, by = self.beam_contact_point()
        dx, dy = point.x - bx, point.y - by
        self.x += dx
        self.y += dy
        return self

    def to_fiber_point(self, point: BeamPoint) -> "FiberCollimator":
        # Move so right end coincides with given BeamPoint
        fx, fy = self.fiber_contact_point()
        dx, dy = point.x - fx, point.y - fy
        self.x += dx
        self.y += dy
        return self


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")

    demo = FiberCollimator(angle_deg=45.0)
    demo.draw(ax)
    ax.set_xlim(-2, 2)
    ax.set_ylim(-2, 2)
    plt.show()
    fig.tight_layout()
    fig.set_size_inches(10, 10)
    fig.savefig("fiber_collimator_demo.png", dpi=200, bbox_inches="tight")
