#!/bin/bash
# PyInstallerビルドスクリプト
# Project Clustering CLI MA

set -e  # エラー時に即座に終了

echo "============================================================"
echo "プロジェクト名クラスタリングツール ビルド開始"
echo "============================================================"
echo ""

# 依存関係インストール
echo "[1/3] 依存関係をインストール中..."
pip install -r requirements.txt
echo "✓ 依存関係のインストールが完了しました"
echo ""

# PyInstallerインストール
echo "[2/3] PyInstallerをインストール中..."
pip install pyinstaller
echo "✓ PyInstallerのインストールが完了しました"
echo ""

# ビルド実行
echo "[3/3] PyInstallerでビルド中..."
pyinstaller build.spec
echo "✓ ビルドが完了しました"
echo ""

# 完了メッセージ
echo "============================================================"
echo "ビルド完了"
echo "============================================================"
echo "実行ファイル: dist/clustering.exe"
echo ""
echo "配布方法:"
echo "  1. dist/clustering.exe を配布フォルダにコピー"
echo "  2. config.yaml を同じフォルダにコピー"
echo "  3. 入力CSVファイルを同じフォルダに配置"
echo "  4. clustering.exe を実行"
echo ""
echo "使用例:"
echo "  clustering.exe"
echo "  clustering.exe --input data.csv"
echo "  clustering.exe --config custom_config.yaml"
echo ""
