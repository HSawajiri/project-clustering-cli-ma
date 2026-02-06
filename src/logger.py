"""
ロガー設定モジュール
"""

import logging
import sys
from pathlib import Path


def setup_logger(name: str, log_file: Path = None, level: int = logging.INFO) -> logging.Logger:
    """
    ロガーをセットアップ

    Args:
        name: ロガー名（通常は __name__）
        log_file: ログファイルパス（Noneの場合は標準出力のみ）
        level: ログレベル

    Returns:
        設定済みロガー
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 既存のハンドラーをクリア（重複防止）
    if logger.hasHandlers():
        logger.handlers.clear()

    # フォーマッター
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # コンソールハンドラー
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # ファイルハンドラー（指定された場合）
    if log_file:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
