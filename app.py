"""
Flask web application for the digital answer system.
Provides question browsing, step-by-step viewing, and video rendering.
"""
import json
import os
import subprocess
import sys
from flask import Flask, render_template, jsonify, request, send_file

app = Flask(__name__)

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")


def load_bank():
    with open(os.path.join(DATA_DIR, "question_bank.json")) as f:
        return json.load(f)


@app.route("/")
def index():
    bank = load_bank()
    return render_template("index.html", bank=bank)


@app.route("/api/chapters")
def get_chapters():
    bank = load_bank()
    chapters = []
    for key, ch in bank.items():
        chapters.append({
            "id": key,
            "title": ch["title"],
            "question_count": len(ch["questions"]),
        })
    return jsonify(chapters)


@app.route("/api/question/<chapter>/<qid>")
def get_question(chapter, qid):
    bank = load_bank()
    ch = bank.get(chapter)
    if not ch:
        return jsonify({"error": "Chapter not found"}), 404
    q = ch["questions"].get(qid)
    if not q:
        return jsonify({"error": "Question not found"}), 404
    return jsonify(q)


@app.route("/api/render", methods=["POST"])
def render_scene():
    data = request.json
    scene = data.get("scene", "doppler")
    quality = data.get("quality", "high")

    scene_map = {
        "doppler": ("scenes/doppler_radar.py", "DopplerRadarScene"),
        "doppler_formula": ("scenes/doppler_radar.py", "DopplerFormulaShowcase"),
        "monopole": ("scenes/monopole_directivity.py", "MonopoleDirectivityScene"),
    }

    quality_map = {"low": "-ql", "medium": "-qm", "high": "-qh", "4k": "-qk"}

    if scene not in scene_map:
        return jsonify({"error": "Unknown scene"}), 400

    scene_file, scene_class = scene_map[scene]
    qf = quality_map.get(quality, "-qh")

    cmd = [
        sys.executable, "-m", "manim",
        qf,
        "--media_dir", OUTPUT_DIR,
        "--format", "mp4",
        "--disable_caching",
        scene_file,
        scene_class,
    ]

    try:
        result = subprocess.run(
            cmd,
            cwd=os.path.dirname(os.path.abspath(__file__)),
            capture_output=True,
            text=True,
            timeout=300,
        )
        if result.returncode == 0:
            # find the output file
            media_dir = os.path.join(OUTPUT_DIR, "videos")
            for root, dirs, files in os.walk(media_dir):
                for f in files:
                    if f.endswith(".mp4") and cls in f:
                        return jsonify({
                            "status": "success",
                            "video_path": os.path.join(root, f),
                        })
            return jsonify({"status": "success", "message": "Rendered but file not found"})
        else:
            return jsonify({"status": "error", "stderr": result.stderr[-500:]})
    except subprocess.TimeoutExpired:
        return jsonify({"status": "error", "message": "Render timed out"})


@app.route("/video/<path:filepath>")
def serve_video(filepath):
    return send_file(filepath, mimetype="video/mp4")


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    app.run(debug=True, port=5000)
