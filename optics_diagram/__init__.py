"""optics_diagram

Lightweight utilities to draw optical setups using Matplotlib.

This package provides a simple scene graph: a `Board` hosting
free-space `components`, `Beam` and `Fiber` routes, and helpers
like `Annotation` and `Arrow`.
"""

from .board import Board
from .beam import Beam
from .fiber import Fiber
from .annotation import Annotation
from .arrow import Arrow
from .wire import Wire
from . import components as components

__all__ = [
    "Board",
    "Beam",
    "Fiber",
    "Annotation",
    "Arrow",
    "Wire",
    "components",
]
