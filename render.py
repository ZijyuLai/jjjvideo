#!/usr/bin/env python3
"""
CLI tool to render Manim scenes to video.
Usage: python render.py [--scene SCENE_NAME] [--quality low|medium|high]
"""
import argparse
import subprocess
import sys
import os

SCENES = {
    "doppler": ("scenes/doppler_radar.py", "DopplerRadarScene"),
    "doppler_formula": ("scenes/doppler_radar.py", "DopplerFormulaShowcase"),
}

QUALITY_FLAGS = {
    "low": "-ql",       # 480p, 15fps
    "medium": "-qm",    # 720p, 30fps
    "high": "-qh",      # 1080p, 60fps
    "4k": "-qk",        # 2160p, 60fps
}


def render(scene_name: str, quality: str = "high", output_dir: str = "output"):
    if scene_name not in SCENES:
        print(f"Unknown scene: {scene_name}")
        print(f"Available scenes: {', '.join(SCENES.keys())}")
        sys.exit(1)

    scene_file, scene_class = SCENES[scene_name]
    quality_flag = QUALITY_FLAGS.get(quality, "-qh")

    os.makedirs(output_dir, exist_ok=True)

    cmd = [
        sys.executable, "-m", "manim",
        quality_flag,
        "--media_dir", output_dir,
        "--format", "mp4",
        "--disable_caching",
        scene_file,
        scene_class,
    ]

    print(f"Rendering {scene_class} from {scene_file} at {quality} quality...")
    print(f"Command: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=os.path.dirname(os.path.abspath(__file__)))
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description="Render Manim animation scenes")
    parser.add_argument("--scene", "-s", default="doppler",
                        choices=list(SCENES.keys()),
                        help="Scene to render")
    parser.add_argument("--quality", "-q", default="high",
                        choices=list(QUALITY_FLAGS.keys()),
                        help="Render quality")
    parser.add_argument("--output", "-o", default="output",
                        help="Output directory")
    args = parser.parse_args()

    sys.exit(render(args.scene, args.quality, args.output))


if __name__ == "__main__":
    main()
