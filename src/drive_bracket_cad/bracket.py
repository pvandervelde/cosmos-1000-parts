"""
Parametric bracket set holding 2x 3.5" HDD + 2x 2.5" SSD, mounted flat
with SATA/power connectors facing the rear (-Z).

Coordinate convention (matches fan bracket):
    X - horizontal (right when facing case front)
    Y - vertical
    Z - depth; Z=0 = connector end of drives (rear), +Z toward case front

Drive orientation ("label up"):
    Label face points in +Y.
    Drive depth (connector end → far end) runs along Z: 0 → +drive_d.
    Drive width runs along X.
    Drive thickness runs along Y.

Layout (Y, bottom to top):
    [feet]
    [HDD box  – 2 HDDs stacked, lower box with feet]
    [box_gap]
    [SSD box  – 2 SSDs stacked]

Each box is an open-ended frame (open at both Z ends for airflow and connector
access).  The frame has left/right side rails, a bottom rail, a mid-rail
between the two drives, and a top rail.

HDD drives are side-mounted: screws go through the left/right side walls in
the X direction (SFF-8300 side-hole pattern).  SSD drives are bottom-mounted
through horizontal rails.

Corner feet below the HDD box have 45° chamfers on their inner edges so the
bracket can be FDM-printed without supports.
"""

from pathlib import Path

from build123d import *
from ocp_vscode import show

from cad_utils import export_3mf

OUTPUT_DIR = Path(__file__).resolve().parents[2] / "outputs"

# ── Drive dimensions (mm) ─────────────────────────────────────────────────────
# 3.5" HDD (SFF-8300), label-up orientation
hdd_w = 101.6    # X – drive width
hdd_t = 25.4     # Y – drive thickness (height when lying flat)
hdd_d = 146.05   # Z – drive depth; connector end at Z=0

# HDD side mounting holes – 6-32 UNC clearance (3.5 mm dia)
# hdd_hole_z: from connector end (same Z positions as SFF-8300 bottom holes)
# hdd_side_hole_y_offset: from drive bottom face (SFF-8300 spec)
hdd_hole_dia          = 3.5
hdd_hole_z            = [28.5, 76.5, 129.5]
hdd_side_hole_y_offset = 3.175

# 2.5" SSD (SFF-8201, 7mm slim), label-up orientation
ssd_w = 69.85    # X
ssd_t = 7.0      # Y
ssd_d = 100.45   # Z; connector end at Z=0

# SSD bottom mounting holes – M3 clearance (3.2 mm dia)
ssd_hole_dia = 3.2
ssd_hole_x   = [-28.5, 28.5]
ssd_hole_z   = [14.0, 84.0]

# ── Bracket parameters ────────────────────────────────────────────────────────
wall    = 2.5    # rail / side-wall thickness
tol     = 0.5    # clearance around drive width (each side in X)
airflow = 5.0    # vertical gap above and below each drive inside its slot
box_gap = 15.0   # vertical gap between HDD box and SSD box

ring_width = 20.0 # Width of the rings

feet_h       = 10.0   # foot pad height (Y, HDD box only)
feet_w       = 15.0   # foot pad footprint (square, X and Z)
foot_chamfer =  5.0   # chamfer size on inner foot edges (45° for printability)

# ── Derived ───────────────────────────────────────────────────────────────────
# Both boxes share the same X width (sized for the wider drive, HDD)
box_inner_width = max(hdd_w, ssd_w) + 2 * tol
box_width       = box_inner_width + 2 * wall

# Y heights per box:
#   bottom_rail(wall) + airflow + drive_t + mid_rail(wall) + drive_t + airflow + top_rail(wall)
hdd_box_height = 3 * wall + 4 * airflow + 2 * hdd_t
ssd_box_height = 3 * wall + 4 * airflow + 2 * ssd_t

# Z depth: each box matches its own drive depth (open-ended, no extra walls)
hdd_box_z = hdd_d
ssd_box_z = ssd_d

def _slot_y_centres(box_y: float, drive_t: float) -> list[float]:
    """Y centres of the lower and upper drive slots (box centred at Y=0)."""
    bot = -box_y / 2 + wall + airflow + drive_t / 2
    top =  box_y / 2 - wall - airflow - drive_t / 2
    return [bot, top]


def _rail_y_centres(box_y: float) -> list[float]:
    """Y centres of the bottom rail and mid-rail (box centred at Y=0)."""
    return [-box_y / 2 + wall / 2, 0.0]


def _add_rail_holes(
    hole_x: list[float],
    hole_z: list[float],
    hole_dia: float,
    rail_ys: list[float],
) -> None:
    """Drill clearance holes through two horizontal rails (Y-direction cylinders).

    Must be called while a BuildPart context is active.
    """
    for ry in rail_ys:
        for hx in hole_x:
            for hz in hole_z:
                with Locations((hx, ry, hz)):
                    Cylinder(
                        hole_dia / 2, wall + 2,
                        rotation=(90, 0, 0),
                        align=(Align.CENTER, Align.CENTER, Align.CENTER),
                        mode=Mode.SUBTRACT,
                    )


def _add_hdd_side_holes(slot_ys: list[float]) -> None:
    """Drill HDD side-mount clearance holes through the left/right side walls.

    Holes run in the X direction.  Y position follows SFF-8300: 3.175 mm from
    the drive bottom face.  Must be called while a BuildPart context is active.
    """
    wall_center_x = box_width / 2 - wall / 2
    for sy in slot_ys:
        hole_y = sy - hdd_t / 2 + hdd_side_hole_y_offset
        for hz in hdd_hole_z:
            for side in [1, -1]:
                with Locations((side * wall_center_x, hole_y, hz)):
                    Cylinder(
                        hdd_hole_dia / 2, wall + 2,
                        rotation=(0, 90, 0),
                        align=(Align.CENTER, Align.CENTER, Align.CENTER),
                        mode=Mode.SUBTRACT,
                    )

def make_hdd_ring(ring_x: float, ring_y: float, ring_z: float) -> None:
    """Open-ended ring for holding 2 HDDs stacked in Y, with chamfered corner feet.

    Must be called while a BuildPart context is active.
    """
    slot_ys = _slot_y_centres(hdd_box_height, hdd_t)

    with Locations((ring_x, ring_y, ring_z)):
        Box(box_width, hdd_box_height, ring_width,
            align=(Align.CENTER, Align.CENTER, Align.MIN))

    # Subtract two open-ended drive slots (open in Z at both ends)
    for cy in slot_ys:
        with Locations((ring_x, cy, ring_z)):
            Box(
                box_inner_width, hdd_t + 2 * airflow, ring_width + 2,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT,
            )

    # Side mounting holes through left/right walls
    _add_hdd_side_holes(slot_ys)

    # 2 corner feet below the HDD box
    foot_bottom_y = -hdd_box_height / 2 - feet_h / 2
    for fx in [box_width / 2 - feet_w / 2, -(box_width / 2 - feet_w / 2)]:
            with Locations((fx, foot_bottom_y, ring_z)):
                Box(feet_w, feet_h, ring_width,
                    align=(Align.CENTER, Align.CENTER, Align.MIN))

    # Chamfer the inner top edges of each foot (45° slope for FDM printability).
    # These edges sit at Y = -hdd_box_y/2 and are feet_w long — the only short
    # edges at that height, where the foot inner vertical faces meet the bracket
    # bottom plate.
    foot_top_y = -hdd_box_height / 2
    inner_foot_edges = [
        e for e in edges()
        if abs(e.center().Y - foot_top_y) < 0.1
        and abs(e.length - feet_w) < 1.0
    ]
    #if inner_foot_edges:
    #    chamfer(inner_foot_edges, foot_chamfer)

def make_hdd_spacer() -> None:
    """Spacer for stacking HDD rings in Y.

    Must be called while a BuildPart context is active.
    """

    Box(box_width, box_gap, ring_width,
        align=(Align.CENTER, Align.CENTER, Align.MIN))

def make_hdd_box() -> Part:
    """Open-ended box for holding 2 HDDs stacked in Y, without the chamfered corner feet."""
    slot_ys = _slot_y_centres(hdd_box_height, hdd_t)

    with BuildPart() as bp:
        for z_pos in hdd_hole_z:
            make_hdd_ring(0.0, 0.0, z_pos - 0.5 * ring_width)

    return bp.part

def make_ssd_box() -> Part:
    """Open-ended frame holding 2 SSDs stacked in Y, no feet."""
    slot_ys = _slot_y_centres(ssd_box_height, ssd_t)
    rail_ys = _rail_y_centres(ssd_box_height)

    with BuildPart() as bp:
        Box(box_width, ssd_box_height, ssd_box_z,
            align=(Align.CENTER, Align.CENTER, Align.MIN))

        for cy in slot_ys:
            with Locations((0, cy, ssd_box_z / 2)):
                Box(
                    box_inner_width, ssd_t + 2 * airflow, ssd_box_z + 2,
                    align=(Align.CENTER, Align.CENTER, Align.CENTER),
                    mode=Mode.SUBTRACT,
                )

        _add_rail_holes(ssd_hole_x, ssd_hole_z, ssd_hole_dia, rail_ys)

    return bp.part


def make_assembly() -> Compound:
    hdd_box = make_hdd_box()
    #ssd_box = make_ssd_box()
    # SSD box sits above HDD box with a gap between them
    #ssd_y = hdd_box_y / 2 + box_gap + ssd_box_y / 2
    return Compound(children=[hdd_box])


def main() -> None:
    hdd_part = make_hdd_box()
    #ssd_part = make_ssd_box()
    assembly = make_assembly()

    #for name, part in [("HDD box", hdd_part), ("SSD box", ssd_part), ("Assembly", assembly)]:
    #    bb = part.bounding_box()
    #    print(f"{name}: {bb.size.X:.1f} x {bb.size.Y:.1f} x {bb.size.Z:.1f} mm")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    export_3mf(hdd_part, str(OUTPUT_DIR / "drive_bracket_hdd.3mf"))
    #export_3mf(ssd_part, str(OUTPUT_DIR / "drive_bracket_ssd.3mf"))
    #export_3mf(assembly, str(OUTPUT_DIR / "drive_bracket_assembly.3mf"))
    print(f"Exported 3MF files to {OUTPUT_DIR}")
    show(assembly)


if __name__ == "__main__":
    main()
