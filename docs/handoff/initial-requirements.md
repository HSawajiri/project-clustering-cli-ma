# 初期要求事項

**プロジェクト名:** project-clustering-cli-ma
**作成日:** 2026-02-06
**作成者:** 新規プロジェクト相談エージェント（ホストOS）
**対象者:** Dev Container内のManager

---

## プロジェクト概要

### プロジェクト名
project-clustering-cli-ma（Multi-Agent 実験版）

### プロジェクトの目的
既存の「Excelクラスタリングアプリ」（`~/projects/excel-clustering-app`）からGUIを除去し、
コマンドライン実行可能な.exeファイルとして提供するバッチ処理ツールを開発する。

**このプロジェクトの特徴:**
- マルチエージェント体制での開発を実験的に実施
- `project-clustering-cli` と同じ機能要件
- Manager + 4つのSubAgent（Requirements Analyst、Designer、Implementer、Tester）による開発プロセスの検証

### 解決したい課題
- 現状: FlaskベースのWebアプリケーション（GUI操作が必要）
- 課題: サーバー起動やブラウザ操作が不要な、シンプルなバッチ実行環境が欲しい
- 解決策: .exeファイルとCSVファイルを同じフォルダに配置して実行するだけで、クラスタリング結果を出力

---

## ヒアリング結果

### 主な要求事項

1. **既存のクラスタリングロジックを流用**
   - 詳細: `~/projects/excel-clustering-app` の `preprocessor.py` と `clustering.py` をそのまま使用
   - 優先度: **高**

2. **GUIなしのCLI実行**
   - 詳細: .exeファイルを実行するだけでクラスタリング処理が完了
   - 優先度: **高**

3. **設定ファイル（config.yaml）による管理**
   - 詳細: 前処理オプション、入出力設定を config.yaml で指定
   - 優先度: **高**

4. **同じフォルダのCSV自動検出**
   - 詳細: .exeと同じフォルダに配置されたCSVファイルを自動的に検出して処理
   - 優先度: **中**

5. **タイムスタンプ付き出力**
   - 詳細: 出力ファイル名に実行日時を付与（`output_clustered_YYYYMMDD_HHMMSS.csv`）
   - 優先度: **中**

### 技術要件

- **プログラミング言語**: Python 3.11
- **既存コード流用元**: `~/projects/excel-clustering-app`
  - `src/webapp/preprocessor.py`
  - `src/webapp/clustering.py`
- **データ処理**: pandas 2.1.3
- **機械学習**: scikit-learn 1.3.2 (TF-IDF, コサイン類似度, AgglomerativeClustering)
- **設定管理**: PyYAML 6.0.1
- **.exe化**: PyInstaller
- **認証**: 不要
- **デプロイ先**: ローカル実行（.exeファイル）

### 入力データ形式

**CSVファイル:**
- 列: `オーダーID`, `会社名`, `作業名称`
- エンコーディング: UTF-8 with BOM（Shift-JISも対応）
- サンプル: `~/projects/excel-clustering-app/shared/data/test_orders.csv`

**例:**
```csv
オーダーID,会社名,作業名称
ORD-00001,みらい銀行,フェーズ2／在庫管理システム／運用／5月度／支援
ORD-00002,東京システム株式会社,販売管理S-開発工程-継続-9月度-案件
```

### 処理フロー

1. **設定読み込み**: `config.yaml` から前処理オプション、入出力設定を読み込み
2. **CSV読み込み**: 同じフォルダの `.csv` ファイルを自動検出または指定
3. **前処理**: 既存の `preprocessor.py` ロジックを流用
   - 半角→全角変換
   - スペース削除
   - 時期情報除去（FY2024, 令和6年度など）
   - フェーズ情報除去（要件定義、基本設計など）
   - 記号・装飾除去
   - 略語正規化
4. **クラスタリング**: 既存の `clustering.py` ロジックを流用
   - TF-IDFベクトル化
   - コサイン類似度計算
   - 会社ごとにグルーピング
   - 階層的クラスタリング
5. **結果出力**: `output_clustered_YYYYMMDD_HHMMSS.csv` に保存

### 非機能要件

- **パフォーマンス**: 1000行のCSVを30秒以内に処理
- **エラーハンドリング**:
  - ファイルが見つからない場合: エラーメッセージ表示
  - CSV形式が不正な場合: エラーメッセージ表示
  - 処理中のエラー: ログファイルに記録
- **ログ出力**:
  - コンソールとファイルの両方にログ出力
  - ログレベル: INFO, WARNING, ERROR
- **保守性**:
  - 既存コードを流用し、メンテナンス性を確保
  - 設定ファイルで動作を変更可能

### 制約条件

- **実行環境**: Windows環境での動作を想定（.exe）
- **既存プロジェクト**: `excel-clustering-app` プロジェクトはそのまま保持（変更しない）
- **ロジック変更禁止**: 既存のクラスタリングロジックを変更しない

---

## 実行方法（完成イメージ）

**フォルダ構成:**
```
project-clustering-cli-ma/
├── clustering.exe       # 実行ファイル
├── config.yaml          # 設定ファイル
├── input.csv            # 入力ファイル（ユーザーが配置）
└── output_clustered_20260206_153000.csv  # 出力ファイル
```

**実行:**
```bash
clustering.exe
```

---

## 設定ファイル（config.yaml）

```yaml
# 前処理オプション
preprocessing:
  normalize_width: true       # 半角→全角変換
  remove_spaces: true         # スペース削除
  remove_period: true         # 時期情報除去
  remove_phase: true          # フェーズ情報除去
  remove_symbols: true        # 記号・装飾除去
  normalize_abbreviations: false  # 略語正規化

# 入出力設定
io:
  input_file: ""              # 入力ファイル名（空の場合は自動検出）
  output_prefix: "output_clustered"  # 出力ファイル接頭辞
  output_timestamp: true      # タイムスタンプ付与

# クラスタリング設定
clustering:
  # 企業ごとのクラスタ数設定（設定なしの場合は自動計算）
  # オフセットモード: 文字列で "+2" や "-1"（自動計算値からの増減）
  # 固定モード: 数値で 7（クラスタ数を強制）
  company_cluster_settings:
    "みらい銀行": "+2"          # 自動計算値 + 2
    "東京システム株式会社": 7    # 固定で7クラスタ
    "ABC株式会社": "-1"         # 自動計算値 - 1

# ログ設定
logging:
  console: true
  file: true
  file_path: "clustering.log"
  level: "INFO"
```

---

## 出力形式

**既存アプリと同じ形式:**
- 元のCSV列 + `クラスタID` 列 + `代表名` 列
- UTF-8 with BOM
- 会社ごとにクラスタリング

**出力例:**
```csv
オーダーID,会社名,作業名称,クラスタID,代表名
ORD-00001,みらい銀行,フェーズ2／在庫管理システム／運用／5月度／支援,1,在庫管理システム
ORD-00015,みらい銀行,バージョンアップ/EDI連携/基設/6月度/プロジェクト,2,EDI連携
```

---

## ユーザー情報

### 想定ユーザー
- データ分析担当者
- 社内の非エンジニア

### 利用シーン
- 受注データのプロジェクト名表記揺れを定期的にチェック
- サーバー起動なしで、手元で簡単にクラスタリングを実行

---

## マルチエージェント開発プロセス（このプロジェクト固有）

このプロジェクトは、マルチエージェント体制での開発を実験的に実施します。

### 開発体制

```
Manager（プロジェクトマネージャー）
  ├── Requirements Analyst SubAgent（要件定義専門家）
  ├── Designer SubAgent（設計者）
  ├── Implementer SubAgent（実装者）
  └── Tester SubAgent（テスター）
```

### 期待される効果

1. **役割の明確化**
   - 各SubAgentが専門領域に集中
   - 責任範囲が明確

2. **独立した視点**
   - SubAgent間は完全に独立
   - バイアスを防止

3. **品質向上**
   - 各フェーズで専門的なレビュー
   - ドキュメントの充実

4. **開発効率**
   - 並列実行可能
   - プロセスの可視化

---

## 次のステップ

### Manager への依頼事項

**⚠️ マルチエージェント体制での開発を実施してください**

1. **Requirements Analyst SubAgent に委譲**
   - この initial-requirements.md を基に、詳細な要件定義を実施
   - 不明点があればユーザーに確認（AskUserQuestion）
   - `docs/requirements.md` を作成

2. **要件定義完了後**
   - Designer SubAgent で設計書作成
   - `docs/specification.md` を作成

3. **設計完了後**
   - Implementer SubAgent でコード実装
   - `src/` 配下にコードを実装

4. **実装完了後**
   - Tester SubAgent でテスト実行
   - テスト結果をレポート

5. **WBS作成**
   - 要件定義 v1.0 完成時に `docs/wbs.md` を作成
   - タスク分解、マイルストーン設定

### 推奨される最初の指示

```
"docs/handoff/initial-requirements.md を確認してください。
Requirements Analyst SubAgentで、この内容を基に詳細な要件定義を開始してください。
不明点があればユーザーに質問して明確化してください。"
```

---

## 備考

### 既存プロジェクトの参照先
- `~/projects/excel-clustering-app/src/webapp/preprocessor.py`
- `~/projects/excel-clustering-app/src/webapp/clustering.py`
- `~/projects/excel-clustering-app/shared/data/test_orders.csv`（テストデータ）

### 参考プロジェクト
- `~/projects/project-clustering-cli` - 同じ機能要件の先行プロジェクト

### 流用するコードの責任範囲
- **前処理ロジック**: そのまま流用
- **クラスタリングロジック**: そのまま流用
- **Flask Webアプリ部分**: 使用しない

---

**このドキュメントについて:**
- このファイルはホストOSでのヒアリング結果を記録したものです
- Dev Container内のManagerは、このファイルを起点に開発を開始してください
- 詳細な要件定義は Requirements Analyst SubAgent が `docs/requirements.md` に作成します
- このファイルは初期情報として保持し、要件変更時の参照用としてください
- **マルチエージェント体制での開発プロセスを実践してください**
