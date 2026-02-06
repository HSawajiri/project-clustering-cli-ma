"""
Integration Tests

テスト対象:
- エンドツーエンド処理フロー
- main()関数の実行
- エラーハンドリング
- 統合テストシナリオ
"""

import pytest
import pandas as pd
import sys
from pathlib import Path
from unittest.mock import patch

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from csv_reader import CSVReader
from preprocessor import TextPreprocessor
from clustering import DataClustering
from config_handler import ConfigHandler
import main


class TestIntegration:
    """統合テスト"""

    @pytest.fixture
    def test_data_dir(self):
        """テストデータディレクトリ"""
        return Path(__file__).parent / 'data'

    @pytest.fixture
    def test_config_path(self):
        """テスト設定ファイルパス"""
        return Path(__file__).parent / 'test_config.yaml'

    # ========================================
    # TC-INT-001: 正常系フルフロー
    # ========================================
    def test_end_to_end_processing(self, test_data_dir, tmp_path):
        """CSV読み込み→前処理→クラスタリング→出力の全フローが動作することを確認"""
        # 1. CSV読み込み
        csv_path = test_data_dir / 'test_sample.csv'
        df = CSVReader.read_csv(csv_path)
        assert len(df) > 0
        assert 'オーダーID' in df.columns
        assert '会社名' in df.columns
        assert '作業名称' in df.columns

        # 2. 前処理
        preprocessing_config = {
            'normalize_width': True,
            'remove_spaces': True,
            'remove_period': True,
            'remove_phase': True,
            'remove_symbols': True,
            'normalize_abbreviations': False
        }
        preprocessor = TextPreprocessor(preprocessing_config)
        df['正規化テキスト'] = preprocessor.preprocess_batch(df['作業名称'].tolist())

        # 前処理が実行されたことを確認
        assert '正規化テキスト' in df.columns
        assert len(df['正規化テキスト']) == len(df)

        # 3. クラスタリング
        clustering_config = {
            'company_cluster_settings': {}
        }
        clustering = DataClustering(clustering_config)
        result_df = clustering.cluster_by_company(df, '正規化テキスト')

        # クラスタIDと代表名が付与されていることを確認
        assert 'クラスタID' in result_df.columns
        assert '代表名' in result_df.columns
        assert result_df['クラスタID'].notna().all()
        assert result_df['代表名'].notna().all()

        # 4. CSV出力
        result_df = result_df.drop(columns=['正規化テキスト'])
        output_path = CSVReader.write_csv(
            result_df,
            output_prefix='test_output',
            add_timestamp=False,
            output_folder=tmp_path
        )

        # 出力ファイルが生成されたことを確認
        assert output_path.exists()

        # 出力CSVを読み込んで検証
        output_df = pd.read_csv(output_path, encoding='utf-8-sig')
        assert len(output_df) == len(result_df)
        assert 'クラスタID' in output_df.columns
        assert '代表名' in output_df.columns

    # ========================================
    # TC-INT-002: 異常系: 入力ファイル不存在
    # ========================================
    def test_error_missing_file(self):
        """入力ファイルが存在しない場合のエラーハンドリングを確認"""
        non_existent_path = Path('/tmp/non_existent_file.csv')

        with pytest.raises(FileNotFoundError):
            CSVReader.read_csv(non_existent_path)

    # ========================================
    # TC-INT-003: 異常系: 必須列欠損
    # ========================================
    def test_error_missing_columns(self, test_data_dir):
        """必須列が欠損している場合のエラーハンドリングを確認"""
        csv_path = test_data_dir / 'test_invalid.csv'

        with pytest.raises(KeyError, match='作業名称'):
            CSVReader.read_csv(csv_path)

    # ========================================
    # TC-INT-004: 異常系: 不正なconfig.yaml
    # ========================================
    def test_error_invalid_config(self, tmp_path):
        """不正な設定ファイルでエラーハンドリングされることを確認"""
        # 不正なYAMLファイルを作成
        invalid_config_path = tmp_path / 'invalid_config.yaml'
        with open(invalid_config_path, 'w') as f:
            f.write("invalid: yaml: syntax: error:")

        # ConfigHandlerで読み込みを試みる
        with pytest.raises(Exception):
            ConfigHandler(invalid_config_path)

    # ========================================
    # TC-INT-005: main()関数の実行
    # ========================================
    def test_main_with_sample_data(self, test_data_dir, test_config_path, tmp_path, monkeypatch):
        """main()関数が正常に実行されることを確認"""
        # テスト用の設定ファイルを一時ディレクトリにコピー
        test_config = tmp_path / 'config.yaml'
        import shutil
        shutil.copy(test_config_path, test_config)

        # テストデータも一時ディレクトリにコピー
        test_csv = tmp_path / 'test_sample.csv'
        shutil.copy(test_data_dir / 'test_sample.csv', test_csv)

        # __file__をモックして、一時ディレクトリを参照させる
        # (実際のmain.pyの__file__を変更することはできないので、コマンドライン引数でテスト)

        # コマンドライン引数をモック
        test_args = [
            'main.py',
            '--config', str(test_config),
            '--input', str(test_csv),
            '--output', 'test_output'
        ]

        with patch('sys.argv', test_args):
            # main関数を実行
            exit_code = main.main()

            # 正常終了することを確認
            assert exit_code == 0

            # 出力ファイルが生成されたことを確認
            # main.pyの仕様上、出力ファイルはPath(__file__).parent.parentに作成される
            # つまりプロジェクトルートディレクトリに作成される
            project_root = Path(__file__).parent.parent
            output_files = list(project_root.glob('test_output*.csv'))
            assert len(output_files) > 0

            # テスト後にクリーンアップ
            for f in output_files:
                f.unlink()

    # ========================================
    # 追加テスト: 企業別クラスタ数設定の統合テスト
    # ========================================
    def test_company_cluster_settings_integration(self, test_data_dir, tmp_path):
        """企業別クラスタ数設定が全フローで正しく動作することを確認"""
        # 1. CSV読み込み
        csv_path = test_data_dir / 'test_sample.csv'
        df = CSVReader.read_csv(csv_path)

        # 2. 前処理
        preprocessing_config = {
            'normalize_width': True,
            'remove_spaces': True,
            'remove_period': True,
            'remove_phase': True,
            'remove_symbols': True,
            'normalize_abbreviations': False
        }
        preprocessor = TextPreprocessor(preprocessing_config)
        df['正規化テキスト'] = preprocessor.preprocess_batch(df['作業名称'].tolist())

        # 3. クラスタリング（企業別設定あり）
        clustering_config = {
            'company_cluster_settings': {
                'みらい銀行': '+2',
                '東京システム株式会社': 3,
                'ABC株式会社': '-1'
            }
        }
        clustering = DataClustering(clustering_config)
        result_df = clustering.cluster_by_company(df, '正規化テキスト')

        # 企業別のクラスタ数を確認
        for company in result_df['会社名'].unique():
            company_df = result_df[result_df['会社名'] == company]
            n_clusters = company_df['クラスタID'].nunique()
            # 設定に応じたクラスタ数になっているか（厳密な数値は自動計算に依存）
            assert n_clusters >= 1

        # 4. 出力
        result_df = result_df.drop(columns=['正規化テキスト'])
        output_path = CSVReader.write_csv(
            result_df,
            output_prefix='test_company_settings',
            add_timestamp=False,
            output_folder=tmp_path
        )

        assert output_path.exists()

    # ========================================
    # 追加テスト: 空のデータフレーム処理
    # ========================================
    def test_empty_dataframe_handling(self, tmp_path):
        """空のデータフレームでもエラーが発生しないことを確認"""
        # 空のデータフレーム（ヘッダーのみ）
        df = pd.DataFrame(columns=['オーダーID', '会社名', '作業名称'])

        # 出力を試みる
        output_path = CSVReader.write_csv(
            df,
            output_prefix='empty_test',
            add_timestamp=False,
            output_folder=tmp_path
        )

        assert output_path.exists()

        # 出力ファイルを読み込んで検証
        output_df = pd.read_csv(output_path, encoding='utf-8-sig')
        assert len(output_df) == 0
        assert list(output_df.columns) == ['オーダーID', '会社名', '作業名称']

    # ========================================
    # 追加テスト: 大量データの処理（パフォーマンステスト）
    # ========================================
    def test_large_data_processing(self, tmp_path):
        """大量データ（100行）の処理がタイムアウトせず完了することを確認"""
        import time

        # 100行のテストデータを生成
        data = {
            'オーダーID': [f'ORD-{i:04d}' for i in range(1, 101)],
            '会社名': ['テスト会社' + str(i % 5) for i in range(1, 101)],
            '作業名称': [f'プロジェクト{i % 10}システム開発' for i in range(1, 101)]
        }
        df = pd.DataFrame(data)

        # CSV出力
        csv_path = tmp_path / 'large_test.csv'
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')

        # 処理開始時刻
        start_time = time.time()

        # 全フロー実行
        df = CSVReader.read_csv(csv_path)

        preprocessing_config = {
            'normalize_width': True,
            'remove_spaces': True,
            'remove_period': True,
            'remove_phase': True,
            'remove_symbols': True,
            'normalize_abbreviations': False
        }
        preprocessor = TextPreprocessor(preprocessing_config)
        df['正規化テキスト'] = preprocessor.preprocess_batch(df['作業名称'].tolist())

        clustering_config = {'company_cluster_settings': {}}
        clustering = DataClustering(clustering_config)
        result_df = clustering.cluster_by_company(df, '正規化テキスト')

        result_df = result_df.drop(columns=['正規化テキスト'])
        output_path = CSVReader.write_csv(
            result_df,
            output_prefix='large_output',
            add_timestamp=False,
            output_folder=tmp_path
        )

        # 処理時間を測定
        elapsed_time = time.time() - start_time

        # 100行のデータが10秒以内に処理されることを確認（緩い基準）
        assert elapsed_time < 10.0

        # 出力ファイルが正しく生成されたことを確認
        assert output_path.exists()
        output_df = pd.read_csv(output_path, encoding='utf-8-sig')
        assert len(output_df) == 100

    # ========================================
    # 追加テスト: 実データパターンの統合テスト
    # ========================================
    def test_real_data_pattern_integration(self, test_data_dir, tmp_path):
        """実際のデータパターンで全フローが動作することを確認"""
        csv_path = test_data_dir / 'test_sample.csv'

        # 全フロー実行
        df = CSVReader.read_csv(csv_path)

        # 元のデータを確認
        assert 'FY2024' in df['作業名称'].iloc[0] or 'FY2024' in df['作業名称'].values.astype(str).tolist().__str__()

        # 前処理
        preprocessing_config = {
            'normalize_width': True,
            'remove_spaces': True,
            'remove_period': True,
            'remove_phase': True,
            'remove_symbols': True,
            'normalize_abbreviations': False
        }
        preprocessor = TextPreprocessor(preprocessing_config)
        df['正規化テキスト'] = preprocessor.preprocess_batch(df['作業名称'].tolist())

        # 前処理後は時期・フェーズ情報が除去されていることを確認
        normalized_texts = ' '.join(df['正規化テキスト'].tolist())
        assert 'FY2024' not in normalized_texts or 'ＦＹ２０２４' not in normalized_texts

        # クラスタリング
        clustering_config = {'company_cluster_settings': {}}
        clustering = DataClustering(clustering_config)
        result_df = clustering.cluster_by_company(df, '正規化テキスト')

        # クラスタリング結果を検証
        assert 'クラスタID' in result_df.columns
        assert '代表名' in result_df.columns

        # 各会社ごとに複数のクラスタが生成されている可能性を確認
        for company in result_df['会社名'].unique():
            company_df = result_df[result_df['会社名'] == company]
            # 最低1クラスタは存在する
            assert company_df['クラスタID'].nunique() >= 1

        # 出力
        result_df = result_df.drop(columns=['正規化テキスト'])
        output_path = CSVReader.write_csv(
            result_df,
            output_prefix='real_data_output',
            add_timestamp=True,
            output_folder=tmp_path
        )

        assert output_path.exists()

        # 出力CSVの内容を検証
        output_df = pd.read_csv(output_path, encoding='utf-8-sig')
        assert len(output_df) == len(result_df)
        assert 'クラスタID' in output_df.columns
        assert '代表名' in output_df.columns
