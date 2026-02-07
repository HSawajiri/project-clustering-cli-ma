"""
CSV入出力モジュール

CSV自動検出、エンコーディング判定、データフレーム読み込み・書き込みを担当
"""

import logging
from pathlib import Path
from typing import Optional
from datetime import datetime
import pandas as pd

logger = logging.getLogger(__name__)

# 必須列
REQUIRED_COLUMNS = ["オーダーID", "会社名", "作業名称"]


class CSVReader:
    """CSV読み込み・書き込みクラス"""

    @staticmethod
    def auto_detect_csv(folder: Path) -> Optional[Path]:
        """
        フォルダ内のCSVファイルを自動検出

        Args:
            folder: 検索対象フォルダ

        Returns:
            最初に見つかったCSVファイルパス、または None
        """
        folder = Path(folder)
        if not folder.exists() or not folder.is_dir():
            logger.warning(f"フォルダが存在しません: {folder}")
            return None

        csv_files = list(folder.glob("*.csv"))
        if not csv_files:
            logger.warning(f"CSVファイルが見つかりません: {folder}")
            return None

        # 最初に見つかったCSVファイルを返す
        csv_file = csv_files[0]
        logger.info(f"CSVファイルを自動検出: {csv_file.name}")

        if len(csv_files) > 1:
            logger.warning(f"複数のCSVファイルが存在します。{csv_file.name}を使用します。")

        return csv_file

    @staticmethod
    def detect_encoding(file_path: Path) -> str:
        """
        CSVのエンコーディングを自動判定

        Args:
            file_path: CSVファイルパス

        Returns:
            "utf-8-sig" or "shift-jis"
        """
        file_path = Path(file_path)

        # BOMチェック（UTF-8 with BOM）
        with open(file_path, 'rb') as f:
            first_bytes = f.read(3)
            if first_bytes == b'\xef\xbb\xbf':
                logger.info("エンコーディング判定: UTF-8 with BOM")
                return "utf-8-sig"

        # Shift-JISを試行
        try:
            with open(file_path, 'r', encoding='shift-jis') as f:
                f.read(1024)  # 最初の1024文字を読んでみる
            logger.info("エンコーディング判定: Shift-JIS")
            return "shift-jis"
        except UnicodeDecodeError:
            pass

        # デフォルトはUTF-8
        logger.info("エンコーディング判定: UTF-8（デフォルト）")
        return "utf-8"

    @staticmethod
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
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"入力ファイルが見つかりません: {file_path}")

        # エンコーディング自動判定
        if encoding is None:
            encoding = CSVReader.detect_encoding(file_path)

        # CSV読み込み
        logger.info(f"CSV読み込み開始: {file_path.name}")
        df = pd.read_csv(file_path, encoding=encoding)

        logger.info(f"CSV読み込み完了: {len(df)}行, {len(df.columns)}列")

        # 必須列検証
        CSVReader.validate_columns(df)

        return df

    @staticmethod
    def validate_columns(df: pd.DataFrame) -> None:
        """
        必須列の存在チェック

        Args:
            df: データフレーム

        Raises:
            KeyError: 必須列（オーダーID、会社名、作業名称）が存在しない
        """
        missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]

        if missing_columns:
            error_msg = f"必須列が存在しません: {', '.join(missing_columns)}"
            logger.error(error_msg)
            logger.error(f"必要な列: {', '.join(REQUIRED_COLUMNS)}")
            raise KeyError(error_msg)

        logger.info("必須列の検証: OK")

    @staticmethod
    def write_csv(
        df: pd.DataFrame,
        output_prefix: str,
        add_timestamp: bool = True,
        output_folder: Path = None
    ) -> Path:
        """
        CSVを出力

        Args:
            df: データフレーム
            output_prefix: 出力ファイル接頭辞
            add_timestamp: タイムスタンプ付与（YYYYMMDD_HHMMSS）
            output_folder: 出力フォルダ（Noneの場合はカレントディレクトリ）

        Returns:
            出力ファイルパス
        """
        if output_folder is None:
            output_folder = Path.cwd()
        else:
            output_folder = Path(output_folder)
            output_folder.mkdir(parents=True, exist_ok=True)

        # ファイル名生成
        if add_timestamp:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{output_prefix}_{timestamp}.csv"
        else:
            filename = f"{output_prefix}.csv"

        output_path = output_folder / filename

        # CSV出力（UTF-8 with BOM）
        logger.info(f"CSV出力開始: {filename}")
        df.to_csv(output_path, index=False, encoding="utf-8-sig")
        logger.info(f"CSV出力完了: {len(df)}行, {len(df.columns)}列")

        return output_path
