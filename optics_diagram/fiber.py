from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Sequence, Tuple

import numpy as np


Point = Tuple[float, float]


def _normalize(vec: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(vec)
    if n == 0:
        return vec
    return vec / n


def _fillet_polyline(
    points: Sequence[Point], radius: float = 0.5, samples: int = 6
) -> np.ndarray:
    if len(points) < 3:
        return np.asarray(points, dtype=float)
    pts = np.asarray(points, dtype=float)
    out: List[np.ndarray] = [pts[0]]
    for i in range(1, len(pts) - 1):
        p_prev, p_curr, p_next = pts[i - 1], pts[i], pts[i + 1]
        v_in = p_curr - p_prev
        v_out = p_next - p_curr
        len_in = np.linalg.norm(v_in)
        len_out = np.linalg.norm(v_out)
        if len_in == 0 or len_out == 0:
            out.append(p_curr)
            continue
        u_in = _normalize(v_in)
        u_out = _normalize(v_out)
        cut = min(radius, 0.5 * len_in, 0.5 * len_out)
        a = p_curr - u_in * cut
        b = p_curr + u_out * cut
        if np.linalg.norm(out[-1] - a) > 1e-9:
            out.append(a)
        for t in np.linspace(0.0, 1.0, samples, endpoint=False)[1:]:
            pt = (1 - t) ** 2 * a + 2 * (1 - t) * t * p_curr + t**2 * b
            out.append(pt)
        out.append(b)
    out.append(pts[-1])
    return np.vstack(out)


@dataclass
class Fiber:
    start: Point
    end: Point
    pins: List[Point] = field(default_factory=list)
    fillet_radius: float = 0.3
    color: Tuple[float, float, float] = (1.0, 0.85, 0.0)
    linewidth: float = 2.0
    linestyle: str = "-"
    zorder: float = 0.5
    capstyle: str = "projecting"

    def add_pin(self, x: float, y: float) -> "Fiber":
        self.pins.append((x, y))
        return self

    def path_points(self) -> List[Point]:
        return [self.start, *self.pins, self.end]

    def draw(self, ax: Any) -> None:
        waypoints = self.path_points()
        if len(waypoints) < 2:
            return
        smooth = _fillet_polyline(waypoints, radius=self.fillet_radius, samples=6)
        # Offset slightly below the nominal y to route under components
        y_offset = -0.002  # small downward offset
        ys = smooth[:, 1] + y_offset
        ax.plot(
            smooth[:, 0],
            ys,
            color=self.color,
            lw=self.linewidth,
            ls=self.linestyle,
            zorder=self.zorder,
            solid_capstyle=self.capstyle,
            solid_joinstyle="round",
        )
