# 技術仕様書

**バージョン:** 1.0
**作成日:** 2026-02-06
**最終更新日:** 2026-02-06

---

## 1. システム概要

### 1.1 システム名
プロジェクト名クラスタリング CLI ツール（project-clustering-cli-ma）

### 1.2 目的
受注データのプロジェクト名表記揺れを検出し、TF-IDF + コサイン類似度によるクラスタリングを行う、コマンドライン実行可能なバッチ処理ツールを提供する。

### 1.3 システム構成図

```
┌─────────────────────────────────────────────────────┐
│           clustering.exe (PyInstaller)              │
│  ┌───────────────────────────────────────────────┐  │
│  │  main.py (Entry Point)                        │  │
│  │  ↓                                             │  │
│  │  config_handler.py (Config Management)        │  │
│  │  ↓                                             │  │
│  │  csv_reader.py (CSV I/O)                      │  │
│  │  ↓                                             │  │
│  │  preprocessor.py (Text Normalization)         │  │
│  │  ↓                                             │  │
│  │  clustering.py (ML Clustering)                │  │
│  │  ↓                                             │  │
│  │  logger.py (Logging)                          │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
          ↑                              ↓
    config.yaml                    output CSV
    input.csv                      clustering.log
```

---

## 2. 技術スタック

### 2.1 プログラミング言語
- **Python:** 3.11+
- **理由:** 既存コード（preprocessor.py, clustering.py）がPython 3.11で実装されているため

### 2.2 主要ライブラリ

| ライブラリ | バージョン | 用途 |
|----------|----------|------|
| pandas | 2.1.3 | CSV読み込み、データフレーム操作 |
| numpy | 1.26.2 | 数値計算、配列操作 |
| scikit-learn | 1.3.2 | TF-IDF、コサイン類似度、階層的クラスタリング |
| PyYAML | 6.0.1 | config.yaml読み込み |
| PyInstaller | 最新版 | .exe化 |

**バージョン固定の理由:** 既存の `excel-clustering-app` と同じバージョンを使用し、ロジック互換性を保証する

### 2.3 ビルド・実行環境

| 項目 | 内容 |
|------|------|
| 開発環境 | VS Code + Dev Container (Debian) |
| ビルド環境 | Python 3.11 + PyInstaller |
| 実行環境 | Windows OS (Pythonインストール不要) |
| パッケージ形式 | 単一の.exeファイル (ワンファイル形式) |

### 2.4 その他

| 項目 | 内容 |
|------|------|
| バージョン管理 | Git / GitHub |
| エンコーディング | UTF-8 with BOM (入出力CSV) |
| ログ形式 | テキストファイル + コンソール出力 |

---

## 3. アーキテクチャ設計

### 3.1 全体アーキテクチャ

**アーキテクチャパターン:** レイヤードアーキテクチャ（3層構造）

```
┌─────────────────────────────────────┐
│  Presentation Layer (CLI)           │  コマンドライン入出力
│  - main.py                          │
├─────────────────────────────────────┤
│  Business Logic Layer               │  ビジネスロジック
│  - preprocessor.py                  │
│  - clustering.py                    │
├─────────────────────────────────────┤
│  Infrastructure Layer               │  基盤サービス
│  - config_handler.py                │
│  - csv_reader.py                    │
│  - logger.py                        │
└─────────────────────────────────────┘
```

### 3.2 処理フロー

```
[開始] clustering.exe実行
  ↓
[1. 初期化]
  - ロガー設定（logger.py）
  - config.yaml読み込み（config_handler.py）
  ↓
[2. 入力データ読み込み]
  - CSV自動検出または指定読み込み（csv_reader.py）
  - エンコーディング自動判定（UTF-8 BOM / Shift-JIS）
  - 必須列検証（オーダーID、会社名、作業名称）
  ↓
[3. 前処理]
  - preprocessor.py の TextPreprocessor クラス使用
  - 処理順序（最適化済み）:
    1. スペース削除
    2. 時期情報除去（半角のうちに実行）
    3. フェーズ情報除去（半角のうちに実行）
    4. 記号・装飾除去（長音記号を保護）
    5. 半角→全角変換
    6. 略語正規化
  ↓
[4. クラスタリング]
  - clustering.py の DataClustering クラス使用
  - 会社ごとにグルーピング
  - TF-IDFベクトル化
  - コサイン類似度計算
  - 階層的クラスタリング（AgglomerativeClustering）
  - クラスタ数決定:
    - デフォルト: calculate_default_clusters() で自動計算
    - オフセットモード: "+2", "-1" などの文字列指定
    - 固定モード: 7 などの数値指定
  ↓
[5. 結果出力]
  - クラスタID・代表名をデータフレームに追加
  - CSV出力（UTF-8 with BOM）
  - ファイル名: {prefix}_YYYYMMDD_HHMMSS.csv
  ↓
[終了] ログ出力、処理完了メッセージ
```

### 3.3 ディレクトリ構成

```
project-clustering-cli-ma/
├── CLAUDE.md                # プロジェクト指示書
├── README.md                # ユーザー向けドキュメント
├── requirements.txt         # Python依存関係
├── config.yaml              # 設定ファイル（デフォルト）
├── build.spec               # PyInstaller設定（作成予定）
├── build.sh                 # ビルドスクリプト（作成予定）
├── .gitignore               # Git除外設定
│
├── docs/                    # ドキュメント
│   ├── requirements.md      # 要件定義書 v1.3
│   ├── specification.md     # 本ドキュメント
│   ├── wbs.md               # WBS・進捗管理
│   ├── reports/
│   │   └── cost-report.md   # コストレポート
│   └── handoff/             # SubAgent間ハンドオフ
│       └── *.md
│
├── src/                     # ソースコード
│   ├── main.py              # エントリーポイント
│   ├── config_handler.py    # 設定管理（既存）
│   ├── logger.py            # ロギング（既存）
│   ├── csv_reader.py        # CSV入出力（作成予定）
│   ├── preprocessor.py      # 前処理（流用）
│   └── clustering.py        # クラスタリング（流用）
│
├── tests/                   # テストコード（作成予定）
│   ├── test_config_handler.py
│   ├── test_csv_reader.py
│   ├── test_preprocessor.py
│   └── test_clustering.py
│
└── shared/                  # 共有データ
    └── data/
        └── test_orders.csv  # テストデータ
```

**配布時のフォルダ構成:**
```
clustering_distribution/
├── clustering.exe           # 実行ファイル
├── config.yaml              # 設定ファイル（ユーザーが編集可能）
├── input.csv                # 入力ファイル（ユーザーが配置）
├── output_clustered_20260206_153000.csv  # 出力ファイル
└── clustering.log           # ログファイル
```

---

## 4. モジュール設計

### 4.1 main.py（エントリーポイント）

**責務:**
- コマンドライン引数の解析（argparse）
- 全体の処理フロー制御
- エラーハンドリング
- 終了コードの返却

**主要関数:**

```python
def main() -> int:
    """
    メイン処理

    Returns:
        int: 終了コード（0: 成功, 1以上: エラー）
    """
    # 1. ロガー初期化
    # 2. config.yaml読み込み
    # 3. CSV読み込み
    # 4. 前処理実行
    # 5. クラスタリング実行
    # 6. 結果出力
    # 7. 完了ログ出力
```

**コマンドライン引数:**

| 引数 | 説明 | デフォルト |
|------|------|----------|
| `--config` | 設定ファイルパス | `./config.yaml` |
| `--input` | 入力CSVファイルパス | config.yamlで指定、または自動検出 |
| `--output` | 出力CSVファイルパス | config.yamlで指定 |
| `--help` | ヘルプメッセージ表示 | - |

**エラーハンドリング:**
- FileNotFoundError: ファイルが見つからない
- ValueError: 設定値が不正
- KeyError: 必須列が存在しない
- Exception: 予期しないエラー（スタックトレース出力）

---

### 4.2 config_handler.py（設定管理）

**責務:**
- config.yaml の読み込み
- 設定値の検証
- 階層構造アクセス（ドット記法）

**既存実装:** あり（流用可能）

**主要クラス:**

```python
class ConfigHandler:
    """設定ファイルハンドラー"""

    def __init__(self, config_path: Path)
    def get(self, key: str, default: Any = None) -> Any
    def get_all(self) -> Dict[str, Any]
    def reload(self)
```

**使用例:**
```python
config = ConfigHandler("config.yaml")
remove_spaces = config.get("preprocessing.remove_spaces", True)
```

---

### 4.3 logger.py（ロギング）

**責務:**
- ロガーの初期化
- コンソール・ファイル出力の設定
- ログレベル管理

**既存実装:** あり（流用可能）

**主要関数:**

```python
def setup_logger(
    name: str,
    log_file: Path = None,
    level: int = logging.INFO
) -> logging.Logger
```

**ログフォーマット:**
```
2026-02-06 15:30:00 - module_name - INFO - Processing started
```

**ログレベル:**
- INFO: 通常動作（処理開始、完了、進捗）
- WARNING: 警告（設定値の自動補正など）
- ERROR: エラー（処理中断、データ不正）

---

### 4.4 csv_reader.py（CSV入出力）

**責務:**
- CSV自動検出（.exeと同じフォルダ内）
- エンコーディング自動判定（UTF-8 BOM / Shift-JIS）
- データフレーム読み込み・書き込み
- 必須列検証

**新規作成:** 必要

**主要クラス:**

```python
class CSVReader:
    """CSV読み込みクラス"""

    def auto_detect_csv(folder: Path) -> Optional[Path]:
        """
        フォルダ内のCSVファイルを自動検出

        Args:
            folder: 検索対象フォルダ

        Returns:
            最初に見つかったCSVファイルパス、または None
        """

    def detect_encoding(file_path: Path) -> str:
        """
        CSVのエンコーディングを自動判定

        Args:
            file_path: CSVファイルパス

        Returns:
            "utf-8-sig" or "shift-jis"
        """

    def read_csv(file_path: Path, encoding: str = None) -> pd.DataFrame:
        """
        CSVを読み込み

        Args:
            file_path: CSVファイルパス
            encoding: エンコーディング（Noneの場合は自動判定）

        Returns:
            データフレーム

        Raises:
            FileNotFoundError: ファイルが存在しない
            KeyError: 必須列が存在しない
        """

    def validate_columns(df: pd.DataFrame) -> None:
        """
        必須列の存在チェック

        Args:
            df: データフレーム

        Raises:
            KeyError: 必須列（オーダーID、会社名、作業名称）が存在しない
        """

    def write_csv(
        df: pd.DataFrame,
        output_prefix: str,
        add_timestamp: bool = True
    ) -> Path:
        """
        CSVを出力

        Args:
            df: データフレーム
            output_prefix: 出力ファイル接頭辞
            add_timestamp: タイムスタンプ付与（YYYYMMDD_HHMMSS）

        Returns:
            出力ファイルパス
        """
```

**エンコーディング判定ロジック:**
1. UTF-8 with BOM（BOMマーカー検出）
2. Shift-JIS（BOMなし、デコード試行）
3. UTF-8（フォールバック）

---

### 4.5 preprocessor.py（前処理）

**責務:**
- テキストの正規化
- 時期・フェーズ情報の除去
- 略語の正規化

**既存実装:** `~/projects/excel-clustering-app/src/webapp/preprocessor.py` から流用

**重要:** ロジックを変更せず、そのままコピーする

**主要クラス:**

```python
class TextPreprocessor:
    """テキスト前処理クラス"""

    def __init__(self, config: dict):
        """
        Args:
            config: 前処理オプション（preprocessing セクション）
        """

    def preprocess(self, text: str) -> str:
        """
        テキスト前処理（処理順序v1.3対応）

        処理順序:
        1. スペース削除（remove_spaces）
        2. 時期情報除去（remove_period）※半角のうちに実行
        3. フェーズ情報除去（remove_phase）※半角のうちに実行
        4. 記号・装飾除去（remove_symbols）※長音記号を保護
        5. 半角→全角変換（normalize_width）
        6. 略語正規化（normalize_abbreviations）

        Args:
            text: 元のテキスト

        Returns:
            正規化されたテキスト
        """
```

**前処理パターン（要件定義書 v1.3 準拠）:**
- 時期: FY2024, ＦＹ２０２４, 令和6年度, 5月度, １Ｑ, 第1四半期
- フェーズ: 要件定義, 基本設計, 詳細設計, 開発, テスト, 移行, 保守, 運用, PMO
- 英語・略称: RequirementDefinition, BD, DD, PG, ST, IT, O&M

**長音記号の保護:**
- 記号除去パターンから「ー」を除外
- カタカナ語（バージョン、フェーズ等）が破壊されないようにする

---

### 4.6 clustering.py（クラスタリング）

**責務:**
- TF-IDFベクトル化
- コサイン類似度計算
- 階層的クラスタリング
- クラスタID・代表名の付与

**既存実装:** `~/projects/excel-clustering-app/src/webapp/clustering.py` から流用

**重要:** ロジックを変更せず、そのままコピーする

**主要クラス:**

```python
class DataClustering:
    """クラスタリングクラス"""

    def __init__(self, config: dict):
        """
        Args:
            config: クラスタリング設定（clustering セクション）
        """

    def calculate_default_clusters(
        self,
        distance_threshold: float,
        linkages: np.ndarray
    ) -> int:
        """
        デフォルトクラスタ数を自動計算

        デンドログラムの距離増加率から最適なクラスタ数を決定
        制約: 2 〜 データ件数 * 0.5

        Args:
            distance_threshold: 距離閾値
            linkages: 階層的クラスタリング結果

        Returns:
            クラスタ数
        """

    def get_cluster_count(
        self,
        company: str,
        default_count: int
    ) -> int:
        """
        企業ごとのクラスタ数を取得（FR-007対応）

        Args:
            company: 企業名
            default_count: デフォルトクラスタ数

        Returns:
            調整後のクラスタ数

        処理:
        1. config["clustering"]["company_cluster_settings"] を参照
        2. 企業名が設定されている場合:
           - 文字列（"+2", "-1"）→ オフセットモード
           - 数値（7）→ 固定モード
        3. 設定がない場合: default_count をそのまま使用
        4. 最終的なクラスタ数を 1 以上に制御
        """

    def cluster_by_company(
        self,
        df: pd.DataFrame,
        text_column: str
    ) -> pd.DataFrame:
        """
        会社ごとにクラスタリングを実行

        Args:
            df: データフレーム
            text_column: クラスタリング対象列（前処理済みテキスト）

        Returns:
            クラスタID・代表名が追加されたデータフレーム

        処理:
        1. 会社ごとにグルーピング
        2. TF-IDFベクトル化
        3. コサイン類似度計算
        4. AgglomerativeClustering実行
        5. クラスタ数決定（自動計算 or 設定値）
        6. クラスタID・代表名付与
        """
```

**クラスタ数決定ロジック（FR-007）:**

```python
# 例: みらい銀行の場合
default_count = calculate_default_clusters(...)  # 例: 5
setting = config["clustering"]["company_cluster_settings"].get("みらい銀行")

if setting is None:
    final_count = default_count  # 5
elif isinstance(setting, str):
    # オフセットモード
    if setting.startswith("+"):
        final_count = default_count + int(setting[1:])  # 5 + 2 = 7
    elif setting.startswith("-"):
        final_count = default_count - int(setting[1:])  # 5 - 1 = 4
else:
    # 固定モード
    final_count = int(setting)  # 7

# 制約: 1以上
final_count = max(1, final_count)
```

---

## 5. データ設計

### 5.1 データモデル

#### 5.1.1 入力データ（CSV）

**必須列:**

| 列名 | データ型 | 説明 | 例 |
|------|---------|------|-----|
| オーダーID | str | 注文識別子 | ORD-00001 |
| 会社名 | str | 顧客企業名 | みらい銀行 |
| 作業名称 | str | プロジェクト名（表記揺れあり） | フェーズ2／在庫管理システム／運用／5月度／支援 |

**その他の列:** 任意（出力時にそのまま保持）

#### 5.1.2 中間データ

**前処理後のデータフレーム:**

| 列名 | データ型 | 説明 |
|------|---------|------|
| オーダーID | str | 元の列 |
| 会社名 | str | 元の列 |
| 作業名称 | str | 元の列 |
| 正規化テキスト | str | 前処理後のテキスト（新規追加） |

**例:**
- 元のテキスト: `フェーズ2／在庫管理システム／運用／5月度／支援`
- 正規化後: `在庫管理システム運用支援`

#### 5.1.3 出力データ（CSV）

**追加列:**

| 列名 | データ型 | 説明 | 例 |
|------|---------|------|-----|
| クラスタID | int | クラスタ識別番号（会社ごとに1から連番） | 1 |
| 代表名 | str | クラスタ内で最頻出の作業名称 | 在庫管理システム |

**出力形式:**
```csv
オーダーID,会社名,作業名称,クラスタID,代表名
ORD-00001,みらい銀行,フェーズ2／在庫管理システム／運用／5月度／支援,1,在庫管理システム
ORD-00015,みらい銀行,バージョンアップ/EDI連携/基設/6月度/プロジェクト,2,EDI連携
```

---

## 6. 設定仕様（config.yaml）

### 6.1 設定ファイル構造

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
  company_cluster_settings:
    "みらい銀行": "+2"          # 自動計算値 + 2
    "東京システム株式会社": 7    # 固定で7クラスタ
    "ABC株式会社": "-1"         # 自動計算値 - 1

# ログ設定
logging:
  console: true
  file: true
  file_path: "clustering.log"
  level: "INFO"                # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### 6.2 設定項目詳細

#### preprocessing（前処理オプション）

| キー | 型 | デフォルト | 説明 |
|------|-----|----------|------|
| normalize_width | bool | true | 半角→全角変換を実行 |
| remove_spaces | bool | true | 全角・半角スペースを削除 |
| remove_period | bool | true | 時期情報（FY2024等）を削除 |
| remove_phase | bool | true | フェーズ情報（要件定義等）を削除 |
| remove_symbols | bool | true | 記号・装飾を削除（長音記号は保護） |
| normalize_abbreviations | bool | false | 略語を正規化（S→システム等） |

#### io（入出力設定）

| キー | 型 | デフォルト | 説明 |
|------|-----|----------|------|
| input_file | str | "" | 入力ファイル名。空の場合は自動検出 |
| output_prefix | str | "output_clustered" | 出力ファイル接頭辞 |
| output_timestamp | bool | true | タイムスタンプ付与（YYYYMMDD_HHMMSS） |

#### clustering（クラスタリング設定）

| キー | 型 | デフォルト | 説明 |
|------|-----|----------|------|
| company_cluster_settings | dict | {} | 企業別クラスタ数設定（詳細は FR-007 参照） |

#### logging（ログ設定）

| キー | 型 | デフォルト | 説明 |
|------|-----|----------|------|
| console | bool | true | コンソール出力を有効化 |
| file | bool | true | ファイル出力を有効化 |
| file_path | str | "clustering.log" | ログファイルパス |
| level | str | "INFO" | ログレベル（DEBUG/INFO/WARNING/ERROR/CRITICAL） |

### 6.3 デフォルト設定の動作

config.yamlが存在しない場合は、上記のデフォルト値で動作する。

---

## 7. エラーハンドリング戦略

### 7.1 エラー分類

| エラー種別 | 対応方針 | ログレベル | 終了コード |
|----------|---------|----------|----------|
| ファイル関連 | エラーメッセージを表示し終了 | ERROR | 1 |
| CSV形式不正 | エラーメッセージを表示し終了 | ERROR | 1 |
| 設定値不正 | エラーメッセージを表示し終了 | ERROR | 1 |
| 処理中エラー | スタックトレースをログ出力し終了 | ERROR | 1 |
| 警告レベル | 警告メッセージを表示し処理継続 | WARNING | 0 |

### 7.2 具体的なエラーハンドリング

#### ファイル関連エラー

```python
try:
    df = csv_reader.read_csv(input_file)
except FileNotFoundError as e:
    logger.error(f"入力ファイルが見つかりません: {input_file}")
    return 1
```

**ユーザー向けメッセージ:**
```
ERROR - 入力ファイルが見つかりません: input.csv
指定されたファイルが存在するか確認してください。
```

#### CSV形式不正エラー

```python
try:
    csv_reader.validate_columns(df)
except KeyError as e:
    logger.error(f"必須列が存在しません: {e}")
    logger.error("必要な列: オーダーID, 会社名, 作業名称")
    return 1
```

**ユーザー向けメッセージ:**
```
ERROR - 必須列が存在しません: 作業名称
必要な列: オーダーID, 会社名, 作業名称
CSVファイルのヘッダーを確認してください。
```

#### 設定値不正エラー

```python
try:
    log_level = config.get("logging.level", "INFO")
    if log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        raise ValueError(f"不正なログレベル: {log_level}")
except ValueError as e:
    logger.error(str(e))
    return 1
```

### 7.3 ログ出力例

**正常処理:**
```
2026-02-06 15:30:00 - main - INFO - ============================================================
2026-02-06 15:30:00 - main - INFO - プロジェクト名クラスタリングツール Starting
2026-02-06 15:30:00 - main - INFO - ============================================================
2026-02-06 15:30:01 - config_handler - INFO - Config loaded: 4 keys
2026-02-06 15:30:01 - csv_reader - INFO - CSV読み込み: input.csv (100行)
2026-02-06 15:30:02 - preprocessor - INFO - 前処理開始: 100件
2026-02-06 15:30:05 - clustering - INFO - クラスタリング開始: 3社
2026-02-06 15:30:05 - clustering - INFO - みらい銀行: 自動計算=5, 調整後=7（+2）
2026-02-06 15:30:08 - csv_reader - INFO - CSV出力: output_clustered_20260206_153000.csv
2026-02-06 15:30:08 - main - INFO - 処理が正常に完了しました
2026-02-06 15:30:08 - main - INFO - ============================================================
```

**エラー時:**
```
2026-02-06 15:30:00 - main - INFO - ============================================================
2026-02-06 15:30:00 - main - INFO - プロジェクト名クラスタリングツール Starting
2026-02-06 15:30:00 - main - INFO - ============================================================
2026-02-06 15:30:01 - csv_reader - ERROR - 入力ファイルが見つかりません: input.csv
2026-02-06 15:30:01 - main - ERROR - 処理が失敗しました
```

---

## 8. PyInstaller設定（build.spec）

### 8.1 ビルド仕様

**ファイル名:** `build.spec`

**設定内容:**

```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config.yaml', '.'),  # config.yamlを同梱
    ],
    hiddenimports=[
        'sklearn.utils._cython_blas',
        'sklearn.neighbors.typedefs',
        'sklearn.neighbors.quad_tree',
        'sklearn.tree._utils',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='clustering',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # コンソールアプリケーション
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
```

### 8.2 ビルドスクリプト（build.sh）

```bash
#!/bin/bash
# PyInstallerビルドスクリプト

echo "=== プロジェクト名クラスタリングツール ビルド開始 ==="

# 依存関係インストール
echo "依存関係をインストール中..."
pip install -r requirements.txt
pip install pyinstaller

# ビルド実行
echo "PyInstallerでビルド中..."
pyinstaller build.spec

# 完了メッセージ
echo "=== ビルド完了 ==="
echo "実行ファイル: dist/clustering.exe"
```

### 8.3 ビルド手順

```bash
# 1. ビルドスクリプトに実行権限を付与
chmod +x build.sh

# 2. ビルド実行
./build.sh

# 3. 実行ファイル確認
ls -lh dist/clustering.exe
```

### 8.4 配布パッケージ構成

```
clustering_distribution/
├── clustering.exe           # ビルドされた実行ファイル
├── config.yaml              # デフォルト設定ファイル（ユーザーが編集可能）
└── README.txt               # 使い方説明書
```

---

## 9. テスト戦略

### 9.1 テスト種別

| テスト種別 | 対象 | カバレッジ目標 | 実施者 |
|----------|------|--------------|--------|
| 単体テスト | 各モジュール | 80%以上 | Tester SubAgent |
| 結合テスト | モジュール間連携 | 主要フロー100% | Tester SubAgent |
| E2Eテスト | .exe実行 | 実データで検証 | Tester SubAgent |

### 9.2 単体テスト（pytest）

**テストファイル:**

- `tests/test_config_handler.py` - 設定管理のテスト
- `tests/test_csv_reader.py` - CSV入出力のテスト
- `tests/test_preprocessor.py` - 前処理ロジックのテスト
- `tests/test_clustering.py` - クラスタリングロジックのテスト

**テスト例（test_csv_reader.py）:**

```python
import pytest
from pathlib import Path
from src.csv_reader import CSVReader

def test_auto_detect_csv():
    """CSV自動検出のテスト"""
    folder = Path("./test_data")
    csv_path = CSVReader.auto_detect_csv(folder)
    assert csv_path is not None
    assert csv_path.suffix == ".csv"

def test_validate_columns_success():
    """必須列検証（正常系）"""
    df = pd.DataFrame({
        "オーダーID": ["ORD-001"],
        "会社名": ["テスト会社"],
        "作業名称": ["テストプロジェクト"]
    })
    CSVReader.validate_columns(df)  # エラーが発生しないこと

def test_validate_columns_error():
    """必須列検証（異常系）"""
    df = pd.DataFrame({
        "オーダーID": ["ORD-001"],
        "会社名": ["テスト会社"]
        # 作業名称が欠けている
    })
    with pytest.raises(KeyError):
        CSVReader.validate_columns(df)
```

### 9.3 E2Eテスト（実データ）

**テストデータ:** `~/projects/excel-clustering-app/shared/data/test_orders.csv`

**テストシナリオ:**

1. **正常系テスト**
   - .exeと同じフォルダにtest_orders.csvを配置
   - .exeを実行
   - 出力CSVが生成されることを確認
   - クラスタID・代表名が付与されていることを確認

2. **エラーハンドリングテスト**
   - 入力ファイルがない場合のエラーメッセージ確認
   - 必須列が欠けているCSVでエラーメッセージ確認
   - 不正なconfig.yamlでエラーメッセージ確認

3. **設定変更テスト**
   - config.yamlの前処理オプションを変更
   - 正規化結果が変化することを確認
   - 企業別クラスタ数設定を変更
   - クラスタ数が調整されることを確認

### 9.4 受け入れテスト基準

全ての機能要件（FR-001〜FR-008）と非機能要件（NFR-001〜NFR-006）が満たされていることを確認する。

**具体的なチェックリスト:**

- [ ] FR-001: UTF-8 BOMとShift-JISのCSVが読み込める
- [ ] FR-002: 前処理が設定通りに動作し、長音記号が保護される
- [ ] FR-003: クラスタリングが既存ロジックと同じ結果を出力
- [ ] FR-004: タイムスタンプ付きCSVが正しく出力される
- [ ] FR-005: config.yamlの設定が反映される
- [ ] FR-006: ログがコンソールとファイルに出力される
- [ ] FR-007: 企業別クラスタ数設定が正しく動作
- [ ] FR-008: .exeファイルがPythonなしで実行可能
- [ ] NFR-001: 1000行のCSVが30秒以内に処理完了
- [ ] NFR-006: 非エンジニアが説明書を見て実行できる

---

## 10. 変更履歴

| バージョン | 日付 | 変更内容 | 変更者 |
|-----------|------|---------|--------|
| 1.0 | 2026-02-06 | 初版作成（requirements.md v1.3を基に技術仕様書を作成） | Designer SubAgent |

---

## 11. 承認

| 役割 | 氏名 | 署名 | 日付 |
|------|------|------|------|
| システムアーキテクト | Designer SubAgent | ✅ 作成完了 | 2026-02-06 |
| プロジェクトマネージャー | Manager | ✅ 承認 | 2026-02-06 |

---

## 補足資料

### A. 既存コードの流用方針

**流用元:**
- `~/projects/excel-clustering-app/src/webapp/preprocessor.py`
- `~/projects/excel-clustering-app/src/webapp/clustering.py`

**流用方法:**
1. 既存ファイルを `src/` フォルダにコピー
2. ロジックを変更せず、そのまま使用
3. 必要に応じて import パスを調整

**禁止事項:**
- 既存のクラスタリングロジックの変更
- アルゴリズムの改良・最適化

**理由:**
- 既存アプリと同じ結果を保証するため
- 予期しない動作変更を防ぐため

### B. 処理順序の最適化（v1.3対応）

**改善内容:**
1. **半角のうちに時期・フェーズ除去を実行**
   - 理由: 半角の正規表現パターンの方がマッチ精度が高い
   - 効果: FY2024 / ＦＹ２０２４ の両方を確実に検出

2. **長音記号の保護**
   - 理由: カタカナ語（バージョン、フェーズ等）が破壊されないようにする
   - 方法: 記号除去パターンから「ー」を除外

3. **月度・四半期対応**
   - 理由: 実データに対応するため
   - 追加パターン: 5月度, １Ｑ, 第1四半期

### C. 企業別クラスタ数調整の仕様（FR-007）

**設定例:**

```yaml
clustering:
  company_cluster_settings:
    "みらい銀行": "+2"          # オフセットモード（自動 + 2）
    "東京システム株式会社": 7    # 固定モード（常に7）
    "ABC株式会社": "-1"         # オフセットモード（自動 - 1）
```

**処理フロー:**

```
企業: みらい銀行
  ↓
自動計算: 5クラスタ
  ↓
設定確認: "+2"
  ↓
オフセット適用: 5 + 2 = 7
  ↓
制約確認: max(1, 7) = 7
  ↓
最終決定: 7クラスタ
```

**ログ出力例:**

```
INFO - みらい銀行: 自動計算=5, 調整後=7（+2）
INFO - 東京システム株式会社: 自動計算=6, 調整後=7（固定）
INFO - ABC株式会社: 自動計算=8, 調整後=7（-1）
INFO - その他の会社: 自動計算=4, 調整後=4（設定なし）
```

---

**以上、技術仕様書v1.0**
