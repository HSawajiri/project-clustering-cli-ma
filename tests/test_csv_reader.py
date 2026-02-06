"""
CSV Reader Module Tests

テスト対象:
- FR-001: CSV入力データ読み込み
- エンコーディング自動検出
- 必須列検証
- CSV出力
"""

import pytest
import pandas as pd
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from csv_reader import CSVReader


class TestCSVReader:
    """CSVReader クラスのテスト"""

    @pytest.fixture
    def test_data_dir(self):
        """テストデータディレクトリのパス"""
        return Path(__file__).parent / 'data'

    @pytest.fixture
    def sample_df(self):
        """サンプルデータフレーム"""
        return pd.DataFrame({
            'オーダーID': ['ORD-001', 'ORD-002', 'ORD-003'],
            '会社名': ['テスト株式会社', 'サンプル銀行', '日本企業'],
            '作業名称': ['在庫管理システム', '顧客管理システム', 'EDI連携']
        })

    # ========================================
    # TC-FR001-001: UTF-8 with BOM エンコーディング読み込み
    # ========================================
    def test_read_csv_utf8_bom(self, test_data_dir):
        """UTF-8 with BOM形式のCSVを正しく読み込めることを確認"""
        csv_path = test_data_dir / 'test_encoding_utf8_bom.csv'

        df = CSVReader.read_csv(csv_path)

        assert len(df) == 3
        assert 'オーダーID' in df.columns
        assert 'テスト株式会社' in df['会社名'].values
        # 文字化けしていないことを確認
        assert '在庫管理システム開発' in df['作業名称'].values

    # ========================================
    # TC-FR001-002: Shift-JIS エンコーディング読み込み
    # ========================================
    def test_read_csv_shift_jis(self, test_data_dir):
        """Shift-JIS形式のCSVを正しく読み込めることを確認"""
        csv_path = test_data_dir / 'test_encoding_sjis.csv'

        df = CSVReader.read_csv(csv_path)

        assert len(df) == 3
        assert 'オーダーID' in df.columns
        assert 'サンプル銀行' in df['会社名'].values

    # ========================================
    # TC-FR001-003: エンコーディング自動検出
    # ========================================
    def test_detect_encoding(self, test_data_dir):
        """エンコーディングを自動判定できることを確認"""
        # UTF-8 with BOM
        utf8_bom_path = test_data_dir / 'test_encoding_utf8_bom.csv'
        encoding = CSVReader.detect_encoding(utf8_bom_path)
        assert encoding == 'utf-8-sig'

        # Shift-JIS
        sjis_path = test_data_dir / 'test_encoding_sjis.csv'
        encoding = CSVReader.detect_encoding(sjis_path)
        assert encoding == 'shift-jis'

    # ========================================
    # TC-FR001-004: 必須列検証（正常系）
    # ========================================
    def test_validate_columns_success(self, sample_df):
        """必須列が存在する場合に正常終了することを確認"""
        # エラーが発生しないことを確認
        CSVReader.validate_columns(sample_df)

    # ========================================
    # TC-FR001-005: 必須列検証（異常系: オーダーID欠損）
    # ========================================
    def test_validate_columns_missing_order_id(self):
        """オーダーID列が存在しない場合にエラーが発生することを確認"""
        df = pd.DataFrame({
            '会社名': ['テスト会社'],
            '作業名称': ['テストプロジェクト']
        })

        with pytest.raises(KeyError, match='オーダーID'):
            CSVReader.validate_columns(df)

    # ========================================
    # TC-FR001-006: 必須列検証（異常系: 会社名欠損）
    # ========================================
    def test_validate_columns_missing_company(self):
        """会社名列が存在しない場合にエラーが発生することを確認"""
        df = pd.DataFrame({
            'オーダーID': ['ORD-001'],
            '作業名称': ['テストプロジェクト']
        })

        with pytest.raises(KeyError, match='会社名'):
            CSVReader.validate_columns(df)

    # ========================================
    # TC-FR001-007: 必須列検証（異常系: 作業名称欠損）
    # ========================================
    def test_validate_columns_missing_task_name(self):
        """作業名称列が存在しない場合にエラーが発生することを確認"""
        df = pd.DataFrame({
            'オーダーID': ['ORD-001'],
            '会社名': ['テスト会社']
        })

        with pytest.raises(KeyError, match='作業名称'):
            CSVReader.validate_columns(df)

    # ========================================
    # TC-FR001-008: CSV自動検出
    # ========================================
    def test_auto_detect_csv(self, test_data_dir):
        """フォルダ内のCSVファイルを自動検出できることを確認"""
        csv_path = CSVReader.auto_detect_csv(test_data_dir)

        assert csv_path is not None
        assert csv_path.suffix == '.csv'
        assert csv_path.exists()

    # ========================================
    # TC-FR001-009: ファイル不存在エラー
    # ========================================
    def test_read_csv_file_not_found(self):
        """存在しないファイルを指定した場合にエラーが発生することを確認"""
        non_existent_path = Path('/tmp/non_existent_file.csv')

        with pytest.raises(FileNotFoundError):
            CSVReader.read_csv(non_existent_path)

    # ========================================
    # TC-FR004-001: CSV出力（UTF-8 with BOM）
    # ========================================
    def test_write_csv_encoding(self, sample_df, tmp_path):
        """UTF-8 with BOMエンコーディングで出力されることを確認"""
        output_path = CSVReader.write_csv(
            sample_df,
            output_prefix='test',
            add_timestamp=False,
            output_folder=tmp_path
        )

        assert output_path.exists()

        # BOMの確認
        with open(output_path, 'rb') as f:
            first_bytes = f.read(3)
            assert first_bytes == b'\xef\xbb\xbf'

    # ========================================
    # TC-FR004-002: タイムスタンプ付きファイル名
    # ========================================
    def test_write_csv_timestamp(self, sample_df, tmp_path):
        """タイムスタンプがファイル名に付与されることを確認"""
        output_path = CSVReader.write_csv(
            sample_df,
            output_prefix='result',
            add_timestamp=True,
            output_folder=tmp_path
        )

        assert output_path.exists()
        # ファイル名が "result_YYYYMMDD_HHMMSS.csv" 形式であることを確認
        assert output_path.name.startswith('result_')
        assert output_path.suffix == '.csv'
        # タイムスタンプ部分（8桁の日付_6桁の時刻）が含まれることを確認
        import re
        assert re.match(r'result_\d{8}_\d{6}\.csv', output_path.name)

    # ========================================
    # TC-FR004-003: タイムスタンプなしファイル名
    # ========================================
    def test_write_csv_no_timestamp(self, sample_df, tmp_path):
        """タイムスタンプなしで出力できることを確認"""
        output_path = CSVReader.write_csv(
            sample_df,
            output_prefix='result',
            add_timestamp=False,
            output_folder=tmp_path
        )

        assert output_path.exists()
        assert output_path.name == 'result.csv'

    # ========================================
    # 追加テスト: 実際のテストデータでの読み込み
    # ========================================
    def test_read_test_sample_csv(self, test_data_dir):
        """test_sample.csv を正しく読み込めることを確認"""
        csv_path = test_data_dir / 'test_sample.csv'

        df = CSVReader.read_csv(csv_path)

        assert len(df) == 15  # 15行のデータ
        assert 'オーダーID' in df.columns
        assert '会社名' in df.columns
        assert '作業名称' in df.columns
        assert 'みらい銀行' in df['会社名'].values
        assert '東京システム株式会社' in df['会社名'].values

    def test_read_invalid_csv(self, test_data_dir):
        """必須列が欠けているCSVでエラーが発生することを確認"""
        csv_path = test_data_dir / 'test_invalid.csv'

        with pytest.raises(KeyError, match='作業名称'):
            CSVReader.read_csv(csv_path)
