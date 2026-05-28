#!/bin/bash
# Setup script for Microwave & Smart Antenna Digital Answer System
# Usage: bash setup.sh

set -e

echo "=== 微波与智能天线课后习题数字化答案系统 - 环境配置 ==="

# Check conda
if ! command -v conda &> /dev/null; then
    echo "Error: conda not found. Please install Anaconda/Miniconda first."
    exit 1
fi

# Create conda environment
echo "Creating conda environment 'jjjvideo' with Python 3.11..."
conda create -n jjjvideo python=3.11 -y 2>/dev/null || echo "Environment may already exist, continuing..."

# Install system dependencies (macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Installing system dependencies via Homebrew..."
    brew install ffmpeg cairo pkg-config pango dvisvgm mupdf-tools 2>/dev/null || true
    brew install texlive 2>/dev/null || true
fi

# Install Python dependencies
echo "Installing Python dependencies..."
conda run -n jjjvideo pip install manim numpy scipy matplotlib flask sympy 2>/dev/null

# Verify installation
echo ""
echo "=== Verification ==="
conda run -n jjjvideo python -c "import manim; print(f'Manim: {manim.__version__}')"
conda run -n jjjvideo python -c "import flask; print(f'Flask: {flask.__version__}')"
conda run -n jjjvideo python -c "import numpy; print(f'NumPy: {numpy.__version__}')"

# Quick render test
echo ""
echo "Running quick render test..."
conda run -n jjjvideo python -m manim -ql --media_dir /tmp/manim_setup_test --disable_caching scenes/doppler_radar.py DopplerFormulaShowcase 2>&1 | tail -5

echo ""
echo "=== Setup complete! ==="
echo "To activate: conda activate jjjvideo"
echo "To render:   python render.py --scene doppler --quality high"
echo "To run web:  python app.py"
