"""
Black box video generator — upload a Word doc + question number, get a video.
The doc is just for show; the video is pre-rendered based on the question number.
"""
import json
import os
import glob
import time
import random
from flask import Flask, render_template, request, jsonify, send_file

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50MB

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
DATA_DIR = os.path.join(BASE_DIR, "data")

# Build question number → video file mapping
def build_video_map():
    vmap = {}
    for f in glob.glob(os.path.join(OUTPUT_DIR, "*.mp4")):
        name = os.path.basename(f)
        # Pattern: 标题_14.X.mp4
        parts = name.rsplit("_", 1)
        if len(parts) == 2 and parts[1].endswith(".mp4"):
            qnum = parts[1].replace(".mp4", "")
            vmap[qnum] = f
    return vmap

VIDEO_MAP = build_video_map()

# Load question titles
def load_titles():
    titles = {}
    for fname in glob.glob(os.path.join(DATA_DIR, "Q14.*.json")):
        with open(fname) as f:
            bank = json.load(f)
        q = list(bank.values())[0]
        qid = q.get("id", "")
        titles[qid] = q.get("title_cn", q.get("title", ""))
    return titles

TITLES = load_titles()


@app.route("/")
def index():
    return render_template("blackbox.html", titles=TITLES)


@app.route("/api/generate", methods=["POST"])
def generate():
    qnum = request.form.get("question", "").strip()
    doc = request.files.get("doc")

    if not qnum:
        return jsonify({"error": "请输入题号"}), 400

    # Accept formats: "14.1", "14_1", "141", "1"
    normalized = qnum.replace("_", ".")
    if "." not in normalized and normalized.isdigit():
        normalized = f"14.{normalized}"

    video_path = VIDEO_MAP.get(normalized)
    if not video_path:
        # Try fuzzy match
        for k, v in VIDEO_MAP.items():
            if k.endswith(f".{normalized}") or k == normalized:
                video_path = v
                normalized = k
                break

    if not video_path:
        return jsonify({"error": f"未找到题号 {qnum} 对应的视频"}), 404

    # Fake processing delay (3-6 seconds)
    delay = random.uniform(3, 6)
    time.sleep(delay)

    title = TITLES.get(normalized, "")
    return jsonify({
        "status": "success",
        "question": normalized,
        "title": title,
        "video_url": f"/video/{normalized}",
        "download_url": f"/download/{normalized}",
    })


@app.route("/video/<qnum>")
def serve_video(qnum):
    video_path = VIDEO_MAP.get(qnum)
    if not video_path or not os.path.exists(video_path):
        return "Not found", 404
    return send_file(video_path, mimetype="video/mp4")


@app.route("/download/<qnum>")
def download_video(qnum):
    video_path = VIDEO_MAP.get(qnum)
    if not video_path or not os.path.exists(video_path):
        return "Not found", 404
    title = TITLES.get(qnum, qnum)
    return send_file(video_path, mimetype="video/mp4",
                     as_attachment=True, download_name=f"{title}_{qnum}.mp4")


if __name__ == "__main__":
    print(f"Loaded {len(VIDEO_MAP)} videos: {', '.join(sorted(VIDEO_MAP.keys()))}")
    app.run(debug=True, port=5001)
