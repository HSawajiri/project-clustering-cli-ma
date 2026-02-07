"""
テキスト前処理モジュール

プロジェクト名の表記揺れを正規化
処理順序（v1.3最適化）:
1. スペース削除
2. 時期情報除去（半角のうちに）
3. フェーズ情報除去（半角のうちに）
4. 記号・装飾除去（長音記号を保護）
5. 半角→全角変換
6. 略語正規化
"""

import re
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class TextPreprocessor:
    """テキスト前処理クラス"""

    def __init__(self, config: Dict[str, Any]):
        """
        初期化

        Args:
            config: 前処理オプション（preprocessing セクション）
        """
        self.config = config
        self._compile_patterns()
        logger.info("TextPreprocessor initialized")

    def _compile_patterns(self):
        """正規表現パターンをコンパイル"""

        # 時期情報パターン（半角・全角両対応）
        self.period_patterns = [
            # 年度パターン
            r'FY\d{4}',
            r'ＦＹ\d{4}',
            r'FY\d{2}',
            r'ＦＹ\d{2}',
            r'令和\d+年度?',
            r'平成\d+年度?',
            r'令和元年度?',
            r'\d{4}年度?',
            r'\d+年度',
            # 月度パターン
            r'\d+月度',
            r'\d+月',
            # 四半期パターン
            r'\d+Q',
            r'\d+Ｑ',
            r'第\d+四半期',
            r'[1-4]Q',
            r'[１-４]Ｑ',
        ]

        # フェーズ情報パターン（半角・全角、英語・日本語）
        self.phase_patterns = [
            # 日本語フェーズ
            r'要件定義',
            r'基本設計',
            r'詳細設計',
            r'外部設計',
            r'内部設計',
            r'開発',
            r'実装',
            r'製造',
            r'プログラミング',
            r'単体テスト',
            r'結合テスト',
            r'総合テスト',
            r'システムテスト',
            r'受入テスト',
            r'テスト',
            r'移行',
            r'リリース',
            r'保守',
            r'運用',
            r'運用保守',
            r'PMO',
            r'プロジェクト管理',
            # 英語・略称
            r'RequirementDefinition',
            r'Requirement',
            r'BasicDesign',
            r'DetailedDesign',
            r'Design',
            r'Development',
            r'Implementation',
            r'Programming',
            r'Coding',
            r'UnitTest',
            r'IntegrationTest',
            r'SystemTest',
            r'Test',
            r'Migration',
            r'Maintenance',
            r'Operation',
            r'O&M',
            # 略称（フェーズ）
            r'要[件定]',
            r'基[本設]',
            r'詳[細設]',
            r'外[部設]',
            r'内[部設]',
            r'BD',
            r'DD',
            r'PG',
            r'ST',
            r'IT',
            r'UT',
            # フェーズ番号
            r'フェーズ\d+',
            r'Phase\d+',
            r'P\d+',
        ]

        # 記号・装飾パターン（長音記号「ー」を除外）
        self.symbol_pattern = r'[／/\-－―‐\【】\[\]\(\)（）「」『』、。，．,\.\s]+'

        # 略語正規化マップ
        self.abbreviation_map = {
            'S': 'システム',
            'ｓ': 'システム',
            's': 'システム',
            'SYS': 'システム',
            'Sys': 'システム',
            'HR': '人事',
            'ＨＲ': '人事',
            'CRM': '顧客管理',
            'ＣＲＭ': '顧客管理',
            'ERP': '統合基幹',
            'ＥＲＰ': '統合基幹',
            'SCM': '供給管理',
            'ＳＣＭ': '供給管理',
            'WMS': '倉庫管理',
            'ＷＭＳ': '倉庫管理',
            'BPR': '業務改革',
            'ＢＰＲ': '業務改革',
            'RPA': '自動化',
            'ＲＰＡ': '自動化',
            'AI': '人工知能',
            'ＡＩ': '人工知能',
            'ML': '機械学習',
            'ＭＬ': '機械学習',
            'IoT': 'モノのインターネット',
            'ＩｏＴ': 'モノのインターネット',
            'API': 'インターフェース',
            'ＡＰＩ': 'インターフェース',
            'DB': 'データベース',
            'ＤＢ': 'データベース',
            'Web': 'ウェブ',
            'ＷＥＢ': 'ウェブ',
            'WEB': 'ウェブ',
            'App': 'アプリ',
            'ＡＰＰ': 'アプリ',
            'APP': 'アプリ',
        }

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
        if not isinstance(text, str):
            return ""

        result = text

        # 1. スペース削除
        if self.config.get('remove_spaces', True):
            result = self._remove_spaces(result)

        # 2. 時期情報除去（半角のうちに実行）
        if self.config.get('remove_period', True):
            result = self._remove_period(result)

        # 3. フェーズ情報除去（半角のうちに実行）
        if self.config.get('remove_phase', True):
            result = self._remove_phase(result)

        # 4. 記号・装飾除去（長音記号を保護）
        if self.config.get('remove_symbols', True):
            result = self._remove_symbols(result)

        # 5. 半角→全角変換
        if self.config.get('normalize_width', True):
            result = self._normalize_width(result)

        # 6. 略語正規化
        if self.config.get('normalize_abbreviations', False):
            result = self._normalize_abbreviations(result)

        return result

    def _remove_spaces(self, text: str) -> str:
        """全角・半角スペースを削除"""
        return re.sub(r'[ 　]+', '', text)

    def _remove_period(self, text: str) -> str:
        """時期情報を除去"""
        result = text
        for pattern in self.period_patterns:
            result = re.sub(pattern, '', result, flags=re.IGNORECASE)
        return result

    def _remove_phase(self, text: str) -> str:
        """フェーズ情報を除去"""
        result = text
        for pattern in self.phase_patterns:
            result = re.sub(pattern, '', result, flags=re.IGNORECASE)
        return result

    def _remove_symbols(self, text: str) -> str:
        """記号・装飾を除去（長音記号「ー」は保護）"""
        return re.sub(self.symbol_pattern, '', text)

    def _normalize_width(self, text: str) -> str:
        """半角→全角変換"""
        # 半角英数字・記号を全角に変換
        result = []
        for char in text:
            code = ord(char)
            # 半角英数字・記号の範囲（0x21-0x7E）を全角に変換
            if 0x21 <= code <= 0x7E:
                result.append(chr(code + 0xFEE0))
            else:
                result.append(char)
        return ''.join(result)

    def _normalize_abbreviations(self, text: str) -> str:
        """略語を正規化"""
        result = text
        for abbr, full in self.abbreviation_map.items():
            # 単語境界でマッチング（前後に英数字がない）
            pattern = r'\b' + re.escape(abbr) + r'\b'
            result = re.sub(pattern, full, result)
        return result

    def preprocess_batch(self, texts: list) -> list:
        """
        複数のテキストを一括前処理

        Args:
            texts: テキストのリスト

        Returns:
            正規化されたテキストのリスト
        """
        logger.info(f"前処理開始: {len(texts)}件")
        results = [self.preprocess(text) for text in texts]
        logger.info(f"前処理完了: {len(results)}件")
        return results
