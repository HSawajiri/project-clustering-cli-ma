#!/bin/bash
set -e

PROJECT_ROOT="${containerWorkspaceFolder:-/workspaces/cli-tool}"

echo "========================================="
echo "CLI Tool Dev Container Setup"
echo "========================================="

# SubAgent定義ファイルの確認
if [ ! -d "$PROJECT_ROOT/.claude/agents" ]; then
  echo "⚠️  Warning: .claude/agents/ directory not found"
  echo "   SubAgent definitions should be placed in .claude/agents/"
fi

# 依存パッケージインストール
if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
  echo "📦 Installing Python dependencies..."
  pip install --quiet --upgrade pip
  pip install --quiet -r "$PROJECT_ROOT/requirements.txt"
  echo "✅ Python dependencies installed"
else
  echo "⚠️  requirements.txt not found"
fi

# PyInstallerのインストール（.exe化用）
echo "📦 Installing PyInstaller..."
pip install --quiet pyinstaller
echo "✅ PyInstaller installed"

echo ""
echo "========================================="
echo "✅ Development environment ready"
echo "========================================="
echo ""
echo "💡 Tips:"
echo "  - Use /agents command to manage SubAgents"
echo "  - Run CLI: python src/main.py"
echo "  - Build .exe: pyinstaller build.spec"
echo ""
