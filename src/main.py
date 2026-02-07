#!/usr/bin/env python3
"""
Project Clustering CLI MA - Main Entry Point

プロジェクト名クラスタリングツール
TF-IDF + コサイン類似度による階層的クラスタリング

Usage:
    python main.py [options]
    clustering.exe [options]
"""

import sys
import argparse
import logging
from pathlib import Path
from config_handler import ConfigHandler
from logger import setup_logger
from csv_reader import CSVReader
from preprocessor import TextPreprocessor
from clustering import DataClustering


def parse_args():
    """コマンドライン引数を解析"""
    parser = argparse.ArgumentParser(
        description='プロジェクト名クラスタリングツール',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用例:
  python main.py
  python main.py --config config.yaml
  python main.py --input data.csv --output result
        '''
    )

    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='設定ファイルパス（デフォルト: config.yaml）'
    )

    parser.add_argument(
        '--input',
        type=str,
        help='入力CSVファイルパス（config.yamlの設定を上書き）'
    )

    parser.add_argument(
        '--output',
        type=str,
        help='出力ファイル接頭辞（config.yamlの設定を上書き）'
    )

    return parser.parse_args()


def main():
    """メイン処理"""
    args = parse_args()

    try:
        # 設定ファイルの読み込み
        config_path = Path(args.config)
        if not config_path.is_absolute():
            # 相対パスの場合は.exeまたはmain.pyからの相対パス
            config_path = Path(__file__).parent.parent / config_path

        config = ConfigHandler(config_path)

        # ロガー設定
        log_level_str = config.get('logging.level', 'INFO')
        log_level = getattr(logging, log_level_str.upper(), logging.INFO)

        log_file_path = None
        if config.get('logging.file', True):
            log_file_path = config.get('logging.file_path', 'clustering.log')
            log_file_path = Path(__file__).parent.parent / log_file_path

        logger = setup_logger(__name__, log_file=log_file_path, level=log_level)

        # 開始メッセージ
        logger.info("=" * 60)
        logger.info("プロジェクト名クラスタリングツール Starting")
        logger.info("=" * 60)

        # 1. CSV入力ファイルの読み込み
        input_file = args.input or config.get('io.input_file', '')

        if not input_file:
            # 自動検出
            logger.info("入力ファイルが指定されていません。自動検出を試みます...")
            search_folder = Path(__file__).parent.parent
            input_path = CSVReader.auto_detect_csv(search_folder)
            if input_path is None:
                logger.error("CSVファイルが見つかりません。")
                logger.error("config.yamlでinput_fileを指定するか、.exeと同じフォルダにCSVファイルを配置してください。")
                return 1
        else:
            input_path = Path(input_file)
            if not input_path.is_absolute():
                input_path = Path(__file__).parent.parent / input_path

        df = CSVReader.read_csv(input_path)

        # 2. 前処理
        preprocessing_config = config.get('preprocessing', {})
        preprocessor = TextPreprocessor(preprocessing_config)

        logger.info("前処理を開始します...")
        df['正規化テキスト'] = preprocessor.preprocess_batch(df['作業名称'].tolist())

        # 3. クラスタリング
        clustering_config = config.get('clustering', {})
        clustering = DataClustering(clustering_config)

        logger.info("クラスタリングを開始します...")
        result_df = clustering.cluster_by_company(df, '正規化テキスト')

        # 正規化テキスト列を削除（出力CSVには含めない）
        result_df = result_df.drop(columns=['正規化テキスト'])

        # 4. 結果出力
        output_prefix = args.output or config.get('io.output_prefix', 'output_clustered')
        add_timestamp = config.get('io.output_timestamp', True)
        output_folder = Path(__file__).parent.parent

        output_path = CSVReader.write_csv(
            result_df,
            output_prefix=output_prefix,
            add_timestamp=add_timestamp,
            output_folder=output_folder
        )

        # 完了メッセージ
        logger.info("=" * 60)
        logger.info("処理が正常に完了しました")
        logger.info(f"出力ファイル: {output_path.name}")
        logger.info("=" * 60)
        return 0

    except FileNotFoundError as e:
        logger.error(f"ファイルが見つかりません: {e}")
        logger.error("指定されたファイルが存在するか確認してください。")
        return 1
    except KeyError as e:
        logger.error(f"必須列が存在しません: {e}")
        logger.error("CSVファイルに必要な列（オーダーID、会社名、作業名称）が含まれているか確認してください。")
        return 1
    except ValueError as e:
        logger.error(f"不正な値: {e}")
        return 1
    except Exception as e:
        logger.error(f"予期しないエラーが発生しました: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
