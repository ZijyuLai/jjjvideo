# 微波与智能天线 - 课后习题数字化答案系统（Windows 版）

> [macOS 版本](README.md) | Windows 版本

## 项目概述

基于 Manim 数学动画引擎的课后习题数字化答案系统，支持：

- LaTeX 公式渲染（pdflatex 后端）
- 分步推导动画（带编号徽章、公式框、结果高亮）
- 1080p / 4K 视频输出
- Web 界面浏览与在线渲染
- JSON 题库管理，易于扩展

---

## 快速开始

### 1. 安装系统依赖

#### 1.1 安装 MiKTeX（LaTeX 发行版）

从 https://miktex.org/download 下载 MiKTeX 安装包并安装。

安装完成后打开 MiKTeX Console，点击 "Packages" 搜索并安装以下包：
- `amsmath`
- `amssymb`
- `amsfonts`
- `mathtools`

或者在命令行执行（以管理员身份运行 PowerShell）：

```powershell
mpm --install amsmath amssymb amsfonts mathtools
```

#### 1.2 安装 FFmpeg

**方式 A：使用 winget（推荐）**

```powershell
winget install Gyan.FFmpeg
```

**方式 B：手动安装**

1. 从 https://www.gyan.dev/ffmpeg/builds/ 下载 `ffmpeg-release-essentials.zip`
2. 解压到如 `C:\ffmpeg`
3. 将 `C:\ffmpeg\bin` 添加到系统 PATH 环境变量：
   - 右键「此电脑」→ 属性 → 高级系统设置 → 环境变量
   - 在「系统变量」中找到 `Path`，编辑，添加 `C:\ffmpeg\bin`

**方式 C：使用 Chocolatey**

```powershell
choco install ffmpeg
```

#### 1.3 安装 dvisvgm

MiKTeX 自带 dvisvgm，通常位于 `C:\Users\<用户名>\AppData\Local\Programs\MiKTeX\miktex\bin\x64\dvisvgm.exe`。

如果命令行找不到 dvisvgm，需要将其 bin 目录添加到 PATH。

验证安装：

```powershell
latex --version
dvisvgm --version
ffmpeg -version
```

### 2. 安装 Conda

从 https://docs.anaconda.com/miniconda/ 下载并安装 Miniconda（Windows 64-bit）。

安装后打开 **Anaconda Prompt**（不是 PowerShell/CMD）进行后续操作。

### 3. 创建 Conda 环境

```bash
conda create -n jjjvideo python=3.11 -y
conda activate jjjvideo
pip install manim numpy scipy matplotlib flask sympy
```

### 4. 验证安装

```bash
python -c "import manim; print(manim.__version__)"
```

应输出类似 `0.20.1`。

### 5. 渲染视频

```bash
conda activate jjjvideo

# 渲染推导动画（默认 1080p）
python render.py --scene doppler

# 渲染公式展示（720p）
python render.py --scene doppler_formula --quality medium

# 可选质量参数
#   low    → 480p, 15fps
#   medium → 720p, 30fps
#   high   → 1080p, 60fps（默认）
#   4k     → 2160p, 60fps

# 指定输出目录
python render.py --scene doppler --quality high --output my_output
```

渲染完成后视频保存在 `output\videos\<场景名>\<画质>\` 目录下。

### 6. 启动 Web 界面

```bash
conda activate jjjvideo
python app.py
# 浏览器访问 http://localhost:5000
```

---

## 项目结构

```
jjjvideo\
├── app.py                    # Flask Web 应用
├── render.py                 # CLI 渲染工具
├── config.py                 # 项目配置
├── README.md                 # macOS 版说明
├── README_WINDOWS.md         # 本文档
├── data\
│   └── question_bank.json    # 题库数据
├── scenes\
│   ├── __init__.py
│   └── doppler_radar.py      # Manim 动画场景
├── templates\
│   └── index.html            # Web 界面模板
└── output\                   # 渲染输出目录
    └── videos\
        └── doppler_radar\
            ├── 480p15\
            ├── 720p30\
            ├── 1080p60\
            └── 2160p60\
```

---

## 题库格式详解

题库文件：`data\question_bank.json`

### 顶层结构

```json
{
  "chapter14": {
    "title": "Chapter 14 - Radar Applications & Antenna Theory",
    "questions": {
      "14.17": { ... },
      "14.18": { ... }
    }
  },
  "chapter5": {
    "title": "Chapter 5 - Impedance Matching",
    "questions": {
      "5.1": { ... }
    }
  }
}
```

- 顶层 key 为章节标识，如 `chapter14`、`chapter5`
- 每个章节包含 `title` 和 `questions`
- `questions` 中每个 key 为题号

### 单题结构

```json
{
  "id": "14.17",
  "title": "Doppler Radar - Doppler Filter Bandwidth",
  "title_cn": "多普勒雷达 - 多普勒滤波器通带宽度",
  "description": "English problem statement",
  "description_cn": "中文题干描述",
  "parameters": {
    "f0": {
      "value": 10000000000,
      "unit": "Hz",
      "description": "Radar carrier frequency (雷达载波频率)"
    }
  },
  "steps": [ ... ],
  "key_concepts": ["English concept 1", "English concept 2"],
  "key_concepts_cn": ["中文概念1", "中文概念2"]
}
```

### 字段说明

| 字段 | 必填 | 说明 |
|------|------|------|
| `id` | 是 | 题号，如 `"14.17"` |
| `title` | 是 | 英文标题 |
| `title_cn` | 是 | 中文标题 |
| `description` | 否 | 英文题干 |
| `description_cn` | 否 | 中文题干 |
| `parameters` | 否 | 题目参数，方便程序化使用 |
| `steps` | 是 | 推导步骤数组 |
| `key_concepts` | 是 | 英文关键概念标签 |
| `key_concepts_cn` | 是 | 中文关键概念标签 |

### 步骤结构 (steps)

```json
{
  "id": 1,
  "title": "Doppler Shift Formula",
  "title_cn": "多普勒频移公式",
  "formula": "f_d = \\frac{2v \\cdot f_0}{c}",
  "formula_cn": "f_d = 2vf_0 / c",
  "result": "f_{d,min} = 666.67 \\text{ Hz}",
  "result_cn": "f_d,min = 666.67 Hz",
  "explanation": "English explanation of this step.",
  "explanation_cn": "这一步的中文说明。"
}
```

| 字段 | 必填 | 说明 |
|------|------|------|
| `id` | 是 | 步骤序号（从 1 开始） |
| `title` | 是 | 英文步骤标题 |
| `title_cn` | 是 | 中文步骤标题 |
| `formula` | 是 | **LaTeX 格式公式**，用于 Manim 渲染动画 |
| `formula_cn` | 是 | 简化公式文字，用于 Web 页面纯文本显示 |
| `result` | 否 | 计算结果的 LaTeX 公式（有结果时填） |
| `result_cn` | 否 | 结果的中文文字描述 |
| `explanation` | 是 | 英文推导说明 |
| `explanation_cn` | 是 | 中文推导说明 |

### LaTeX 公式编写注意事项

1. **反斜杠需要转义**：JSON 中 `\` 要写成 `\\`
   - LaTeX: `\frac{a}{b}` → JSON: `"\\frac{a}{b}"`
2. **公式不要太长**：超过 11.5 个单位宽度会被自动缩放，建议拆分
3. **常用 LaTeX 语法**：
   - 分数：`\\frac{分子}{分母}`
   - 上标：`10^{9}`
   - 下标：`f_{d,min}`
   - 乘号：`\\times`
   - 文本：`\\text{ Hz}`
   - 希腊字母：`\\lambda`、`\\omega`、`\\beta`

---

## 添加新题目完整流程

### 第 1 步：编辑题库 JSON

在 `data\question_bank.json` 中添加题目。示例——添加习题 14.18：

```json
{
  "chapter14": {
    "title": "Chapter 14 - Radar Applications & Antenna Theory",
    "questions": {
      "14.17": { ... },
      "14.18": {
        "id": "14.18",
        "title": "Radar Range Equation",
        "title_cn": "雷达距离方程",
        "description": "Calculate the maximum detection range.",
        "description_cn": "计算雷达系统的最大探测距离。",
        "parameters": {
          "Pt": {"value": 1e6, "unit": "W", "description": "Transmit power"},
          "G": {"value": 40, "unit": "dB", "description": "Antenna gain"}
        },
        "steps": [
          {
            "id": 1,
            "title": "Radar Range Equation",
            "title_cn": "雷达距离方程",
            "formula": "R_{max} = \\left(\\frac{P_t G^2 \\lambda^2 \\sigma}{(4\\pi)^3 S_{min}}\\right)^{1/4}",
            "formula_cn": "R_max = (Pt*G^2*λ^2*σ / (4π)^3*Smin)^(1/4)",
            "explanation": "The maximum radar range depends on transmit power, antenna gain, wavelength, target RCS, and minimum detectable signal.",
            "explanation_cn": "最大雷达距离取决于发射功率、天线增益、波长、目标RCS和最小可检测信号。"
          }
        ],
        "key_concepts": ["Radar range equation", "Link budget"],
        "key_concepts_cn": ["雷达距离方程", "链路预算"]
      }
    }
  }
}
```

### 第 2 步：创建 Manim 场景

在 `scenes\` 目录下新建 Python 文件，如 `scenes\range_equation.py`：

```python
"""Manim scene for 习题14.18 - Radar Range Equation."""
from manim import *
import json
import os

from scenes.doppler_radar import (
    BG_COLOR, ACCENT_BLUE, ACCENT_GREEN, ACCENT_ORANGE,
    ACCENT_PURPLE, TITLE_COLOR, FORMULA_COLOR,
    HIGHLIGHT_COLOR, TEX, fit,
)

def load_question():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(base, "data", "question_bank.json")) as f:
        bank = json.load(f)
    return bank["chapter14"]["questions"]["14.18"]


class RangeEquationScene(Scene):
    def construct(self):
        self.camera.background_color = BG_COLOR
        q = load_question()

        # 标题
        title = Text(q["title_cn"], font_size=42, color=TITLE_COLOR, weight=BOLD)
        subtitle = Text("习题 " + q["id"], font_size=28, color=ACCENT_BLUE)
        group = VGroup(title, subtitle).arrange(DOWN, buff=0.3)
        self.play(Write(title), FadeIn(subtitle, shift=UP * 0.3))
        self.wait(1)
        self.play(FadeOut(group))

        # 分步推导
        for step in q["steps"]:
            badge = VGroup(
                Circle(radius=0.3, color=ACCENT_BLUE, fill_opacity=0.2, stroke_width=2),
                Text(str(step["id"]), font_size=22, color=ACCENT_BLUE, weight=BOLD),
            )
            badge[1].move_to(badge[0])
            badge.to_corner(UL, buff=0.5)

            step_title = Text(step["title_cn"], font_size=32, color=ACCENT_GREEN, weight=BOLD)
            step_title.next_to(badge, RIGHT, buff=0.3)
            self.play(FadeIn(badge), Write(step_title))

            formula = fit(MathTex(step["formula"], font_size=36, color=FORMULA_COLOR, tex_template=TEX))
            formula.next_to(step_title, DOWN, buff=0.6)
            formula.set_x(0)
            box = SurroundingRectangle(formula, color=ACCENT_BLUE, buff=0.25, corner_radius=0.1)
            self.play(Write(formula), Create(box))

            if "result" in step:
                result = fit(MathTex(step["result"], font_size=36, color=HIGHLIGHT_COLOR, tex_template=TEX))
                result.next_to(box, DOWN, buff=0.5)
                result.set_x(0)
                result_box = SurroundingRectangle(result, color=ACCENT_ORANGE, buff=0.2, corner_radius=0.1)
                self.play(Write(result), Create(result_box))

            explanation = fit(Text(step["explanation_cn"], font_size=22, color=ACCENT_PURPLE), max_width=12.5)
            explanation.to_edge(DOWN, buff=0.8)
            self.play(FadeIn(explanation))
            self.wait(2)
            self.play(*[FadeOut(m) for m in self.mobjects])
```

### 第 3 步：注册新场景

在 `render.py` 的 `SCENES` 字典中添加：

```python
SCENES = {
    "doppler": ("scenes/doppler_radar.py", "DopplerRadarScene"),
    "doppler_formula": ("scenes/doppler_radar.py", "DopplerFormulaShowcase"),
    "range_equation": ("scenes/range_equation.py", "RangeEquationScene"),  # 新增
}
```

在 `app.py` 的 `scene_map` 中添加：

```python
scene_map = {
    "doppler": ("scenes/doppler_radar.py", "DopplerRadarScene"),
    "doppler_formula": ("scenes/doppler_radar.py", "DopplerFormulaShowcase"),
    "range_equation": ("scenes/range_equation.py", "RangeEquationScene"),  # 新增
}
```

### 第 4 步：渲染

```bash
python render.py --scene range_equation --quality high
```

---

## Windows 常见问题

### Q: 提示 `'latex' 不是内部或外部命令`

MiKTeX 的 bin 目录没有加入 PATH。找到 MiKTeX 安装目录（通常在 `C:\Users\<用户名>\AppData\Local\Programs\MiKTeX\miktex\bin\x64`），将其添加到系统 PATH。

### Q: 提示找不到 dvisvgm

同上，确保 MiKTeX 的 bin 目录在 PATH 中。MiKTeX 自带 dvisvgm。

### Q: FFmpeg 相关错误

确保 FFmpeg 已安装且 `ffmpeg.exe` 所在目录在 PATH 中。安装后重新打开终端使 PATH 生效。

### Q: 中文显示为方块

Windows 10/11 自带中文字体，一般不会出现此问题。如遇到，安装「微软雅黑」字体。

### Q: 渲染速度慢

- 使用 `--quality low` 进行预览（480p）
- 使用 `--quality high` 渲染最终版本（1080p）
- Manim 会缓存已渲染的片段，重复渲染会更快

### Q: 如何清除缓存重新渲染

```bash
# 删除场景输出目录
rmdir /s /q output\videos\<场景名>

# 或在命令行加 --disable_caching 参数
python render.py --scene doppler --quality high
```

### Q: conda activate 报错

如果 `conda activate` 不生效，先执行：

```bash
conda init bash   # 或 conda init powershell
```

然后重新打开终端。

---

## 技术栈

| 组件 | 技术 | 用途 |
|------|------|------|
| 动画引擎 | Manim Community 0.20+ | 数学公式动画渲染 |
| 公式排版 | MiKTeX (pdflatex + dvisvgm) | LaTeX → SVG 转换 |
| Web 框架 | Flask | 界面与 API |
| 数值计算 | NumPy / SciPy | 参数计算 |
| 图表绘制 | Matplotlib | 辅助图表 |
| 视频编码 | FFmpeg | MP4 视频输出 |
