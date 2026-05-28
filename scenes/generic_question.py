"""
Generic Manim scene for rendering any question from the question bank.
Usage: pass QUESTION_FILE env var to specify which JSON file to render.

This module creates scene classes dynamically for each question file.
"""
import scenes.patch_svg  # noqa: F401
from manim import *
import json
import os

# ── Color palette ──────────────────────────────────────────────
BG_COLOR = "#0f0f1a"
ACCENT_BLUE = "#4fc3f7"
ACCENT_GREEN = "#81c784"
ACCENT_ORANGE = "#ffb74d"
ACCENT_PINK = "#f48fb1"
ACCENT_PURPLE = "#b39ddb"
TITLE_COLOR = "#ffffff"
FORMULA_COLOR = "#e0e0e0"
HIGHLIGHT_COLOR = "#ffd54f"

TEX = TexTemplate(tex_compiler="pdflatex", output_format=".pdf")
MAX_FORMULA_WIDTH = 11.5


def fit(mobject, max_width=MAX_FORMULA_WIDTH):
    if mobject.width > max_width:
        mobject.scale_to_fit_width(max_width)
    return mobject


def load_question_from_file(filepath):
    with open(filepath) as f:
        bank = json.load(f)
    return list(bank.values())[0]


def make_scene_class(json_path, class_name):
    """Dynamically create a Scene class for a given question JSON file."""

    class GenericQuestionScene(Scene):
        def construct(self):
            self.camera.background_color = BG_COLOR
            q = load_question_from_file(json_path)

            # ── Title ──
            title_text = q.get("title_cn", q.get("title", ""))
            qid = q.get("id", "")
            title = Text(title_text, font_size=42, color=TITLE_COLOR, weight=BOLD)
            subtitle = Text(f"习题 {qid}", font_size=28, color=ACCENT_BLUE)
            title_group = VGroup(title, subtitle).arrange(DOWN, buff=0.3)
            self.play(Write(title), FadeIn(subtitle, shift=UP * 0.3))
            self.wait(1)
            self.play(FadeOut(title_group))

            # ── Steps ──
            for step in q.get("steps", []):
                self._show_step(step)
                self.wait(0.5)

            # ── Summary ──
            self._show_summary(q)
            self.wait(2)

        def _show_step(self, step):
            sid = step["id"]
            badge = VGroup(
                Circle(radius=0.3, color=ACCENT_BLUE, fill_opacity=0.2, stroke_width=2),
                Text(str(sid), font_size=22, color=ACCENT_BLUE, weight=BOLD),
            )
            badge[1].move_to(badge[0])
            badge.to_corner(UL, buff=0.5)

            step_title = Text(
                step.get("title_cn", step.get("title", f"Step {sid}")),
                font_size=32, color=ACCENT_GREEN, weight=BOLD,
            )
            step_title.next_to(badge, RIGHT, buff=0.3)
            self.play(FadeIn(badge), Write(step_title))

            formula_tex = step.get("formula", "")
            if formula_tex:
                formula = fit(MathTex(formula_tex, font_size=36, color=FORMULA_COLOR, tex_template=TEX))
                formula.next_to(step_title, DOWN, buff=0.6)
                formula.set_x(0)
                box = SurroundingRectangle(formula, color=ACCENT_BLUE, buff=0.25, corner_radius=0.1)
                self.play(Write(formula, run_time=1.5), Create(box))

            if "result" in step:
                result = fit(MathTex(step["result"], font_size=36, color=HIGHLIGHT_COLOR, tex_template=TEX))
                result.next_to(box, DOWN, buff=0.5)
                result.set_x(0)
                result_box = SurroundingRectangle(result, color=ACCENT_ORANGE, buff=0.2, corner_radius=0.1)
                self.play(Write(result), Create(result_box))

            explanation_text = step.get("explanation_cn", step.get("explanation", ""))
            if explanation_text:
                explanation = fit(Text(explanation_text, font_size=22, color=ACCENT_PURPLE), max_width=12.5)
                explanation.to_edge(DOWN, buff=0.8)
                self.play(FadeIn(explanation))

            self.wait(2)
            self.play(*[FadeOut(m) for m in self.mobjects])

        def _show_summary(self, q):
            result_title = Text("最终结果", font_size=36, color=ACCENT_GREEN, weight=BOLD)
            result_title.to_edge(UP, buff=1)

            # Find the last step's result for summary
            steps = q.get("steps", [])
            summary_formula = ""
            for s in reversed(steps):
                if "result" in s:
                    summary_formula = s["result"]
                    break
            if not summary_formula and steps:
                summary_formula = steps[-1].get("formula", "")

            anchor = result_title  # anchor for positioning concepts below
            if summary_formula:
                final = fit(MathTex(summary_formula, font_size=40, color=HIGHLIGHT_COLOR, tex_template=TEX))
                final.next_to(result_title, DOWN, buff=0.6)
                final_box = SurroundingRectangle(final, color=ACCENT_ORANGE, buff=0.3, corner_radius=0.15, stroke_width=2.5)
                self.play(Write(result_title), Write(final, run_time=1.5), Create(final_box))
                anchor = final_box
            else:
                self.play(Write(result_title))

            concepts = q.get("key_concepts_cn", q.get("key_concepts", []))
            if concepts:
                concepts_title = Text("关键概念", font_size=28, color=ACCENT_BLUE, weight=BOLD)
                concepts_title.next_to(anchor, DOWN, buff=0.8)

                concept_group = VGroup()
                for concept in concepts:
                    dot = Dot(radius=0.06, color=ACCENT_PINK)
                    text = Text(concept, font_size=20, color=FORMULA_COLOR)
                    row = VGroup(dot, text).arrange(RIGHT, buff=0.2)
                    concept_group.add(row)
                concept_group.arrange(DOWN, buff=0.25, aligned_edge=LEFT)
                concept_group.next_to(concepts_title, DOWN, buff=0.4)
                self.play(FadeIn(concepts_title))
                self.play(LaggedStart(*[FadeIn(c, shift=RIGHT * 0.3) for c in concept_group], lag_ratio=0.3))

    GenericQuestionScene.__name__ = class_name
    GenericQuestionScene.__qualname__ = class_name
    return GenericQuestionScene


# ── Auto-generate scene classes for all question files ──
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
SCENE_REGISTRY = {}

for fname in sorted(os.listdir(DATA_DIR)):
    if fname.startswith("Q14.") and fname.endswith(".json"):
        qid = fname.replace("Q", "").replace(".json", "").replace(".", "_")
        fpath = os.path.join(DATA_DIR, fname)
        with open(fpath) as f:
            bank = json.load(f)
        q = list(bank.values())[0]
        title = q.get("title_cn", q.get("title", "")).replace(" ", "_")
        class_name = f"Q{qid}Scene"
        scene_cls = make_scene_class(fpath, class_name)
        globals()[class_name] = scene_cls
        SCENE_REGISTRY[qid] = (f"scenes/generic_question.py", class_name)
