# Project Clustering CLI MA

プロジェクト作業名のクラスタリングCLIツール（Multi-Agent 実験版）

## 概要

このプロジェクトは、受注データの作業名表記揺れを自動分類するCLIツールです。
TF-IDF + コサイン類似度 + 階層的クラスタリングにより、プロジェクト名のクラスタリングを実行します。

**このプロジェクトの特徴:**
- マルチエージェント体制（Manager + 4つのSubAgent）での開発を実験的に実施
- `project-clustering-cli` と同じ機能要件
- ドキュメントファーストの開発プロセスの検証

## 技術スタック

- **言語**: Python 3.11+
- **設定管理**: PyYAML
- **.exe化**: PyInstaller
- **開発環境**: VS Code Dev Container

## プロジェクト構成

```
cli-tool/
├── .devcontainer/          # Dev Container設定
│   ├── devcontainer.json
│   └── setup.sh
│
├── .claude/
│   └── agents/             # SubAgent定義（5人体制）
│       ├── requirements-analyst.yaml
│       ├── designer.yaml
│       ├── implementer.yaml
│       └── tester.yaml
│
├── docs/                   # ドキュメント
│   ├── requirements.md
│   ├── specification.md
│   ├── wbs.md
│   └── handoff/            # SubAgent間引き継ぎ
│
├── shared/                 # 共有リソース
│   ├── data/               # テストデータ
│   └── config/             # 共通設定
│
├── src/                    # ソースコード
│   ├── main.py             # エントリーポイント
│   ├── config_handler.py   # 設定ファイル管理
│   └── logger.py           # ロガー設定
│
├── config.yaml             # 設定ファイル
├── build.spec              # PyInstaller設定
├── requirements.txt        # Python依存パッケージ
└── README.md               # このファイル
```

## セットアップ

### 1. Dev Containerで開く

```bash
cd /path/to/cli-tool
code .
# VS Code: "Reopen in Container"
```

### 2. 依存パッケージインストール（自動）

Dev Container起動時に自動的に実行されます。

手動でインストールする場合:
```bash
pip install -r requirements.txt
```

## 使い方

### 開発モード（Python直接実行）

```bash
cd /path/to/cli-tool
python src/main.py
```

### 設定ファイル編集

`config.yaml` で動作をカスタマイズ:

```yaml
app:
  name: "My CLI Tool"
  log_level: "INFO"

io:
  input_file: "input.csv"
  output_file: "output.csv"
```

### .exe化（PyInstaller）

```bash
# .exeファイルを生成
pyinstaller build.spec

# 出力先: dist/cli-tool.exe (Windows) または dist/cli-tool (macOS/Linux)
```

### .exeの配布

```
配布フォルダ/
├── cli-tool.exe        # 実行ファイル
├── config.yaml         # 設定ファイル
└── input.csv           # 入力データ（例）
```

ユーザーは `cli-tool.exe` をダブルクリックまたはコマンドラインから実行します。

## 開発ガイド

このプロジェクトは5人体制SubAgentアーキテクチャを採用しています。

詳細は [CLAUDE.md](./CLAUDE.md) を参照してください。

### SubAgentの使い方

```
User: "Requirements Analyst SubAgentで要件を整理してください"
User: "Designer SubAgentで設計書を作成してください"
User: "Implementer SubAgentでコードを実装してください"
User: "Tester SubAgentでテストを実行してください"
```

## ドキュメント

| ドキュメント | パス | 内容 |
|------------|------|------|
| **要件定義書** | `docs/requirements.md` | 機能要件・非機能要件 |
| **仕様書** | `docs/specification.md` | 技術詳細・実装仕様 |
| **WBS** | `docs/wbs.md` | 作業分解構造・進捗管理 |

## トラブルシューティング

### PyInstallerでのビルドエラー

```bash
# キャッシュをクリア
pyinstaller --clean build.spec
```

### 依存パッケージの追加

1. `requirements.txt` に追加
2. Dev Containerを再ビルド、または手動でインストール

```bash
pip install -r requirements.txt
```

## ライセンス

（未定）

## 連絡先

（未定）
