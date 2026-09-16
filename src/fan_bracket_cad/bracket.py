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
internal_hole_fdm_correction = 0.1  # correction for FDM printing, in mm

opening_width = 150.0        # total case cutout width (X)
opening_height = 440.0       # case cutout height (Y)

horizontal_margin = 12.0     # extra mounting strip left & right of the opening
vertical_margin = 5.0        # Extra mounting strip above & below the fan
bottom_margin = 33.0         # extra mounting strip above & below opening
top_margin = 14.0            # extra mounting strip above & below opening
case_width = 207.0

bottom_bracket_height = bottom_margin - vertical_margin

n_fans = 3
fan_size = 140.0
fan_hole_spacing = 124.5     # Noctua NF-A14x25 G2 square-frame spacing
fan_hole_dia = 4.5           # M4 clearance
fan_recess_depth = 2.0       # depth of fan frame recess into bracket

bracket_thickness = 6.0      # bracket thickness
glue_strip_thickness = 4.0   # thickness of the glue strip
vent_dia = fan_size - 10.0   # 130mm airflow opening, 5mm rim inside fan frame

case_screw_dia = 4.5
case_screw_inset_x = 5.0     # inset from bracket left/right edges
plate_corner_fillet = 3.0

# ---------------- DERIVED ----------------
bracket_height = fan_size + 2 * vertical_margin
bracket_pitch = opening_width  + 2 * horizontal_margin
bracket_width = bracket_pitch

glue_strip_width = bracket_width - 2 * horizontal_margin
glue_strip_cut_out_width = glue_strip_width + 2 * internal_hole_fdm_correction

top_case_hole_center_y = bracket_height / 2 - 3 * vertical_margin
bottom_case_hole_center_y = -bracket_height / 2 + 3 * vertical_margin



fan_hole_offsets = [
    (fan_hole_spacing / 2, fan_hole_spacing / 2),
    (fan_hole_spacing / 2, -fan_hole_spacing / 2),
    (-fan_hole_spacing / 2, fan_hole_spacing / 2),
    (-fan_hole_spacing / 2, -fan_hole_spacing / 2),
]

case_hole_offsets = [
    (bracket_width / 2 - case_screw_inset_x, top_case_hole_center_y),
    (-(bracket_width / 2 - case_screw_inset_x), top_case_hole_center_y),
    (bracket_width / 2 - case_screw_inset_x, bottom_case_hole_center_y),
    (-(bracket_width / 2 - case_screw_inset_x), bottom_case_hole_center_y),
]

def glue_strip_offset(panel_height: float) -> list[tuple[float, float]]:
    return [
        (0, panel_height / 2 - vertical_margin / 2.0),
        (0, -panel_height / 2 + vertical_margin / 2.0)
    ]

def make_bracket() -> Part:
    """One bracket: plate from Z=0 to Z=+bracket_thickness."""
    with BuildPart() as bp:
        with BuildSketch() as sk:
            Rectangle(bracket_width, bracket_height)
            fillet(sk.vertices(), radius=plate_corner_fillet)
        extrude(sk.sketch, amount=bracket_thickness)

        front_face = bp.faces().sort_by(Axis.Z)[-1]

        # glue strip
        with BuildSketch(front_face) as glue_strip_sk:
            with Locations(glue_strip_offset(bracket_height)):
                Rectangle(glue_strip_cut_out_width, vertical_margin)
                fillet(sk.vertices(), radius=plate_corner_fillet)
        extrude(glue_strip_sk.sketch, amount=-glue_strip_thickness, mode=Mode.SUBTRACT)

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

    return bp.part

def get_case_bracket_holes() -> list[tuple[float, float, float]]:
    bottom_edge_left = (-case_width / 2, -1.5 * bracket_height - bottom_bracket_height, 8.0)
    bottom_edge_right = (case_width / 2, -1.5 * bracket_height - bottom_bracket_height, 8.0)

    bottom_clip_left = (-33.0, -1.5 * bracket_height - bottom_bracket_height, 5.0)
    bottom_clip_right = (35.0, -1.5 * bracket_height - bottom_bracket_height, 5.0)

    bottom_hole_left = (-38.0, -1.5 * bracket_height - bottom_bracket_height + 19.0, 1.5)
    bottom_hole_right = (38.0, -1.5 * bracket_height - bottom_bracket_height + 19.0, 1.5)

    side_hole_1_left = (-84.0, -1.5 * bracket_height - bottom_bracket_height + 236.0, 4.5)
    side_hole_1_right = (84.0, -1.5 * bracket_height - bottom_bracket_height + 236.0, 4.5)

    side_hole_2_left = (-78.0, -1.5 * bracket_height - bottom_bracket_height + 303.0, 1.5)
    side_hole_2_right = (78.0, -1.5 * bracket_height - bottom_bracket_height + 303.0, 1.5)

    side_hole_3_left = (-78.0, -1.5 * bracket_height - bottom_bracket_height + 429.0, 1.5)
    side_hole_3_right = (78.0, -1.5 * bracket_height - bottom_bracket_height + 429.0, 1.5)

    return [
        bottom_edge_left,
        bottom_edge_right,
        bottom_clip_left,
        bottom_clip_right,
        bottom_hole_left,
        bottom_hole_right,
        side_hole_1_left,
        side_hole_1_right,
        side_hole_2_left,
        side_hole_2_right,
        side_hole_3_left,
        side_hole_3_right,
    ]

def make_glue_strip() -> Part:
    with BuildPart() as bp:
        with BuildSketch() as sk:
            Rectangle(glue_strip_width, 2 * vertical_margin)
            fillet(sk.vertices(), radius=plate_corner_fillet)
        extrude(sk.sketch, amount=glue_strip_thickness)
    return bp.part

def make_case_bottom_bracket() -> Part:
    with BuildPart() as bp:
        with BuildSketch() as sk:
            Rectangle(case_width, bottom_bracket_height)
            fillet(sk.vertices(), radius=plate_corner_fillet)
        extrude(sk.sketch, amount=bracket_thickness)

        front_face = bp.faces().sort_by(Axis.Z)[-1]

        with BuildSketch(front_face) as glue_strip_sk:
            locations = glue_strip_offset(bottom_bracket_height)
            with Locations(locations[0]):
                Rectangle(glue_strip_cut_out_width, vertical_margin)
                fillet(sk.vertices(), radius=plate_corner_fillet)
        extrude(glue_strip_sk.sketch, amount=-glue_strip_thickness, mode=Mode.SUBTRACT)
    return bp.part

def make_hole(location: tuple[float, float, float], radius: float) -> Part:
    with BuildPart() as bp:
        with BuildSketch() as sk:
            with Locations(location):
                Circle(radius + 0.5 * internal_hole_fdm_correction)
        extrude(sk.sketch, amount=bracket_thickness, mode=Mode.ADD)
    return bp.part

def make_assembly() -> list[Part]:
    bracket = make_bracket()
    parts = []

    for i in range(n_fans):
        y = -opening_height / 2 -vertical_margin + bracket_height * (i + 0.5)
        parts.append(bracket.moved(Location((0, y, 0))))

    for i in range(n_fans - 1):
        y = -opening_height / 2 - vertical_margin + bracket_height * (i + 1)
        parts.append(make_glue_strip().moved(Location((0, y, bracket_thickness - glue_strip_thickness))))

    parts.append(make_case_bottom_bracket().moved(Location((0, -1.5 * bracket_height - 0.5 * bottom_bracket_height, 0))))

    y = -1.5 * bracket_height
    parts.append(make_glue_strip().moved(Location((0, y, bracket_thickness - glue_strip_thickness))))

    #assembly = Compound(children=parts)

    # add the case bracket holes
    hole_parts = []
    hole_positions = get_case_bracket_holes()
    for h in hole_positions:
        hole_parts.append(make_hole((h[0], h[1], 0), h[2]))

    new_children = [part - hole_parts for part in parts]

    return new_children

def export_3mf_assembly(assembly: list[Part], filename: str) -> None:
    exporter = Mesher()
    for part in assembly:
        exporter.add_shape(part)

    exporter.add_code_to_metadata()
    exporter.write(filename)

def main() -> None:
    gluestrip = make_glue_strip()

    print(f"Bracket pitch: {bracket_pitch:.3f} mm")
    print(f"Bracket size: {bracket_width:.3f} x {bracket_height:.1f} mm")
    print(f"Vent dia: {vent_dia} mm, fan hole spacing: {fan_hole_spacing} mm")

    single = make_bracket()
    #print(f"Single bracket volume: {single.volume:.1f} mm^3")
    #print(f"Assembly bounding box: {assembly.bounding_box()}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    export_3mf(gluestrip, str(OUTPUT_DIR / "fan_brackets_gluestrip.3mf"))
    export_3mf(single, str(OUTPUT_DIR / "fan_bracket_single.3mf"))

    assembly = make_assembly()
    export_3mf_assembly(assembly, str(OUTPUT_DIR / "fan_brackets_assembly.3mf"))
    print(f"Exported 3MF files to {OUTPUT_DIR}")

    show(assembly)


if __name__ == "__main__":
    main()
