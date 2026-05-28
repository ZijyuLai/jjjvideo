"""
Patch manim's PDF→SVG conversion to use pdftocairo instead of dvisvgm.
dvisvgm drops PDF rules (fraction lines, fraction bars, etc.) during conversion.
pdftocairo renders them correctly.

Import this module BEFORE any manim MathTex usage:
    import scenes.patch_svg  # noqa: F401
"""
import subprocess
import shutil
from pathlib import Path
from manim.utils import tex_file_writing as _tw


def _convert_to_svg_cairo(dvi_file: Path, extension: str, page: int = 1) -> Path:
    result = dvi_file.with_suffix(".svg")
    if not result.exists():
        if shutil.which("pdftocairo"):
            subprocess.run(
                ["pdftocairo", "-svg", str(dvi_file), str(result)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        else:
            # fallback to original dvisvgm
            _tw_orig_convert(dvi_file, extension, page)
            return dvi_file.with_suffix(".svg")
    if not result.exists():
        raise ValueError(f"pdftocairo failed to convert {dvi_file} to SVG")
    return result


# store original and patch
_tw_orig_convert = _tw.convert_to_svg
_tw.convert_to_svg = _convert_to_svg_cairo
