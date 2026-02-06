"""
設定ファイルハンドラー

config.yaml の読み込みと検証を担当
"""

import yaml
from pathlib import Path
from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)


class ConfigHandler:
    """設定ファイルハンドラー"""

    def __init__(self, config_path: Path):
        """
        初期化

        Args:
            config_path: config.yamlのパス

        Raises:
            FileNotFoundError: 設定ファイルが見つからない
            yaml.YAMLError: YAML形式が不正
        """
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self._load()

    def _load(self):
        """設定ファイルを読み込み"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        logger.info(f"Loading config from: {self.config_path}")

        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

        if self.config is None:
            self.config = {}

        logger.info(f"Config loaded: {len(self.config)} keys")

    def get(self, key: str, default: Any = None) -> Any:
        """
        設定値を取得

        Args:
            key: 設定キー（ドット区切りで階層アクセス可能）
            default: デフォルト値

        Returns:
            設定値またはデフォルト値

        Example:
            config.get("database.host", "localhost")
        """
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def get_all(self) -> Dict[str, Any]:
        """全設定を取得"""
        return self.config.copy()

    def reload(self):
        """設定ファイルを再読み込み"""
        self._load()
