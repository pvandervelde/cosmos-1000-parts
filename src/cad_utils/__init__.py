import os
import tempfile

from build123d import Lib3MF, export_stl
from build123d import Compound, Part


def export_3mf(shape: Part | Compound, file_path: str) -> None:
    """Export a build123d shape to 3MF via an intermediate STL tessellation."""
    with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as f:
        stl_path = f.name
    try:
        export_stl(shape, stl_path)
        wrapper = Lib3MF.Wrapper()
        model = wrapper.CreateModel()
        model.QueryReader("stl").ReadFromFile(stl_path)
        model.QueryWriter("3mf").WriteToFile(file_path)
    finally:
        os.unlink(stl_path)
