# ビルド手順書（Windows PC向け）

このドキュメントは、Windows PC上で.exeファイルをビルドする手順を説明します。

---

## 前提条件

### 必須環境
- **Python 3.11以上** がインストールされている
- **pip** が使用可能
- **Git** がインストールされている（clone済み）

### Python環境の確認

コマンドプロンプトまたはPowerShellで以下を実行：

```cmd
python --version
```

期待される出力例: `Python 3.11.x` または `Python 3.12.x`

---

## ビルド手順

### ステップ1: リポジトリをclone（済み）

```cmd
git clone https://github.com/HSawajiri/project-clustering-cli-ma.git
cd project-clustering-cli-ma
```

### ステップ2: 最新のコードを取得（必要に応じて）

```cmd
git pull origin main
```

### ステップ3: ビルドスクリプトを実行

```cmd
build.bat
```

**実行内容:**
1. 依存パッケージのインストール（requirements.txt）
2. PyInstallerのインストール
3. .exeファイルのビルド

**処理時間:** 約5〜10分（初回のみ、環境による）

### ステップ4: ビルド成果物の確認

ビルドが成功すると、以下のファイルが生成されます：

```
project-clustering-cli-ma/
├── dist/
│   └── clustering.exe    ← これが実行ファイル
├── build/                ← 中間ファイル（削除可）
└── ...
```

---

## トラブルシューティング

### エラー: `python` コマンドが見つからない

**原因:** Pythonが環境変数PATHに追加されていない

**対処法:**
1. Pythonインストーラーを再実行
2. "Add Python to PATH" にチェックを入れて再インストール

または、`python` の代わりに `py` コマンドを使用：

```cmd
py --version
```

---

### エラー: `pip install` で失敗する

**原因:** ネットワークエラー、または権限不足

**対処法1（プロキシ設定）:**

会社のプロキシ経由の場合：

```cmd
set http_proxy=http://proxy.company.com:8080
set https_proxy=http://proxy.company.com:8080
pip install -r requirements.txt
```

**対処法2（管理者権限）:**

コマンドプロンプトを「管理者として実行」してから再実行

---

### エラー: `pyinstaller` でビルドが失敗する

**原因1:** メモリ不足

**対処法:** 他のアプリケーションを終了してから再実行

**原因2:** ウイルス対策ソフトがブロック

**対処法:** ウイルス対策ソフトを一時的に無効化、または `dist/` フォルダを除外リストに追加

---

### エラー: `ModuleNotFoundError: No module named 'sklearn'`

**原因:** 依存パッケージのインストールが不完全

**対処法:**

```cmd
pip install scikit-learn==1.3.2
pip install pandas==2.1.3
pip install numpy==1.26.2
pip install pyyaml==6.0.1
```

その後、再度ビルド：

```cmd
pyinstaller build.spec
```

---

## ビルド後の動作確認

### テスト実行

```cmd
cd dist
clustering.exe --help
```

期待される出力：使用方法のヘルプメッセージ

### サンプルデータでテスト

1. `dist/` フォルダに移動
2. `config.yaml` をコピー
3. テストCSVファイルを配置
4. `clustering.exe` を実行

```cmd
copy ..\config.yaml .
copy ..\shared\data\test_orders.csv input.csv
clustering.exe
```

---

## 配布方法

### 配布パッケージの作成

以下のファイルを1つのフォルダにまとめます：

```
clustering_v1.0/
├── clustering.exe       ← dist/clustering.exe をコピー
├── config.yaml          ← プロジェクトルートからコピー
└── README.md            ← 使い方説明（任意）
```

このフォルダをZIP圧縮して配布、または直接コピーします。

---

## サポート

### ドキュメント

- **要件定義書**: [docs/requirements.md](docs/requirements.md)
- **設計仕様書**: [docs/specification.md](docs/specification.md)
- **使い方**: [README.md](README.md)

### 問題が解決しない場合

1. `clustering.log` を確認
2. エラーメッセージをコピーして報告
3. Python/pip のバージョンを確認

---

## 補足情報

### ビルドオプション（高度）

`build.spec` を編集することで、以下をカスタマイズできます：

- 実行ファイル名（`name='clustering'`）
- コンソール表示（`console=True/False`）
- アイコン（`icon='app.ico'`）
- 同梱ファイル（`datas=[...]`）

編集後、再ビルド：

```cmd
pyinstaller build.spec
```

---

**最終更新:** 2026-02-09
**作成者:** Claude Code (Project Manager)
