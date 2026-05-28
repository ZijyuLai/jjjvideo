"""Manim scene for 习题14.3 - Monopole Antenna Directivity."""
import scenes.patch_svg  # noqa: F401 — fix fraction lines before MathTex
from manim import *
import json
import os

from scenes.doppler_radar import (
    BG_COLOR, ACCENT_BLUE, ACCENT_GREEN, ACCENT_ORANGE,
    ACCENT_PINK, ACCENT_PURPLE, TITLE_COLOR, FORMULA_COLOR,
    HIGHLIGHT_COLOR, TEX, fit,
)

# LaTeX formulas for each step (converted from Unicode)
STEP_FORMULAS = {
    1: r"D = \frac{4\pi \, |F_{max}|^2}{\int_0^{2\pi}\!\int_0^{\pi} |F|^2 \sin\theta \, d\theta \, d\phi}",
    2: r"|F_{max}|^2 = A^2 \quad (\theta = 90°)",
    3: r"\int_0^{2\pi}\!\int_0^{\pi/2} (A\sin\theta)^2 \sin\theta \, d\theta \, d\phi = 2\pi A^2 \times \frac{2}{3} = \frac{4\pi A^2}{3}",
    4: r"D = \frac{4\pi A^2}{4\pi A^2 / 3} = 3",
    5: r"D_{dB} = 10\log_{10}(3) = 4.77 \text{ dB}",
}


def load_question():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(base, "data", "Q14.3.json")) as f:
        bank = json.load(f)
    return bank["14.3"]


class MonopoleDirectivityScene(Scene):
    """Full derivation animation for monopole antenna directivity."""

    def construct(self):
        self.camera.background_color = BG_COLOR
        q = load_question()

        # ── Title ──
        title = Text(q["title_cn"], font_size=42, color=TITLE_COLOR, weight=BOLD)
        subtitle = Text("习题 " + q["id"], font_size=28, color=ACCENT_BLUE)
        title_group = VGroup(title, subtitle).arrange(DOWN, buff=0.3)
        self.play(Write(title), FadeIn(subtitle, shift=UP * 0.3))
        self.wait(1)
        self.play(FadeOut(title_group))

        # ── Steps ──
        for step in q["steps"]:
            self.show_step(step)
            self.wait(0.5)

        # ── Summary ──
        self.show_summary(q)
        self.wait(2)

    def show_step(self, step):
        sid = step["id"]

        # badge
        badge = VGroup(
            Circle(radius=0.3, color=ACCENT_BLUE, fill_opacity=0.2, stroke_width=2),
            Text(str(sid), font_size=22, color=ACCENT_BLUE, weight=BOLD),
        )
        badge[1].move_to(badge[0])
        badge.to_corner(UL, buff=0.5)

        # title
        step_title = Text(step["title_cn"], font_size=32, color=ACCENT_GREEN, weight=BOLD)
        step_title.next_to(badge, RIGHT, buff=0.3)
        self.play(FadeIn(badge), Write(step_title))

        # formula (use pre-defined LaTeX)
        formula_tex = STEP_FORMULAS.get(sid, step["formula"])
        formula = fit(MathTex(formula_tex, font_size=36, color=FORMULA_COLOR, tex_template=TEX))
        formula.next_to(step_title, DOWN, buff=0.6)
        formula.set_x(0)
        box = SurroundingRectangle(formula, color=ACCENT_BLUE, buff=0.25, corner_radius=0.1)
        self.play(Write(formula, run_time=1.5), Create(box))

        # explanation
        explanation = fit(Text(step["explanation_cn"], font_size=22, color=ACCENT_PURPLE), max_width=12.5)
        explanation.to_edge(DOWN, buff=0.8)
        self.play(FadeIn(explanation))
        self.wait(2)

        self.play(*[FadeOut(m) for m in self.mobjects])

    def show_summary(self, q):
        result_title = Text("最终结果", font_size=36, color=ACCENT_GREEN, weight=BOLD)
        result_title.to_edge(UP, buff=1)

        final = fit(MathTex(
            r"D = 3 \quad \Rightarrow \quad D_{dB} = 4.77 \text{ dB}",
            font_size=40, color=HIGHLIGHT_COLOR, tex_template=TEX,
        ))
        final.next_to(result_title, DOWN, buff=0.6)
        final_box = SurroundingRectangle(final, color=ACCENT_ORANGE, buff=0.3, corner_radius=0.15, stroke_width=2.5)

        concepts_title = Text("关键概念", font_size=28, color=ACCENT_BLUE, weight=BOLD)
        concepts_title.next_to(final_box, DOWN, buff=0.8)

        concepts = VGroup()
        for concept in q["key_concepts_cn"]:
            dot = Dot(radius=0.06, color=ACCENT_PINK)
            text = Text(concept, font_size=20, color=FORMULA_COLOR)
            row = VGroup(dot, text).arrange(RIGHT, buff=0.2)
            concepts.add(row)
        concepts.arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        concepts.next_to(concepts_title, DOWN, buff=0.4)

        self.play(Write(result_title))
        self.play(Write(final, run_time=1.5), Create(final_box))
        self.play(FadeIn(concepts_title))
        self.play(LaggedStart(*[FadeIn(c, shift=RIGHT * 0.3) for c in concepts], lag_ratio=0.3))
