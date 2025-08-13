from __future__ import annotations

import os

from optics_diagram import Board, Beam, Wire, Fiber
from optics_diagram.components import (
    FlatMirror,
    ConvexLens,
    ConcaveLens,
    PlanoConvexLens,
    DichroicMirror,
    NPBS,
    QWP,
    HWP,
    EOM,
    FiberCollimator,
)
import matplotlib.pyplot as plt


def build_scene() -> Board:
    board = Board(size=(10.0, 5.0))
    unit_length = 2
    beam = Beam(wavelength_nm=635)
    p1 = beam.move_to(0.0, 0.0)
    p2 = beam.line_to(unit_length, 0.0)
    p3 = beam.line_to(unit_length, unit_length)
    p4 = beam.line_to(unit_length, 2 * unit_length)
    p5 = beam.line_to(2 * unit_length, 2 * unit_length)
    p6 = beam.line_to(2 * unit_length, 3 * unit_length)

    # # Branch from p3
    branch = beam.divide(p3)
    p7 = branch.line_to(2 * unit_length, unit_length)
    p8 = branch.line_to(2 * unit_length, 0.0)
    board.add_beam(beam)

    # Components
    board.add(c1 := FiberCollimator(angle_deg=180.0).to_beam_point(p1))
    board.add(m1 := FlatMirror(angle_deg=-45.0).to_beam_point(p2))
    board.add(d1 := NPBS(angle_deg=90.0).to_beam_point(p3))
    board.add(m2 := FlatMirror(angle_deg=135.0).to_beam_point(p4))
    board.add(m3 := FlatMirror(angle_deg=-45.0).to_beam_point(p5))
    board.add(m4 := FlatMirror(angle_deg=45.0).to_beam_point(p7))
    board.add(l1 := PlanoConvexLens(angle_deg=180.0).to_beam_point(p1.divide(p2, 1, 1)))
    board.add(l2 := QWP(angle_deg=-90.0).to_beam_point(p2.divide(p3, 1, 1)))
    board.add(eom := EOM(angle_deg=-90.0).to_beam_point(p3.divide(p4, 1, 1)))
    top_contact = eom.rf_contact_top()
    wire = Wire(start=top_contact, end=(top_contact[0] + 1, top_contact[1]))
    board.add(wire)

    c1_fiber_contact = c1.fiber_contact_point()
    f = Fiber(
        start=c1_fiber_contact, end=(c1_fiber_contact[0] - 3, c1_fiber_contact[1])
    )
    f.add_pin(c1_fiber_contact[0] - 1, c1_fiber_contact[1]).add_pin(
        c1_fiber_contact[0] - 1, c1_fiber_contact[1] + 1
    ).add_pin(c1_fiber_contact[0] - 2, c1_fiber_contact[1] + 1)
    board.add(f)

    return board


if __name__ == "__main__":
    board = build_scene()
    fig, ax = board.draw()
    plt.show()
    out_path = os.path.join(os.path.dirname(__file__), "mirror_and_lenses.png")
    board.save(out_path)
    print(f"Saved demo to {out_path}")
