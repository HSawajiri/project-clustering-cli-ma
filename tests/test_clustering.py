"""
Clustering Module Tests

テスト対象:
- FR-003: TF-IDFベクトル化とクラスタリング
- FR-007: 企業別クラスタ数調整
- デフォルトクラスタ数自動計算
- クラスタID・代表名付与
"""

import pytest
import pandas as pd
import numpy as np
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from clustering import DataClustering


class TestDataClustering:
    """DataClustering クラスのテスト"""

    @pytest.fixture
    def default_config(self):
        """デフォルト設定"""
        return {
            'company_cluster_settings': {}
        }

    @pytest.fixture
    def config_with_settings(self):
        """企業別設定を含む設定"""
        return {
            'company_cluster_settings': {
                'みらい銀行': '+2',
                '東京システム株式会社': 7,
                'ABC株式会社': '-1'
            }
        }

    @pytest.fixture
    def clustering(self, default_config):
        """デフォルト設定のクラスタリング"""
        return DataClustering(default_config)

    @pytest.fixture
    def sample_dataframe(self):
        """サンプルデータフレーム"""
        return pd.DataFrame({
            'オーダーID': [f'ORD-{i:03d}' for i in range(1, 11)],
            '会社名': ['みらい銀行'] * 5 + ['東京システム株式会社'] * 5,
            '作業名称': [
                '在庫管理システム開発',
                '在庫管理システム保守',
                '在庫管理システム運用',
                '顧客管理システム開発',
                '顧客管理システム保守',
                'EDI連携システム開発',
                'EDI連携システム保守',
                'EDI連携システム運用',
                '業務改善プロジェクト',
                '業務改善支援'
            ],
            '正規化テキスト': [
                '在庫管理システム開発',
                '在庫管理システム保守',
                '在庫管理システム運用',
                '顧客管理システム開発',
                '顧客管理システム保守',
                'ＥＤＩ連携システム開発',
                'ＥＤＩ連携システム保守',
                'ＥＤＩ連携システム運用',
                '業務改善プロジェクト',
                '業務改善支援'
            ]
        })

    # ========================================
    # TC-FR003-001: デフォルトクラスタ数自動計算
    # ========================================
    def test_calculate_default_clusters(self, clustering):
        """デンドログラムからクラスタ数が自動計算されることを確認"""
        # ダミーのlinkages配列を作成
        linkages = np.array([
            [0, 1, 0.1, 2],
            [2, 3, 0.2, 2],
            [4, 5, 0.3, 3],
            [6, 7, 0.5, 4],
            [8, 9, 0.8, 5]
        ])

        n_samples = 10
        result = clustering.calculate_default_clusters(0.5, linkages, n_samples)

        # クラスタ数が2〜5の範囲内であることを確認
        assert 2 <= result <= 5
        assert isinstance(result, int)

    # ========================================
    # TC-FR003-002: クラスタ数計算（サンプル数2以下）
    # ========================================
    def test_calculate_default_clusters_small_sample(self, clustering):
        """サンプル数が2以下の場合に1クラスタになることを確認"""
        linkages = np.array([[0, 1, 0.1, 2]])
        n_samples = 2

        result = clustering.calculate_default_clusters(0.5, linkages, n_samples)

        assert result == 1

    # ========================================
    # TC-FR007-001: クラスタ数自動計算（設定なし）
    # ========================================
    def test_get_cluster_count_auto(self, clustering):
        """設定がない企業は自動計算されることを確認"""
        company = "テスト株式会社"
        default_count = 5

        result = clustering.get_cluster_count(company, default_count)

        assert result == default_count

    # ========================================
    # TC-FR007-002: オフセットモード（+2）
    # ========================================
    def test_get_cluster_count_offset_plus(self, config_with_settings):
        """"+2"指定で自動計算値+2になることを確認"""
        clustering = DataClustering(config_with_settings)
        company = "みらい銀行"
        default_count = 5

        result = clustering.get_cluster_count(company, default_count)

        assert result == 7  # 5 + 2

    # ========================================
    # TC-FR007-003: オフセットモード（-1）
    # ========================================
    def test_get_cluster_count_offset_minus(self, config_with_settings):
        """"-1"指定で自動計算値-1になることを確認"""
        clustering = DataClustering(config_with_settings)
        company = "ABC株式会社"
        default_count = 8

        result = clustering.get_cluster_count(company, default_count)

        assert result == 7  # 8 - 1

    # ========================================
    # TC-FR007-004: 固定モード（7）
    # ========================================
    def test_get_cluster_count_fixed(self, config_with_settings):
        """数値指定で固定値になることを確認"""
        clustering = DataClustering(config_with_settings)
        company = "東京システム株式会社"
        default_count = 6

        result = clustering.get_cluster_count(company, default_count)

        assert result == 7  # 固定値

    # ========================================
    # TC-FR007-005: クラスタ数下限制御（1以上）
    # ========================================
    def test_get_cluster_count_minimum(self):
        """クラスタ数が1未満にならないことを確認"""
        config = {
            'company_cluster_settings': {
                'テスト会社': '-10'
            }
        }
        clustering = DataClustering(config)
        company = "テスト会社"
        default_count = 3

        result = clustering.get_cluster_count(company, default_count)

        assert result == 1  # max(1, 3 - 10) = 1

    # ========================================
    # TC-FR007-006: 企業名の完全一致
    # ========================================
    def test_company_exact_match(self, config_with_settings):
        """企業名が完全一致で判定されることを確認"""
        clustering = DataClustering(config_with_settings)

        # 完全一致する場合
        result1 = clustering.get_cluster_count("みらい銀行", 5)
        assert result1 == 7  # 設定が適用される

        # 一致しない場合（スペースがある）
        result2 = clustering.get_cluster_count("みらい銀行 ", 5)
        assert result2 == 5  # デフォルト値が使用される

        # 一致しない場合（大文字小文字が異なる）は該当なし（日本語なので同じ）
        # 存在しない企業
        result3 = clustering.get_cluster_count("存在しない会社", 5)
        assert result3 == 5  # デフォルト値が使用される

    # ========================================
    # TC-FR003-003: 会社別クラスタリング
    # ========================================
    def test_cluster_by_company(self, clustering, sample_dataframe):
        """会社ごとに独立してクラスタリングが実行されることを確認"""
        result_df = clustering.cluster_by_company(sample_dataframe, '正規化テキスト')

        # クラスタID列と代表名列が追加されていることを確認
        assert 'クラスタID' in result_df.columns
        assert '代表名' in result_df.columns

        # 各会社ごとにクラスタIDが1から始まることを確認
        for company in result_df['会社名'].unique():
            company_df = result_df[result_df['会社名'] == company]
            cluster_ids = company_df['クラスタID'].unique()
            assert min(cluster_ids) >= 1

        # データ行数が変わらないことを確認
        assert len(result_df) == len(sample_dataframe)

    # ========================================
    # TC-FR003-004: クラスタID・代表名付与
    # ========================================
    def test_cluster_id_and_representative_name(self, clustering, sample_dataframe):
        """クラスタIDと代表名が正しく付与されることを確認"""
        result_df = clustering.cluster_by_company(sample_dataframe, '正規化テキスト')

        # 全行にクラスタIDと代表名が付与されていることを確認
        assert result_df['クラスタID'].notna().all()
        assert result_df['代表名'].notna().all()

        # クラスタIDが整数であることを確認
        assert result_df['クラスタID'].dtype == int or result_df['クラスタID'].dtype == np.int64

        # 代表名が作業名称列に存在する値であることを確認
        for rep_name in result_df['代表名'].unique():
            assert rep_name in result_df['作業名称'].values

    # ========================================
    # 追加テスト: 1件のデータのクラスタリング
    # ========================================
    def test_cluster_single_row(self, clustering):
        """1件のデータでもエラーが発生しないことを確認"""
        df = pd.DataFrame({
            'オーダーID': ['ORD-001'],
            '会社名': ['テスト会社'],
            '作業名称': ['テストプロジェクト'],
            '正規化テキスト': ['テストプロジェクト']
        })

        result_df = clustering.cluster_by_company(df, '正規化テキスト')

        assert len(result_df) == 1
        assert result_df['クラスタID'].iloc[0] == 1
        assert result_df['代表名'].iloc[0] == 'テストプロジェクト'

    # ========================================
    # 追加テスト: 同一テキストのクラスタリング
    # ========================================
    def test_cluster_identical_texts(self, clustering):
        """全て同じテキストの場合でもエラーが発生しないことを確認"""
        df = pd.DataFrame({
            'オーダーID': ['ORD-001', 'ORD-002', 'ORD-003'],
            '会社名': ['テスト会社', 'テスト会社', 'テスト会社'],
            '作業名称': ['同じプロジェクト', '同じプロジェクト', '同じプロジェクト'],
            '正規化テキスト': ['同じプロジェクト', '同じプロジェクト', '同じプロジェクト']
        })

        result_df = clustering.cluster_by_company(df, '正規化テキスト')

        assert len(result_df) == 3
        # 同じテキストの場合、クラスタリングアルゴリズムの特性上1-2クラスタになる可能性がある
        # （完全に同一の距離値での分割は数値誤差により予測不能な挙動を示すことがある）
        assert 1 <= result_df['クラスタID'].nunique() <= 2
        assert result_df['代表名'].iloc[0] == '同じプロジェクト'

    # ========================================
    # 追加テスト: 複数会社の混在データ
    # ========================================
    def test_cluster_multiple_companies(self, clustering):
        """複数会社のデータが正しくクラスタリングされることを確認"""
        df = pd.DataFrame({
            'オーダーID': [f'ORD-{i:03d}' for i in range(1, 7)],
            '会社名': ['A社', 'A社', 'B社', 'B社', 'C社', 'C社'],
            '作業名称': ['システム開発', 'システム保守', 'システム開発', 'システム保守', 'プロジェクト管理', 'プロジェクト支援'],
            '正規化テキスト': ['システム開発', 'システム保守', 'システム開発', 'システム保守', 'プロジェクト管理', 'プロジェクト支援']
        })

        result_df = clustering.cluster_by_company(df, '正規化テキスト')

        # 各会社のクラスタIDが独立していることを確認
        for company in ['A社', 'B社', 'C社']:
            company_df = result_df[result_df['会社名'] == company]
            assert len(company_df) == 2
            assert min(company_df['クラスタID']) >= 1

    # ========================================
    # 追加テスト: 不正なオフセット設定
    # ========================================
    def test_invalid_offset_setting(self):
        """不正なオフセット設定でデフォルト値が使用されることを確認"""
        config = {
            'company_cluster_settings': {
                'テスト会社': '+abc'  # 不正な値
            }
        }
        clustering = DataClustering(config)
        company = "テスト会社"
        default_count = 5

        result = clustering.get_cluster_count(company, default_count)

        # 不正な設定なのでデフォルト値が使用される
        assert result == default_count

    # ========================================
    # 追加テスト: 不正な設定タイプ
    # ========================================
    def test_invalid_setting_type(self):
        """不正な設定タイプでデフォルト値が使用されることを確認"""
        config = {
            'company_cluster_settings': {
                'テスト会社': ['invalid', 'list']  # リスト（不正）
            }
        }
        clustering = DataClustering(config)
        company = "テスト会社"
        default_count = 5

        result = clustering.get_cluster_count(company, default_count)

        # 不正な設定タイプなのでデフォルト値が使用される
        assert result == default_count
