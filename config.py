"""Project configuration."""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
SCENES_DIR = os.path.join(BASE_DIR, "scenes")

# Manim defaults
MANIM_QUALITY = "high"  # low/medium/high/4k
MANIM_FORMAT = "mp4"

# Flask
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5000
FLASK_DEBUG = True
