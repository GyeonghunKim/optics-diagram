Toolkits for drawing optics diagram

## Installation

```bash
pip install -e .
```

## Quick start

```python
from optics_diagram import Board, Beam
from optics_diagram.components import FlatMirror, ConvexLens

board = Board()

beam = Beam(wavelength_nm=532).move_to(0, 0).line_to(2, 0).line_to(2, 2)
board.add_beam(beam)

board.add(FlatMirror(x=2, y=0, angle_deg=45))
board.add(ConvexLens(x=2, y=2, angle_deg=0))

board.save("example.png")
```

This will create a simple diagram and save it to `example.png`.

## Package structure

```
optics_diagram/
  __init__.py
  board.py
  beam.py
  fiber.py
  annotation.py
  arrow.py
  components/
    __init__.py
    freespace_component.py
    flat_mirror.py
    dichroic.py
    convex_lens.py
    concave_lens.py
    pbs.py
    npbs.py
    eom.py
    fiber_components.py
    fiber_bs.py
    fiber_dichroic.py
    fiber_eom.py
setup.py
```

