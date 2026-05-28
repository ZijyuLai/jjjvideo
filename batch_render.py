#!/usr/bin/env python3
"""
Batch render all questions from the data/ directory.
Usage: python batch_render.py [--quality low|medium|high|4k]
"""
import argparse
import json
import os
import subprocess
import sys
import shutil

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
SCENE_FILE = "scenes/generic_question.py"

QUALITY_FLAGS = {
    "low": "-ql",
    "medium": "-qm",
    "high": "-qh",
    "4k": "-qk",
}

QUALITY_DIRS = {
    "low": "480p15",
    "medium": "720p30",
    "high": "1080p60",
    "4k": "2160p60",
}


def get_questions():
    questions = []
    for fname in sorted(os.listdir(DATA_DIR)):
        if fname.startswith("Q14.") and fname.endswith(".json"):
            fpath = os.path.join(DATA_DIR, fname)
            with open(fpath) as f:
                bank = json.load(f)
            q = list(bank.values())[0]
            qid = fname.replace("Q", "").replace(".json", "").replace(".", "_")
            title = q.get("title_cn", q.get("title", ""))
            class_name = f"Q{qid}Scene"
            questions.append({
                "file": fname,
                "qid": qid,
                "class_name": class_name,
                "title": title,
            })
    return questions


def render_one(class_name, quality, output_dir):
    qf = QUALITY_FLAGS[quality]
    cmd = [
        sys.executable, "-m", "manim",
        qf,
        "--media_dir", output_dir,
        "--format", "mp4",
        "--disable_caching",
        SCENE_FILE,
        class_name,
    ]
    result = subprocess.run(cmd, cwd=os.path.dirname(os.path.abspath(__file__)),
                            capture_output=True, text=True, timeout=600)
    return result.returncode, result.stderr[-300:] if result.returncode != 0 else ""


def main():
    parser = argparse.ArgumentParser(description="Batch render all questions")
    parser.add_argument("--quality", "-q", default="high", choices=QUALITY_FLAGS.keys())
    parser.add_argument("--output", "-o", default=OUTPUT_DIR)
    parser.add_argument("--start", type=int, default=0, help="Start index (0-based)")
    parser.add_argument("--count", type=int, default=0, help="Number of questions to render (0=all)")
    args = parser.parse_args()

    questions = get_questions()
    if args.count > 0:
        questions = questions[args.start:args.start + args.count]
    elif args.start > 0:
        questions = questions[args.start:]

    total = len(questions)
    print(f"Rendering {total} questions at {args.quality} quality...\n")

    success = 0
    failed = []

    for i, q in enumerate(questions):
        print(f"[{i+1}/{total}] {q['title']} ({q['file']}) ... ", end="", flush=True)
        code, err = render_one(q["class_name"], args.quality, args.output)
        if code == 0:
            # Copy to output root with proper name
            quality_dir = QUALITY_DIRS[args.quality]
            src = os.path.join(args.output, "videos", "generic_question", quality_dir, f"{q['class_name']}.mp4")
            safe_title = q['title'].replace('/', '_').replace('\\', '_').replace(':', '_')
            dst_name = f"{safe_title}_{q['file'].replace('.json', '').replace('Q', '')}.mp4"
            dst = os.path.join(args.output, dst_name)
            if os.path.exists(src):
                shutil.copy2(src, dst)
                print(f"OK -> {dst_name}")
            else:
                print(f"OK (file not found at {src})")
            success += 1
        else:
            print(f"FAILED\n  {err}")
            failed.append(q["file"])

    print(f"\nDone: {success}/{total} succeeded")
    if failed:
        print(f"Failed: {', '.join(failed)}")


if __name__ == "__main__":
    main()
