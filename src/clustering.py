"""
クラスタリングモジュール

TF-IDFベクトル化とコサイン類似度による階層的クラスタリング
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import AgglomerativeClustering
from scipy.cluster.hierarchy import linkage

logger = logging.getLogger(__name__)


class DataClustering:
    """クラスタリングクラス"""

    def __init__(self, config: Dict[str, Any]):
        """
        初期化

        Args:
            config: クラスタリング設定（clustering セクション）
        """
        self.config = config
        self.company_cluster_settings = config.get('company_cluster_settings', {})
        logger.info("DataClustering initialized")

    def calculate_default_clusters(
        self,
        distance_threshold: float,
        linkages: np.ndarray,
        n_samples: int
    ) -> int:
        """
        デフォルトクラスタ数を自動計算

        デンドログラムの距離増加率から最適なクラスタ数を決定
        制約: 2 〜 データ件数 * 0.5

        Args:
            distance_threshold: 距離閾値
            linkages: 階層的クラスタリング結果
            n_samples: サンプル数

        Returns:
            クラスタ数
        """
        if n_samples <= 2:
            return 1

        # デンドログラムの距離増加率を計算
        distances = linkages[:, 2]

        # 距離の増加率が最も大きい箇所を探す
        if len(distances) > 1:
            diffs = np.diff(distances)
            max_diff_idx = np.argmax(diffs)
            n_clusters = len(distances) - max_diff_idx
        else:
            n_clusters = 1

        # 制約: 2 〜 n_samples * 0.5
        min_clusters = 2
        max_clusters = max(2, int(n_samples * 0.5))

        n_clusters = max(min_clusters, min(n_clusters, max_clusters))

        return n_clusters

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
        setting = self.company_cluster_settings.get(company)

        if setting is None:
            # 設定なし: デフォルト値を使用
            logger.info(f"{company}: 自動計算={default_count}, 調整後={default_count}（設定なし）")
            return default_count

        final_count = default_count

        if isinstance(setting, str):
            # オフセットモード
            if setting.startswith("+"):
                try:
                    offset = int(setting[1:])
                    final_count = default_count + offset
                    logger.info(f"{company}: 自動計算={default_count}, 調整後={final_count}（{setting}）")
                except ValueError:
                    logger.warning(f"{company}: 不正なオフセット設定 '{setting}'。デフォルト値を使用します。")
                    final_count = default_count
            elif setting.startswith("-"):
                try:
                    offset = int(setting[1:])
                    final_count = default_count - offset
                    logger.info(f"{company}: 自動計算={default_count}, 調整後={final_count}（{setting}）")
                except ValueError:
                    logger.warning(f"{company}: 不正なオフセット設定 '{setting}'。デフォルト値を使用します。")
                    final_count = default_count
            else:
                logger.warning(f"{company}: 不正なオフセット設定 '{setting}'。デフォルト値を使用します。")
                final_count = default_count
        elif isinstance(setting, (int, float)):
            # 固定モード
            final_count = int(setting)
            logger.info(f"{company}: 自動計算={default_count}, 調整後={final_count}（固定）")
        else:
            logger.warning(f"{company}: 不正な設定タイプ '{type(setting)}'。デフォルト値を使用します。")
            final_count = default_count

        # 制約: 1以上
        final_count = max(1, final_count)

        return final_count

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
        companies = df['会社名'].unique()
        logger.info(f"クラスタリング開始: {len(companies)}社")

        result_dfs = []

        for company in companies:
            company_df = df[df['会社名'] == company].copy()
            logger.info(f"処理中: {company} ({len(company_df)}件)")

            if len(company_df) <= 1:
                # データが1件以下の場合はクラスタリングをスキップ
                company_df['クラスタID'] = 1
                company_df['代表名'] = company_df['作業名称'].iloc[0] if len(company_df) > 0 else ""
                result_dfs.append(company_df)
                logger.info(f"{company}: データが1件以下のためクラスタリングをスキップ")
                continue

            # TF-IDFベクトル化
            texts = company_df[text_column].tolist()
            vectorizer = TfidfVectorizer(
                token_pattern=r'(?u)\b\w+\b',  # 文字ベースでトークン化
                min_df=1
            )

            try:
                tfidf_matrix = vectorizer.fit_transform(texts)
            except ValueError as e:
                logger.warning(f"{company}: TF-IDFベクトル化に失敗。全て同じクラスタに割り当てます。エラー: {e}")
                company_df['クラスタID'] = 1
                company_df['代表名'] = company_df['作業名称'].iloc[0]
                result_dfs.append(company_df)
                continue

            # コサイン類似度計算
            similarity_matrix = cosine_similarity(tfidf_matrix)

            # 距離行列（1 - コサイン類似度）
            distance_matrix = 1 - similarity_matrix

            # 階層的クラスタリング（linkage計算）
            try:
                # 距離行列を1次元配列に変換（condensed form）
                from scipy.spatial.distance import squareform
                condensed_distance = squareform(distance_matrix, checks=False)
                linkages = linkage(condensed_distance, method='average')

                # デフォルトクラスタ数を自動計算
                default_clusters = self.calculate_default_clusters(
                    distance_threshold=0.5,
                    linkages=linkages,
                    n_samples=len(company_df)
                )

                # 企業別設定を反映
                n_clusters = self.get_cluster_count(company, default_clusters)

                # AgglomerativeClusteringでクラスタリング
                clustering_model = AgglomerativeClustering(
                    n_clusters=n_clusters,
                    metric='precomputed',
                    linkage='average'
                )
                cluster_labels = clustering_model.fit_predict(distance_matrix)

            except Exception as e:
                logger.warning(f"{company}: クラスタリングに失敗。全て同じクラスタに割り当てます。エラー: {e}")
                cluster_labels = np.zeros(len(company_df), dtype=int)

            # クラスタIDを付与（1から始まる連番）
            company_df['クラスタID'] = cluster_labels + 1

            # 代表名を付与（各クラスタで最頻出の作業名称）
            representative_names = {}
            for cluster_id in company_df['クラスタID'].unique():
                cluster_rows = company_df[company_df['クラスタID'] == cluster_id]
                # 最頻出の作業名称を取得
                most_common = cluster_rows['作業名称'].mode()
                if len(most_common) > 0:
                    representative_names[cluster_id] = most_common.iloc[0]
                else:
                    representative_names[cluster_id] = cluster_rows['作業名称'].iloc[0]

            company_df['代表名'] = company_df['クラスタID'].map(representative_names)

            result_dfs.append(company_df)
            logger.info(f"{company}: 完了 ({n_clusters}クラスタ)")

        # 全ての会社のデータを結合
        result_df = pd.concat(result_dfs, ignore_index=True)
        logger.info(f"クラスタリング完了: 全{len(result_df)}件")

        return result_df
