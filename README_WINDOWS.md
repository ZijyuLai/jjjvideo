# 微波与智能天线 - 课后习题数字化答案系统（Windows 版）

> [macOS 版本](README.md) | Windows 版本

## 项目概述

基于 Manim 数学动画引擎的课后习题数字化答案系统，具备三大核心功能：

1. **分步推导动画** — LaTeX 公式逐笔书写、步骤编号、公式框、结果高亮，输出 1080p/60fps MP4 视频
2. **AI 智能批改** — 上传作答文档，AI 自动对比参考答案评分，输出逐步分析和学习建议
3. **题库管理** — 23 道习题独立 JSON 文件，新增题目只需编写 JSON

---

## 快速开始

### 1. 安装系统依赖

#### MiKTeX（LaTeX 发行版）

从 https://miktex.org/download 下载并安装。打开 MiKTeX Console，安装以下包：

```
amsmath, amssymb, amsfonts, mathtools
```

#### FFmpeg

**winget（推荐）：**

```powershell
winget install Gyan.FFmpeg
```

**手动：** 从 https://www.gyan.dev/ffmpeg/builds/ 下载 `ffmpeg-release-essentials.zip`，解压到 `C:\ffmpeg`，将 `C:\ffmpeg\bin` 添加到系统 PATH。

#### dvisvgm

MiKTeX 自带 dvisvgm，位于 `C:\Users\<用户名>\AppData\Local\Programs\MiKTeX\miktex\bin\x64\dvisvgm.exe`。确保 MiKTeX 的 bin 目录在 PATH 中。

#### 验证安装

```powershell
latex --version
dvisvgm --version
ffmpeg -version
```

### 2. 安装 Python 环境

从 https://docs.anaconda.com/miniconda/ 下载 Miniconda，安装后在 **Anaconda Prompt** 中执行：

```bash
conda create -n jjjvideo python=3.11 -y
conda activate jjjvideo
pip install manim numpy scipy matplotlib flask sympy openai python-docx python-dotenv
```

### 3. 配置 AI 评分

编辑项目根目录的 `.env` 文件：

```
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
```

### 4. 渲染视频

```bash
conda activate jjjvideo

# 批量渲染全部 23 道题
python batch_render.py --quality high

# 画质：low(480p) / medium(720p) / high(1080p) / 4k(2160p)
```

### 5. 启动 AI 批改界面

```bash
conda activate jjjvideo
python blackbox.py
# 打开 http://localhost:5001
```

---

## 题库 JSON 格式

每道题一个独立 JSON 文件（`data/Q14.1.json` ~ `data/Q14.23.json`）。格式详见 [macOS README](README.md) 的题库部分。

添加新题目：在 `data/` 下新建 JSON 文件，运行 `python batch_render.py` 即可，无需改代码。

---

## AI 评分原理

```
上传 .docx → python-docx 提取文本（含 OMML 公式转 LaTeX）
    → 拼接参考答案 JSON + 学生作答 → GPT prompt
    → OpenAI 兼容 API 返回评分 JSON
    → 前端展示评分、分析、建议、参考答案、视频
```

---

## Windows 常见问题

| 问题 | 解决 |
|------|------|
| `'latex' 不是内部命令` | MiKTeX bin 目录未加入 PATH |
| `dvisvgm 找不到` | 同上，MiKTeX 自带 dvisvgm |
| `PermissionError` 文件占用 | 已修复，拉取最新代码 |
| `conda activate` 报错 | 先执行 `conda init powershell` 或 `conda init cmd` |
| AI 评分返回空 | 检查 `.env` 中 API Key 和 Base URL |
| 中文字体显示异常 | 安装「微软雅黑」字体 |

---

## 技术栈

| 组件 | 技术 |
|------|------|
| 动画引擎 | Manim Community 0.20+ |
| 公式渲染 | MiKTeX (pdflatex + dvisvgm) |
| AI 评分 | OpenAI 兼容 API |
| 文档解析 | python-docx + OMML→LaTeX 转换器 |
| Web 框架 | Flask |
| 前端公式 | KaTeX (CDN) |
| 视频编码 | FFmpeg |
| 环境管理 | Conda (Python 3.11) |
