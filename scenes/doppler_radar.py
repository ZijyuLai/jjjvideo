"""
Manim scene for 习题14.17 - Doppler Radar Doppler Filter Bandwidth
Generates a step-by-step derivation animation with formula rendering.
"""
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

# ── LaTeX template (pdflatex backend) ─────────────────────────
TEX = TexTemplate(tex_compiler="pdflatex", output_format=".pdf")

# max width for formulas (screen width ~14.2, leave margin)
MAX_FORMULA_WIDTH = 11.5


def fit(mobject, max_width=MAX_FORMULA_WIDTH):
    """Scale mobject down if it exceeds max_width, keeping aspect ratio."""
    if mobject.width > max_width:
        mobject.scale_to_fit_width(max_width)
    return mobject


def load_question():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(base, "data", "question_bank.json")) as f:
        bank = json.load(f)
    return bank["chapter14"]["questions"]["14.17"]


class DopplerRadarScene(Scene):
    """Full derivation animation for Doppler radar filter bandwidth."""

    def construct(self):
        self.camera.background_color = BG_COLOR
        q = load_question()

        # ── Title ──────────────────────────────────────────────
        self.show_title(q)
        self.wait(0.5)

        # ── Step-by-step derivation ────────────────────────────
        for step in q["steps"]:
            self.show_step(step)
            self.wait(1)

        # ── Final summary ──────────────────────────────────────
        self.show_summary(q)
        self.wait(2)

    # ─── helpers ───────────────────────────────────────────────

    def show_title(self, q):
        title = Text(
            q["title_cn"],
            font_size=42,
            color=TITLE_COLOR,
            weight=BOLD,
        )
        subtitle = Text(
            "习题 " + q["id"],
            font_size=28,
            color=ACCENT_BLUE,
        )
        title_group = VGroup(title, subtitle).arrange(DOWN, buff=0.3)
        title_group.move_to(ORIGIN)

        # decorative line
        line = Line(
            LEFT * 3, RIGHT * 3,
            color=ACCENT_BLUE,
            stroke_width=2,
        )
        line.next_to(title_group, DOWN, buff=0.3)

        self.play(Write(title, run_time=1.2))
        self.play(FadeIn(subtitle, shift=UP * 0.3), GrowFromCenter(line))
        self.wait(1)
        self.play(FadeOut(title_group), FadeOut(line))

    def show_step(self, step):
        # step number badge
        badge = self._make_badge(step["id"])
        badge.to_corner(UL, buff=0.5)

        # step title
        title = Text(
            step["title_cn"],
            font_size=32,
            color=ACCENT_GREEN,
            weight=BOLD,
        )
        title.next_to(badge, RIGHT, buff=0.3)

        self.play(FadeIn(badge, shift=DOWN * 0.3), Write(title))
        self.wait(0.3)

        # formula — centered horizontally, below title
        formula = fit(MathTex(
            step["formula"],
            font_size=36,
            color=FORMULA_COLOR,
            tex_template=TEX,
        ))
        formula.next_to(title, DOWN, buff=0.6)
        formula.set_x(0)  # center horizontally

        # box around formula
        box = SurroundingRectangle(
            formula,
            color=ACCENT_BLUE,
            buff=0.25,
            corner_radius=0.1,
            stroke_width=1.5,
        )

        self.play(Write(formula, run_time=1.5))
        self.play(Create(box))

        # result if present
        if "result" in step:
            result = fit(MathTex(
                step["result"],
                font_size=36,
                color=HIGHLIGHT_COLOR,
                tex_template=TEX,
            ))
            result.next_to(box, DOWN, buff=0.5)
            result.set_x(0)  # center horizontally

            result_box = SurroundingRectangle(
                result,
                color=ACCENT_ORANGE,
                buff=0.2,
                corner_radius=0.1,
                stroke_width=2,
            )
            self.play(Write(result, run_time=1))
            self.play(Create(result_box))
            result_group = VGroup(result, result_box)
        else:
            result_group = None

        # explanation
        explanation = fit(Text(
            step["explanation_cn"],
            font_size=22,
            color=ACCENT_PURPLE,
        ), max_width=12.5)
        explanation.to_edge(DOWN, buff=0.8)

        self.play(FadeIn(explanation, shift=UP * 0.2))
        self.wait(2)

        # clean up
        to_fade = [badge, title, formula, box, explanation]
        if result_group:
            to_fade.append(result_group)
        self.play(*[FadeOut(m) for m in to_fade])

    def show_summary(self, q):
        # final result
        result_title = Text(
            "最终结果",
            font_size=36,
            color=ACCENT_GREEN,
            weight=BOLD,
        )
        result_title.to_edge(UP, buff=1)

        final_formula = fit(MathTex(
            r"B = f_{d,max} - f_{d,min} = 6000 \text{ Hz} = 6 \text{ kHz}",
            font_size=40,
            color=HIGHLIGHT_COLOR,
            tex_template=TEX,
        ))
        final_formula.next_to(result_title, DOWN, buff=0.6)

        box = SurroundingRectangle(
            final_formula,
            color=ACCENT_ORANGE,
            buff=0.3,
            corner_radius=0.15,
            stroke_width=2.5,
        )

        # key concepts
        concepts_title = Text(
            "关键概念",
            font_size=28,
            color=ACCENT_BLUE,
            weight=BOLD,
        )
        concepts_title.next_to(box, DOWN, buff=0.8)

        concepts = VGroup()
        for concept in q["key_concepts_cn"]:
            dot = Dot(radius=0.06, color=ACCENT_PINK)
            text = Text(concept, font_size=20, color=FORMULA_COLOR)
            row = VGroup(dot, text).arrange(RIGHT, buff=0.2)
            concepts.add(row)
        concepts.arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        concepts.next_to(concepts_title, DOWN, buff=0.4)

        self.play(Write(result_title))
        self.play(Write(final_formula, run_time=1.5), Create(box))
        self.play(FadeIn(concepts_title))
        self.play(LaggedStart(*[FadeIn(c, shift=RIGHT * 0.3) for c in concepts], lag_ratio=0.3))

    def _make_badge(self, number):
        circle = Circle(radius=0.3, color=ACCENT_BLUE, fill_opacity=0.2, stroke_width=2)
        num = Text(str(number), font_size=22, color=ACCENT_BLUE, weight=BOLD)
        num.move_to(circle)
        return VGroup(circle, num)


class DopplerFormulaShowcase(Scene):
    """Standalone formula showcase with animated building blocks."""

    def construct(self):
        self.camera.background_color = BG_COLOR

        # Doppler shift formula building animation
        title = Text("多普勒频移公式推导", font_size=36, color=ACCENT_BLUE, weight=BOLD)
        title.to_edge(UP, buff=0.8)
        self.play(Write(title))

        # Build formula piece by piece
        parts = [
            (r"f_d", ACCENT_GREEN),
            (r"=", FORMULA_COLOR),
            (r"\frac{2v \cdot f_0}{c}", HIGHLIGHT_COLOR),
        ]

        formula_parts = VGroup()
        for tex, color in parts:
            part = MathTex(tex, font_size=44, color=color, tex_template=TEX)
            formula_parts.add(part)
        formula_parts.arrange(RIGHT, buff=0.3)
        formula_parts.move_to(ORIGIN)

        for part in formula_parts:
            self.play(Write(part), run_time=0.8)
            self.wait(0.3)

        box = SurroundingRectangle(formula_parts, color=ACCENT_BLUE, buff=0.3, corner_radius=0.1)
        self.play(Create(box))

        # Annotation arrows
        annotations = [
            ("f_d: 多普勒频移", LEFT * 4 + DOWN * 1, ACCENT_GREEN),
            ("v: 目标速度", RIGHT * 3.5 + DOWN * 1, ACCENT_ORANGE),
            ("f_0: 载波频率", LEFT * 4 + DOWN * 2, ACCENT_PINK),
            ("c: 光速", RIGHT * 3.5 + DOWN * 2, ACCENT_PURPLE),
        ]

        ann_group = VGroup()
        for text, pos, color in annotations:
            t = Text(text, font_size=20, color=color)
            t.move_to(pos)
            ann_group.add(t)

        self.play(LaggedStart(*[FadeIn(a, shift=UP * 0.2) for a in ann_group], lag_ratio=0.3))
        self.wait(2)
