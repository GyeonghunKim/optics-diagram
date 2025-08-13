from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Sequence, Tuple, Optional


def wavelength_to_rgb(wavelength_nm: float) -> Tuple[float, float, float]:
    """Approximate conversion from wavelength in nm to an RGB tuple (0-1).

    Range clamped to ~380-780 nm.
    Implementation adapted from common public-domain approximations.
    """
    w = max(380.0, min(780.0, float(wavelength_nm)))

    if 380.0 <= w < 440.0:
        r, g, b = -(w - 440.0) / (440.0 - 380.0), 0.0, 1.0
    elif 440.0 <= w < 490.0:
        r, g, b = 0.0, (w - 440.0) / (490.0 - 440.0), 1.0
    elif 490.0 <= w < 510.0:
        r, g, b = 0.0, 1.0, -(w - 510.0) / (510.0 - 490.0)
    elif 510.0 <= w < 580.0:
        r, g, b = (w - 510.0) / (580.0 - 510.0), 1.0, 0.0
    elif 580.0 <= w < 645.0:
        r, g, b = 1.0, -(w - 645.0) / (645.0 - 580.0), 0.0
    else:
        r, g, b = 1.0, 0.0, 0.0

    # Intensity adjustment near vision limits
    if 380.0 <= w < 420.0:
        factor = 0.3 + 0.7 * (w - 380.0) / (420.0 - 380.0)
    elif 420.0 <= w < 700.0:
        factor = 1.0
    else:
        factor = 0.3 + 0.7 * (780.0 - w) / (780.0 - 700.0)

    return (
        max(0.0, min(1.0, r * factor)),
        max(0.0, min(1.0, g * factor)),
        max(0.0, min(1.0, b * factor)),
    )


Point = Tuple[float, float]


@dataclass
class BeamPoint:
    x: float
    y: float
    parents: List["BeamPoint"] = field(default_factory=list)
    children: List["BeamPoint"] = field(default_factory=list)

    def divide(self, other: "BeamPoint", m: float, n: float) -> "BeamPoint":
        """Return the section point dividing self→other in the ratio m:n.

        Uses the signed section formula. For internal division, m and n are
        positive. If one of m or n is negative, it yields an external division
        point (outside the segment) on the corresponding side, e.g.
        self.divide(other, -1, 2) is outside near `self`.
        """
        denom = m + n
        if abs(denom) < 1e-12:
            raise ValueError("Undefined division: m + n must not be zero")
        x = (n * self.x + m * other.x) / denom
        y = (n * self.y + m * other.y) / denom
        return BeamPoint(x, y)


@dataclass
class Beam:
    """Beam represented as a directed graph of BeamPoint nodes.

    Use `move_to` to create a start node, `line_to` to create edges and
    subsequent nodes, and `divide` to create a branch view starting from
    any existing node.
    """

    # Style
    wavelength_nm: float = 780.0
    color: Tuple[float, float, float] | None = None
    linewidth: float = 2.0
    show_arrow: bool = True
    zorder: float = 100.0

    # Graph storage (shared between branches)
    _nodes: List[BeamPoint] = field(default_factory=list, init=False, repr=False)
    _edges: List[Tuple[BeamPoint, BeamPoint]] = field(
        default_factory=list, init=False, repr=False
    )
    _roots: List[BeamPoint] = field(default_factory=list, init=False, repr=False)
    _current: Optional[BeamPoint] = field(default=None, init=False, repr=False)

    def _add_node(self, x: float, y: float) -> BeamPoint:
        node = BeamPoint(x, y)
        self._nodes.append(node)
        return node

    def _add_edge(self, a: BeamPoint, b: BeamPoint) -> None:
        a.children.append(b)
        b.parents.append(a)
        self._edges.append((a, b))

    def move_to(self, x: float, y: float) -> BeamPoint:
        start = self._add_node(x, y)
        self._roots.append(start)
        self._current = start
        return start

    def line_to(
        self, x: float, y: float, from_point: Optional[BeamPoint] = None
    ) -> BeamPoint:
        if from_point is None:
            if self._current is None:
                raise ValueError(
                    "Call move_to before line_to to define the starting point"
                )
            from_point = self._current
        newp = self._add_node(x, y)
        self._add_edge(from_point, newp)
        self._current = newp
        return newp

    def extend(
        self, pts: Sequence[Point], from_point: Optional[BeamPoint] = None
    ) -> List[BeamPoint]:
        """Extend the beam with a sequence of points, returning the created nodes."""
        created: List[BeamPoint] = []
        start = from_point or self._current
        if start is None and pts:
            start = self.move_to(*pts[0])
            pts = pts[1:]
            created.append(start)
        if start is None:
            return created
        last = start
        for x, y in pts:
            last = self.line_to(x, y, from_point=last)
            created.append(last)
        return created

    def divide(self, at: BeamPoint) -> "Beam":
        """Create a branch view of this beam graph starting at `at`.

        The returned object shares the same underlying nodes/edges and style,
        but has its own current pointer, enabling chained `line_to` calls from
        `at` without affecting this object's current pointer.
        """
        branch = Beam(
            wavelength_nm=self.wavelength_nm,
            color=self.color,
            linewidth=self.linewidth,
            show_arrow=self.show_arrow,
        )
        # Share the storage by reference
        branch._nodes = self._nodes
        branch._edges = self._edges
        branch._roots = self._roots
        branch._current = at
        return branch

    def _color(self) -> Tuple[float, float, float]:
        return (
            self.color
            if self.color is not None
            else wavelength_to_rgb(self.wavelength_nm)
        )

    def draw(self, ax: Any) -> None:
        if not self._edges:
            return
        c = self._color()
        # Draw all segments
        for a, b in self._edges:
            ax.plot(
                [a.x, b.x],
                [a.y, b.y],
                color=c,
                lw=self.linewidth,
                zorder=self.zorder,
            )
        # Draw arrows at leaves
        if self.show_arrow:
            leaves = [
                n for n in self._nodes if len(n.children) == 0 and len(n.parents) > 0
            ]
            for leaf in leaves:
                for parent in leaf.parents:
                    ax.annotate(
                        "",
                        xy=(leaf.x, leaf.y),
                        xytext=(parent.x, parent.y),
                        arrowprops=dict(arrowstyle="->", color=c, lw=self.linewidth),
                        zorder=self.zorder,
                    )
