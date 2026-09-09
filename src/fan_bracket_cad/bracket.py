"""
Parametric 140mm x3 fan bracket for a case front panel cutout.

Coordinate convention:
    X - across the 150mm opening (horizontal), pointing to the right when looking at the case front.
    Y - vertical across the 440mm cutout (vertical)
    Z - depth. Z=0 is the OUTER (front) face of the case panel.
        +Z points OUT of the case (toward the viewer).
        -Z points INTO the case interior.

Design assumptions (stated explicitly so they're easy to change):
    - The bracket is a thin plate that sits proud of the panel's front
      face, screwed to the case through the 10mm top/bottom margins
      (from the front). Its thickness is capped at 8mm ("front side height").
    - The fan bolts to the BACK face of this plate (at Z=0, the panel's
      front face) and hangs backward into the case (-Z), so it never
      pokes past the front (Z=0) and the bracket itself never exceeds +8mm.
    - Fan mounting pattern: 124.5 x 124.5mm, M4 clearance holes (4.5mm).
    - A circular vent opening lets air pass through the plate, sized
      5mm smaller radius than the fan frame to leave a mounting rim.
    - Case-attachment holes are placed in the middle of each 10mm
      margin strip, inset 15mm from the bracket's left/right edges.
    - 3 brackets are equally spaced across the 440mm opening, each
      bracket "owning" a 440/3 = 146.667mm wide slice, fan centered in it.

Adjust the PARAMETERS block and re-run.
"""

from pathlib import Path

from build123d import *
from ocp_vscode import show

from cad_utils import export_3mf

# Repo-relative output dir - works the same on Windows and Linux
OUTPUT_DIR = Path(__file__).resolve().parents[2] / "outputs"

# ---------------- PARAMETERS ----------------
opening_width = 150.0        # total case cutout width (X)
opening_height = 440.0       # case cutout height (Y)
margin = 10.0                # extra mounting strip above & below opening
n_fans = 3

fan_size = 140.0
fan_hole_spacing = 124.5     # Noctua NF-A14x25 G2 square-frame spacing
fan_hole_dia = 4.5           # M4 clearance
fan_recess_depth = 2.0       # depth of fan frame recess into bracket

bracket_thickness = 6.0      # bracket thickness
vent_dia = fan_size - 10.0   # 130mm airflow opening, 5mm rim inside fan frame

case_screw_dia = 4.5
case_screw_inset_x = 5.0     # inset from bracket left/right edges
plate_corner_fillet = 3.0

# ---------------- DERIVED ----------------
bracket_height = opening_height / n_fans
bracket_pitch = opening_width  + 2 * margin
bracket_width = bracket_pitch

top_margin_y = bracket_height / 2 - margin / 2
bottom_margin_y = -bracket_height / 2 + margin / 2

fan_hole_offsets = [
    (fan_hole_spacing / 2, fan_hole_spacing / 2),
    (fan_hole_spacing / 2, -fan_hole_spacing / 2),
    (-fan_hole_spacing / 2, fan_hole_spacing / 2),
    (-fan_hole_spacing / 2, -fan_hole_spacing / 2),
]

case_hole_offsets = [
    (bracket_width / 2 - case_screw_inset_x, top_margin_y),
    (-(bracket_width / 2 - case_screw_inset_x), top_margin_y),
    (bracket_width / 2 - case_screw_inset_x, bottom_margin_y),
    (-(bracket_width / 2 - case_screw_inset_x), bottom_margin_y),
]


def make_bracket() -> Part:
    """One bracket: plate from Z=0 to Z=+bracket_thickness."""
    with BuildPart() as bp:
        with BuildSketch() as sk:
            Rectangle(bracket_width, bracket_height)
            fillet(sk.vertices(), radius=plate_corner_fillet)
        extrude(sk.sketch, amount=bracket_thickness)

        front_face = bp.faces().sort_by(Axis.Z)[-1]

        # fan recess (shallow pocket)
        with BuildSketch(front_face) as fan_recess_sk:
            Rectangle(fan_size, fan_size)
            fillet(fan_recess_sk.vertices(), radius=plate_corner_fillet)
        extrude(fan_recess_sk.sketch, amount=-fan_recess_depth, mode=Mode.SUBTRACT)

        # Airflow vent (through hole)
        with BuildSketch(front_face) as vent_sk:
            Circle(vent_dia / 2)
        extrude(vent_sk.sketch, amount=-bracket_thickness, mode=Mode.SUBTRACT)

        # Fan mounting holes
        with BuildSketch(front_face) as fan_holes_sk:
            with Locations(fan_hole_offsets):
                Circle(fan_hole_dia / 2)
        extrude(fan_holes_sk.sketch, amount=-bracket_thickness, mode=Mode.SUBTRACT)

        # Case attachment holes (through the top/bottom margin strips)
        with BuildSketch(front_face) as case_holes_sk:
            with Locations(case_hole_offsets):
                Circle(case_screw_dia / 2)
        extrude(case_holes_sk.sketch, amount=-bracket_thickness, mode=Mode.SUBTRACT)

    return bp.part


def make_assembly() -> Compound:
    bracket = make_bracket()
    parts = []
    for i in range(n_fans):
        y = -opening_width / 2 + bracket_pitch * (i + 0.5)
        parts.append(bracket.moved(Location((0, y, 0))))
    return Compound(children=parts)


def main() -> None:
    assembly = make_assembly()

    print(f"Bracket pitch: {bracket_pitch:.3f} mm")
    print(f"Bracket size: {bracket_width:.3f} x {bracket_height:.1f} mm")
    print(f"Vent dia: {vent_dia} mm, fan hole spacing: {fan_hole_spacing} mm")

    single = make_bracket()
    print(f"Single bracket volume: {single.volume:.1f} mm^3")
    print(f"Assembly bounding box: {assembly.bounding_box()}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    export_3mf(assembly, str(OUTPUT_DIR / "fan_brackets_assembly.3mf"))
    export_3mf(single, str(OUTPUT_DIR / "fan_bracket_single.3mf"))
    print(f"Exported 3MF files to {OUTPUT_DIR}")
    show(assembly)


if __name__ == "__main__":
    main()
