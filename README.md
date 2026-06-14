# 微波与智能天线 - 课后习题数字化答案系统

> macOS 版本 | [Windows 版本](README_WINDOWS.md)

## 项目概述

基于 Manim 数学动画引擎的课后习题数字化答案系统，具备三大核心功能：

1. **分步推导动画** — LaTeX 公式逐笔书写、步骤编号、公式框、结果高亮、关键概念展示，输出 1080p/60fps MP4 视频
2. **AI 智能批改** — 上传作答文档，系统对比 JSON 参考答案自动评分，输出逐步分析、总分和学习建议
3. **题库管理** — 23 道习题独立 JSON 文件存储，新增题目只需编写 JSON，无需改代码

---

## 快速开始

### 1. 环境配置

```bash
# conda 环境
conda create -n jjjvideo python=3.11 -y
conda activate jjjvideo
pip install manim numpy scipy matplotlib flask sympy openai python-docx python-dotenv
```

**系统依赖（macOS）：**

```bash
brew install ffmpeg texlive dvisvgm mupdf-tools
```

**系统依赖（Windows）：**
安装 MiKTeX（https://miktex.org/download）和 FFmpeg，并添加到系统 PATH。

### 2. 配置 AI 评分

编辑项目根目录的 `.env` 文件：

```
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
```

支持任何 OpenAI 兼容接口的模型（如小米 mimo、DeepSeek 等），只需修改 Base URL 和 Model。

### 3. 渲染视频

```bash
conda activate jjjvideo

# 一键渲染全部 23 道题（1080p）
python batch_render.py --quality high

# 渲染单道题
python render.py --scene doppler --quality high

# 画质选项: low(480p), medium(720p), high(1080p), 4k(2160p)
```

渲染完成后视频保存在 `output/` 目录下。

### 4. 启动 AI 批改界面

```bash
conda activate jjjvideo
python blackbox.py
# 打开 http://localhost:5001
```

上传作答 .docx 文档，选择题号，AI 自动评分并展示讲解视频。

---

## 项目结构

```
jjjvideo/
├── blackbox.py               # AI 批改 Flask 应用（端口 5001）
├── app.py                    # 题目浏览 Flask 应用（端口 5000）
├── render.py                 # CLI 单题渲染工具
├── batch_render.py           # CLI 批量渲染工具
├── .env                      # AI API 配置（不纳入版本控制）
├── data/
│   ├── Q14.1.json            # 每题独立 JSON 文件
│   ├── Q14.2.json
│   ├── ...
│   └── Q14.23.json           # 共 23 道题
├── scenes/
│   ├── generic_question.py   # 通用场景引擎（动态生成场景类）
│   ├── patch_svg.py          # dvisvgm 分数线修复
│   ├── doppler_radar.py      # 早期单题场景（已废弃）
│   └── monopole_directivity.py
├── templates/
│   ├── blackbox.html         # AI 批改界面
│   └── index.html            # 题目浏览界面
├── output/                   # 视频输出目录（23 个 .mp4）
├── setup.sh                  # macOS 自动配置脚本
├── README.md
├── README_WINDOWS.md
└── .gitignore
```

---

## 题库 JSON 格式

每道题一个独立的 JSON 文件，命名格式 `Q{章节}.{题号}.json`（如 `Q14.17.json`）。

### 单题结构

```json
{
  "14.17": {
    "id": "14.17",
    "title": "Doppler Radar Filter Bandwidth",
    "title_cn": "多普勒雷达滤波器通带",
    "description": "English problem statement",
    "description_cn": "中文题干",
    "parameters": {
      "f0": {"value": 12e9, "unit": "Hz", "description": "载波频率"}
    },
    "steps": [
      {
        "id": 1,
        "title": "Calculate Wavelength",
        "title_cn": "计算波长",
        "formula": "\\lambda = \\frac{c}{f_0} = 0.025 \\text{ m}",
        "formula_cn": "λ = c/f0 = 0.025 m",
        "explanation": "Wavelength equals speed of light divided by frequency.",
        "explanation_cn": "波长等于光速除以载波频率。"
      },
      {
        "id": 2,
        "title": "Result",
        "title_cn": "结果",
        "formula": "f_d = \\frac{2v}{\\lambda}",
        "formula_cn": "f_d = 2v/λ",
        "result": "f_d = 80 \\text{ Hz}",
        "result_cn": "f_d = 80 Hz",
        "explanation": "Substituting into Doppler formula.",
        "explanation_cn": "代入多普勒公式计算。"
      }
    ],
    "key_concepts": ["Doppler effect", "Filter bandwidth"],
    "key_concepts_cn": ["多普勒效应", "滤波器带宽"]
  }
}
```

### 字段说明

| 字段 | 必填 | 说明 |
|------|------|------|
| `id` | 是 | 题号 |
| `title` / `title_cn` | 是 | 英文/中文标题 |
| `formula` | 是 | LaTeX 公式（`\` 需转义为 `\\`） |
| `formula_cn` | 是 | 纯文本公式，Web 页面备用 |
| `result` / `result_cn` | 否 | 计算结果（有则填） |
| `explanation` / `explanation_cn` | 是 | 推导说明。支持 `$...$` 行内 LaTeX |
| `key_concepts` / `key_concepts_cn` | 是 | 关键概念标签 |

---

## 添加新题目

1. 在 `data/` 下新建 JSON 文件（如 `Q14.24.json`），按上述格式填写题目数据
2. 运行 `python batch_render.py --quality high`，通用场景引擎会自动生成视频
3. 无需修改任何 Python 代码

---

## AI 评分原理

```
用户上传 .docx → python-docx 提取文本（含 OMML 公式转 LaTeX）
    → 拼接参考答案 JSON + 学生作答 → 构建 prompt
    → 调用 OpenAI 兼容 API → GPT 返回 JSON 评分结果
    → 前端展示：评分、逐步分析、学习建议、参考答案、讲解视频
```

后端通过 `.env` 配置 API Key、Base URL 和模型名，支持任何 OpenAI 兼容接口。

---

## 常见问题

| 问题 | 解决 |
|------|------|
| 公式渲染失败 | 确保安装了 texlive、dvisvgm |
| AI 评分返回空 | 检查 `.env` 中的 API Key 和 Base URL |
| Windows 下文件权限错误 | 已修复，拉取最新代码 |
| 中文字体显示异常 | macOS 自带中文字体，Windows 需安装微软雅黑 |
| 渲染速度慢 | 预览用 `--quality low`，正式用 `--quality high` |
| 清除缓存重渲染 | 删掉 `output/videos/` 目录 |

---

## 技术栈

| 组件 | 技术 |
|------|------|
| 动画引擎 | Manim Community 0.20+ |
| 公式渲染 | pdflatex + dvisvgm（配合 patch_svg 修复分数线） |
| AI 评分 | OpenAI 兼容 API (GPT / mimo-v2.5-pro) |
| 文档解析 | python-docx + OMML→LaTeX 转换器 |
| Web 框架 | Flask × 2（端口 5000 / 5001） |
| 前端公式 | KaTeX (CDN) |
| 数值计算 | NumPy / SciPy |
| 视频编码 | FFmpeg |
| 环境管理 | Conda (Python 3.11) |
| 报告生成 | docx (Node.js) |
