"""
Combined display: fan brackets + drive brackets in a single OCP viewport.

Coordinate system (fan-bracket convention):
    X  – horizontal, right when facing the case front
    Y  – vertical
    Z  – depth; Z=0 is the outer (front) face of the case panel,
         +Z points toward the viewer, –Z points into the case interior.

Positioning:
    Fan brackets  – natural position, bracket plate from Z=0 to Z=+bracket_thickness.
    Drive brackets – their front-facing end placed 50 mm behind the fan bracket
                     back face (Z=0), so at Z=–50 mm.  Because drive-bracket Z=0
                     is the connector (rear) end and Z=+hdd_d is the front-facing
                     end, the drive assembly is shifted by –(50 + hdd_d) in Z.
"""

from build123d import Compound, Location
from ocp_vscode import show

import fan_bracket_cad.bracket as fb
import drive_bracket_cad.bracket as db


FAN_DRIVE_GAP = 50.0   # mm gap between fan bracket back face and drive bracket front face


def make_combined() -> Compound:
    fan_assembly = fb.make_assembly()

    drive_assembly = db.make_assembly()
    drive_z_offset = -(FAN_DRIVE_GAP + db.hdd_d)
    drive_assembly = drive_assembly.moved(Location((0, 0, drive_z_offset)))

    return Compound(children=[fan_assembly, drive_assembly])


if __name__ == "__main__":
    combined = make_combined()
    print(f"Fan bracket thickness : {fb.bracket_thickness} mm")
    print(f"Drive bracket gap from panel: {FAN_DRIVE_GAP} mm")
    print(f"Drive assembly Z offset: {-(FAN_DRIVE_GAP + db.hdd_d):.2f} mm")
    print(f"Combined bounding box : {combined.bounding_box()}")
    show(combined)
