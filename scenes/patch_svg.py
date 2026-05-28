"""
Patch manim's PDF→SVG conversion to preserve fraction lines.

Problem: dvisvgm renders fraction bars as stroke-only <path> elements,
but manim's SVG parser only processes filled paths, dropping the bars.

Fix: After dvisvgm generates the SVG, convert stroke-only paths to
filled rectangles so manim renders them correctly.

Import this module BEFORE any manim MathTex usage:
    import scenes.patch_svg  # noqa: F401
"""
import re
import subprocess
import shutil
from pathlib import Path
from manim.utils import tex_file_writing as _tw


def _convert_stroke_to_fill(svg_text: str) -> str:
    """Convert stroke-only horizontal paths to filled thin rectangles."""
    # Match any <path ... /> element
    path_re = re.compile(r'<path\b([^>]*)/>', re.DOTALL)

    def _replace(match):
        attrs = match.group(1)
        # Must have stroke and fill="none"
        if 'stroke' not in attrs:
            return match.group(0)
        if "fill='none'" not in attrs and 'fill="none"' not in attrs:
            return match.group(0)
        # Extract d attribute (single or double quotes)
        d_match = re.search(r"""d=['"]([^'"]*)['"]""", attrs)
        if not d_match:
            return match.group(0)
        d = d_match.group(1)
        # Check if it's a simple horizontal line: M x1 y H x2
        h_match = re.match(r'\s*M\s*([\d.]+)\s+([\d.-]+)\s*H\s*([\d.]+)\s*$', d)
        if not h_match:
            return match.group(0)
        x1, y, x2 = float(h_match.group(1)), float(h_match.group(2)), float(h_match.group(3))
        if x2 < x1:
            x1, x2 = x2, x1
        h = 0.04  # thin bar height
        new_d = f'M{x1} {y}H{x2}V{y + h}H{x1}Z'
        # Strip original d, stroke attrs, replace fill="none" with fill
        new_attrs = re.sub(r"""d=['"][^'"]*['"]""", '', attrs)
        new_attrs = re.sub(r"stroke-width='[^']*'", '', new_attrs)
        new_attrs = re.sub(r'stroke-width="[^"]*"', '', new_attrs)
        new_attrs = re.sub(r"stroke='[^']*'", '', new_attrs)
        new_attrs = re.sub(r'stroke="[^"]*"', '', new_attrs)
        new_attrs = re.sub(r"stroke-\w+='[^']*'", '', new_attrs)
        new_attrs = re.sub(r'stroke-\w+="[^"]*"', '', new_attrs)
        new_attrs = re.sub(r"stroke-miterlimit='[^']*'", '', new_attrs)
        new_attrs = re.sub(r'stroke-miterlimit="[^"]*"', '', new_attrs)
        new_attrs = new_attrs.replace("fill='none'", "fill='#e0e0e0'")
        new_attrs = new_attrs.replace('fill="none"', 'fill="#e0e0e0"')
        if 'fill=' not in new_attrs and "fill=" not in new_attrs:
            new_attrs += " fill='#e0e0e0'"
        return f'<path{new_attrs} d="{new_d}"/>'

    return path_re.sub(_replace, svg_text)


def _convert_to_svg_patched(dvi_file: Path, extension: str, page: int = 1) -> Path:
    result = dvi_file.with_suffix(".svg")
    if not result.exists():
        # Run original dvisvgm conversion
        command = [
            "dvisvgm",
            *(["--pdf"] if extension == ".pdf" else []),
            f"--page={page}",
            "--no-fonts",
            "--verbosity=0",
            f"--output={result.as_posix()}",
            f"{dvi_file.as_posix()}",
        ]
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if not result.exists():
        raise ValueError(f"dvisvgm failed to convert {dvi_file}")
    # Post-process: convert stroke-only fraction lines to filled paths
    try:
        svg_text = result.read_text(encoding="utf-8")
        patched = _convert_stroke_to_fill(svg_text)
        if patched != svg_text:
            result.write_text(patched, encoding="utf-8")
    except Exception:
        pass  # fallback: use original SVG
    return result


# Store original and apply patch
_tw_orig = _tw.convert_to_svg
_tw.convert_to_svg = _convert_to_svg_patched
