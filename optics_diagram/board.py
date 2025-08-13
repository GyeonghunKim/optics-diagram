from __future__ import annotations

from typing import Any, Iterable, Tuple


class Board:
    """Canvas holding components, beams, and annotations.

    Example:
        board = Board()
        board.add(component)
        board.add_beam(beam)
        board.save("diagram.png")
    """

    def __init__(self, size: Tuple[float, float] = (8.0, 6.0)) -> None:
        import matplotlib.pyplot as plt  # deferred import

        self.figure, self.ax = plt.subplots(figsize=size)
        self.components: list[Any] = []
        self.beams: list[Any] = []
        self.annotations: list[Any] = []
        self._configure_axes()

    def _configure_axes(self) -> None:
        self.ax.set_aspect("equal", adjustable="box")
        self.ax.axis("off")

    def add(self, item: Any) -> Any:
        if hasattr(item, "draw"):
            self.components.append(item)
        else:
            raise TypeError("Item must implement a draw(ax) method")
        return item

    def add_many(self, items: Iterable[Any]) -> None:
        for item in items:
            self.add(item)

    def add_beam(self, beam: Any) -> Any:
        if not hasattr(beam, "draw"):
            raise TypeError("Beam must implement a draw(ax) method")
        self.beams.append(beam)
        return beam

    def annotate(self, annotation: Any) -> Any:
        if not hasattr(annotation, "draw"):
            raise TypeError("Annotation must implement a draw(ax) method")
        self.annotations.append(annotation)
        return annotation

    def draw(self) -> tuple[Any, Any]:
        for component in self.components:
            component.draw(self.ax)
        for beam in self.beams:
            beam.draw(self.ax)
        for note in self.annotations:
            note.draw(self.ax)
        return self.figure, self.ax

    def save(
        self, output_path: str, dpi: int = 300, bbox_inches: str = "tight"
    ) -> None:
        self.draw()
        self.figure.savefig(output_path, dpi=dpi, bbox_inches=bbox_inches)
