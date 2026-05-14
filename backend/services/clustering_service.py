from __future__ import annotations

from pathlib import Path
import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from kneed import KneeLocator
from sklearn.ensemble import RandomForestClassifier
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.neighbors import NearestNeighbors
from scipy.cluster.hierarchy import dendrogram, linkage

from dto.clustering_dto import ClusteringAlgorithm
from preprocessing.preprocessing import Preprocessing
from models.agent.groq import GroqModel
from models.clustering.dbscan import DBSCANClustering
from models.clustering.hierarchical import HierarchicalClustering
from models.clustering.kmeans import KMeansClustering
from models.pca.covariance_matrix import CovarianceMatrixPCA
from models.pca.svd import SVD
from prompts.clustering import (
    build_cluster_insights_prompt,
    get_clustering_prompt_builder,
)
from utils.read_file import read_file


class ClusteringService:
    """ "
    Service for running clustering algorithms on uploaded data. Handles preprocessing, model fitting, scoring, and diagram generation.

    """

    def __init__(self) -> None:
        self.preprocessor = Preprocessing()
        self.model = GroqModel()
        self.pca_feature_threshold = 50
        self.pca_correlation_threshold = 0.9
        self.pca_variance_target = 0.95

    def run(
        self,
        file_path: str,
        algorithm: ClusteringAlgorithm,
        params: dict[str, object] | None = None,
    ) -> tuple[Path, list[int], list[str]]:
        """
        Run a specific clustering algorithm on the given file.
        Args:
            file_path (str): The path to the preprocessed file.
            algorithm (ClusteringAlgorithm): The clustering algorithm to run.
            params (dict[str, object], optional): Additional parameters for the algorithm.
        Returns:
            tuple[Path, list[int]]: The path to the output file and the list of cluster labels.
        """
        prompt_fun = get_clustering_prompt_builder(algorithm.value, params or {})

        preprocessed_path = self.preprocessor.run(
            file_path=file_path,
            prompt_fun=prompt_fun,
            model=self.model,
        )

        df = read_file(str(preprocessed_path))
        base_df = df.copy()
        df_for_clustering, _ = self._maybe_apply_pca(df)
        cluster_model, labels = self._fit_model(algorithm, df_for_clustering)

        result_df = base_df.copy()
        result_df["cluster"] = labels

        output_path = self._build_output_path(file_path, algorithm.value)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        result_df.to_csv(output_path, index=False)

        insights = self._build_cluster_insights(base_df, labels)
        insights_path = output_path.parent / f"{output_path.stem}_insights.json"
        insights_path.write_text(
            json.dumps({"insights": insights}, ensure_ascii=True),
            encoding="utf-8",
        )

        return output_path, labels, insights

    def run_best(
        self, file_path: str, upload_id: str
    ) -> tuple[
        Path, list[int], ClusteringAlgorithm, list[dict[str, object]], list[str]
    ]:
        """
        Run all clustering algorithms and select the best one based on silhouette score.
        Args:
            file_path (str): The path to the preprocessed file.
            upload_id (str): The ID of the upload, used for saving diagrams.
        Returns:
            tuple[Path, list[int], ClusteringAlgorithm, list[dict[str, object]]]: The path to the output file, the best cluster labels, the best algorithm, and a list of results for all algorithms.
        """
        prompt_fun = get_clustering_prompt_builder(ClusteringAlgorithm.KMEANS.value, {})

        preprocessed_path = self.preprocessor.run(
            file_path=file_path,
            prompt_fun=prompt_fun,
            model=self.model,
        )

        df = read_file(str(preprocessed_path))
        base_df = df.copy()
        df_for_clustering, _ = self._maybe_apply_pca(df)
        values = df_for_clustering.to_numpy()

        best_score = -1.0
        best_algorithm = ClusteringAlgorithm.KMEANS
        best_labels: list[int] = []
        results: list[dict[str, object]] = []
        models: dict[ClusteringAlgorithm, object] = {}
        labels_by_algorithm: dict[ClusteringAlgorithm, list[int]] = {}

        for algorithm in ClusteringAlgorithm:
            model, labels = self._fit_model(algorithm, df_for_clustering)
            score = self._score_labels(values, labels)
            n_clusters, noise_points = self._summarize_labels(labels, algorithm)

            models[algorithm] = model
            labels_by_algorithm[algorithm] = labels

            results.append(
                {
                    "algorithm": algorithm,
                    "silhouette": score,
                    "n_clusters": n_clusters,
                    "noise_points": noise_points,
                }
            )

            if score > best_score:
                best_score = score
                best_algorithm = algorithm
                best_labels = labels

        result_df = base_df.copy()
        result_df["cluster"] = best_labels

        self._save_diagrams(upload_id, base_df, models, labels_by_algorithm)

        output_path = self._build_output_path(file_path, best_algorithm.value)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        result_df.to_csv(output_path, index=False)

        insights = self._build_cluster_insights(base_df, best_labels)
        insights_path = output_path.parent / f"{output_path.stem}_insights.json"
        insights_path.write_text(
            json.dumps({"insights": insights}, ensure_ascii=True),
            encoding="utf-8",
        )

        return output_path, best_labels, best_algorithm, results, insights

    def _fit_model(
        self,
        algorithm: ClusteringAlgorithm,
        df: pd.DataFrame,
    ) -> tuple[object, list[int]]:
        """
        Fit the specified clustering model to the data and return the model and cluster labels.
        Args:
            algorithm (ClusteringAlgorithm): The clustering algorithm to fit.
            df (pd.DataFrame): The input data as a DataFrame.
        Returns:
            tuple[object, list[int]]: The fitted model and the list of cluster labels.
        """
        if algorithm == ClusteringAlgorithm.KMEANS:
            n_clusters = self._choose_k_elbow(df)
            model = KMeansClustering(n_clusters=n_clusters)
            return model, model.fit_predict(df)
        if algorithm == ClusteringAlgorithm.DBSCAN:
            return self._choose_dbscan_model(df)
        if algorithm == ClusteringAlgorithm.HIERARCHICAL:
            return self._choose_hierarchical_model(df)

        raise ValueError(f"Unsupported algorithm: {algorithm}")

    def _choose_k_elbow(self, df: pd.DataFrame) -> int:
        """
        Choose the optimal number of clusters using the elbow method.
        Args:
            df (pd.DataFrame): The input data as a DataFrame.
        Returns:
            int: The chosen number of clusters.
        """
        sample_count = len(df.index)
        if sample_count < 3:
            return 1

        max_k = min(10, sample_count - 1)
        k_values = list(range(2, max_k + 1))
        inertias: list[float] = []

        for k in k_values:
            model = KMeans(n_clusters=k, n_init=10, random_state=42)
            model.fit(df)
            inertias.append(model.inertia_)

        knee = KneeLocator(
            k_values,
            inertias,
            curve="convex",
            direction="decreasing",
        )

        return int(knee.knee or 3)

    def _choose_dbscan_model(self, df: pd.DataFrame) -> tuple[object, list[int]]:
        """
        Choose the optimal DBSCAN model based on silhouette score.
        Args:
            df (pd.DataFrame): The input data as a DataFrame.
        Returns:
            tuple[object, list[int]]: The chosen DBSCAN model and the list of cluster labels.
        """
        sample_count = len(df.index)
        if sample_count < 3:
            model = DBSCANClustering(eps=0.5, min_samples=2)
            return model, model.fit_predict(df)

        min_samples_grid = [3, 5, 8]
        best_score = -1.0
        best_model: DBSCANClustering | None = None
        best_labels: list[int] | None = None

        values = df.to_numpy()

        for min_samples in min_samples_grid:
            if sample_count <= min_samples:
                continue

            neighbors = NearestNeighbors(n_neighbors=min_samples)
            neighbors.fit(values)
            distances, _ = neighbors.kneighbors(values)
            k_distances = np.sort(distances[:, -1])

            knee = KneeLocator(
                range(len(k_distances)),
                k_distances,
                curve="convex",
                direction="increasing",
            )

            if knee.knee is None:
                continue

            eps = float(k_distances[int(knee.knee)])
            labels = DBSCANClustering(eps=eps, min_samples=min_samples).fit_predict(df)
            unique_labels = set(labels)
            unique_labels.discard(-1)

            if len(unique_labels) < 2:
                continue

            try:
                score = silhouette_score(values, labels)
            except ValueError:
                continue

            if score > best_score:
                best_score = score
                best_model = DBSCANClustering(eps=eps, min_samples=min_samples)
                best_labels = labels

        if best_model and best_labels:
            return best_model, best_labels

        fallback = DBSCANClustering(eps=0.5, min_samples=5)
        return fallback, fallback.fit_predict(df)

    def _choose_hierarchical_model(self, df: pd.DataFrame) -> tuple[object, list[int]]:
        """
        Choose the optimal hierarchical clustering model based on silhouette score.
        Args:
            df (pd.DataFrame): The input data as a DataFrame.
        Returns:
            tuple[object, list[int]]: The chosen hierarchical clustering model and the list of cluster labels.
        """
        sample_count = len(df.index)
        if sample_count < 3:
            model = HierarchicalClustering(n_clusters=1, linkage="average")
            return model, model.fit_predict(df)

        max_k = min(10, sample_count - 1)
        k_values = list(range(2, max_k + 1))
        linkages = ["single", "average", "complete"]

        best_score = -1.0
        best_model: HierarchicalClustering | None = None
        best_labels: list[int] | None = None
        values = df.to_numpy()

        for linkage in linkages:
            for k in k_values:
                model = HierarchicalClustering(n_clusters=k, linkage=linkage)
                labels = model.fit_predict(df)
                unique_labels = set(labels)

                if len(unique_labels) < 2:
                    continue

                try:
                    score = silhouette_score(values, labels)
                except ValueError:
                    continue

                if score > best_score:
                    best_score = score
                    best_model = HierarchicalClustering(n_clusters=k, linkage=linkage)
                    best_labels = labels

        if best_model and best_labels:
            return best_model, best_labels

        fallback = HierarchicalClustering(n_clusters=3, linkage="average")
        return fallback, fallback.fit_predict(df)

    def _score_labels(self, values: np.ndarray, labels: list[int]) -> float:
        """
        Score the quality of the clustering labels using the silhouette score.
        Args:
            values (np.ndarray): The input data as a NumPy array.
            labels (list[int]): The list of cluster labels.
        Returns:
            float: The silhouette score.
        """
        unique_labels = set(labels)
        unique_labels.discard(-1)

        if len(unique_labels) < 2:
            return -1.0

        try:
            return float(silhouette_score(values, labels))
        except ValueError:
            return -1.0

    def _build_cluster_insights(
        self,
        df: pd.DataFrame,
        labels: list[int],
        max_clusters: int = 4,
        max_features: int = 3,
    ) -> list[str]:
        facts = self._build_cluster_facts(df, labels, max_clusters, max_features)
        if not facts:
            return []

        llm_output = self._summarize_cluster_facts_with_llm(facts)
        if llm_output:
            return llm_output

        return self._format_cluster_facts(facts)

    def _build_cluster_facts(
        self,
        df: pd.DataFrame,
        labels: list[int],
        max_clusters: int,
        max_features: int,
    ) -> dict[str, object] | None:
        if df.empty or len(labels) != len(df.index):
            return None

        working = df.copy()
        working["cluster"] = labels
        clusters = sorted(c for c in working["cluster"].unique() if c != -1)

        if not clusters:
            return {
                "summary": "No stable clusters found in this dataset.",
                "clusters": [],
            }

        total_count = int(len(working.index))
        feature_df = working.drop(columns=["cluster"])
        overall_means = feature_df.mean(numeric_only=True)
        overall_stds = feature_df.std(numeric_only=True).replace(0, np.nan)

        ranked_features = self._rank_features_by_cluster(
            feature_df, labels, max_features * 4
        )
        if not ranked_features:
            ranked_features = list(overall_means.index)

        binary_columns: set[str] = set()
        for col in feature_df.columns:
            values = feature_df[col].dropna().unique()
            if values.size == 0:
                continue
            rounded = set(np.round(values.astype(float), 6).tolist())
            if rounded.issubset({0.0, 1.0}):
                binary_columns.add(col)

        cluster_sizes = {
            cluster: int((working["cluster"] == cluster).sum()) for cluster in clusters
        }
        top_clusters = sorted(
            clusters, key=lambda c: cluster_sizes.get(c, 0), reverse=True
        )[:max_clusters]

        cluster_entries: list[dict[str, object]] = []
        for cluster in top_clusters:
            cluster_df = working[working["cluster"] == cluster]
            cluster_count = int(len(cluster_df.index))
            share = cluster_count / total_count
            cluster_means = cluster_df.drop(columns=["cluster"]).mean(numeric_only=True)

            deltas: list[dict[str, object]] = []
            for col in ranked_features:
                if col not in overall_means:
                    continue
                overall_value = overall_means[col]
                cluster_value = float(cluster_means.get(col, overall_value))
                if col in binary_columns:
                    diff = cluster_value - float(overall_value)
                    deltas.append(
                        {
                            "name": col,
                            "type": "binary",
                            "diff": float(diff),
                            "cluster_value": cluster_value,
                            "overall_value": float(overall_value),
                        }
                    )
                else:
                    std_value = float(overall_stds.get(col, np.nan))
                    if np.isnan(std_value) or std_value <= 0:
                        continue
                    z_score = (cluster_value - float(overall_value)) / std_value
                    deltas.append(
                        {
                            "name": col,
                            "type": "numeric",
                            "z_score": float(z_score),
                            "cluster_value": cluster_value,
                            "overall_value": float(overall_value),
                            "std": std_value,
                        }
                    )

            deltas.sort(
                key=lambda item: abs(float(item.get("diff", item.get("z_score", 0.0)))),
                reverse=True,
            )

            highlights: list[dict[str, object]] = []
            for item in deltas:
                if len(highlights) >= max_features:
                    break
                if item["type"] == "binary":
                    if abs(float(item["diff"])) < 0.15:
                        continue
                else:
                    if abs(float(item["z_score"])) < 0.75:
                        continue
                highlights.append(item)

            cluster_entries.append(
                {
                    "cluster": int(cluster),
                    "count": cluster_count,
                    "share": round(share, 3),
                    "highlights": highlights,
                }
            )

        return {
            "summary": f"Found {len(clusters)} clusters across {total_count} records.",
            "clusters": cluster_entries,
        }

    def _rank_features_by_cluster(
        self,
        df: pd.DataFrame,
        labels: list[int],
        max_features: int,
    ) -> list[str]:
        if df.empty or len(labels) != len(df.index):
            return []

        label_array = np.array(labels)
        mask = label_array != -1
        if mask.sum() < 5:
            return []

        filtered_labels = label_array[mask]
        if len(set(filtered_labels.tolist())) < 2:
            return []

        try:
            model = RandomForestClassifier(
                n_estimators=200,
                random_state=42,
                n_jobs=-1,
                class_weight="balanced_subsample",
            )
            model.fit(df.loc[mask].to_numpy(), filtered_labels)
            importances = model.feature_importances_
            ranked_indices = np.argsort(importances)[::-1]
            ranked_features = [df.columns[idx] for idx in ranked_indices]
            return ranked_features[:max_features]
        except (ValueError, TypeError):
            return []

    def _format_cluster_facts(self, facts: dict[str, object]) -> list[str]:
        summary = facts.get("summary")
        if isinstance(summary, str) and summary.startswith("No stable"):
            return [summary]

        insights: list[str] = [str(summary)] if summary else []
        clusters = facts.get("clusters", [])
        if not isinstance(clusters, list):
            return insights

        for cluster in clusters:
            cluster_id = cluster.get("cluster")
            count = cluster.get("count")
            share = cluster.get("share")
            highlights = cluster.get("highlights", [])

            if not highlights:
                insights.append(
                    f"Cluster {cluster_id} ({count} records, {share:.0%}) looks similar to the overall dataset."
                )
                continue

            feature_notes: list[str] = []
            for item in highlights:
                name = item["name"]
                if item["type"] == "binary":
                    cluster_rate = round(float(item["cluster_value"]) * 100)
                    overall_rate = round(float(item["overall_value"]) * 100)
                    direction = "higher" if item["diff"] > 0 else "lower"
                    feature_notes.append(
                        f"{direction} rate of {name} ({cluster_rate}% vs {overall_rate}%)"
                    )
                else:
                    direction = "higher" if item["z_score"] > 0 else "lower"
                    cluster_value = round(float(item["cluster_value"]), 2)
                    overall_value = round(float(item["overall_value"]), 2)
                    feature_notes.append(
                        f"{direction} {name} (avg {cluster_value} vs {overall_value})"
                    )

            details = "; ".join(feature_notes)
            insights.append(
                f"Cluster {cluster_id} ({count} records, {share:.0%}): {details}."
            )

        return insights

    def _summarize_cluster_facts_with_llm(
        self, facts: dict[str, object]
    ) -> list[str] | None:
        summary = facts.get("summary")
        if isinstance(summary, str) and summary.startswith("No stable"):
            return [summary]

        prompt = build_cluster_insights_prompt(facts)

        try:
            model = GroqModel(config={"max_completion_tokens": 600})
            output = model.generate(prompt)
            parsed = json.loads(output)
            if isinstance(parsed, list) and all(
                isinstance(item, str) for item in parsed
            ):
                return parsed
        except (json.JSONDecodeError, ValueError, TypeError):
            return None

        return None

    def _maybe_apply_pca(
        self, df: pd.DataFrame
    ) -> tuple[pd.DataFrame, dict[str, object]]:
        feature_count = df.shape[1]
        if feature_count < 2:
            return df, {"applied": False, "reason": "insufficient_features"}

        max_corr = self._max_abs_correlation(df)
        needs_pca = feature_count >= self.pca_feature_threshold or (
            max_corr is not None and max_corr >= self.pca_correlation_threshold
        )

        if not needs_pca:
            return df, {"applied": False, "reason": "not_needed"}

        pca_df, details = self._apply_pca(df)
        details.update({"applied": True, "max_correlation": max_corr})
        return pca_df, details

    def _max_abs_correlation(self, df: pd.DataFrame) -> float | None:
        if df.shape[1] < 2:
            return None

        corr = df.corr(numeric_only=True).abs()
        if corr.empty:
            return None

        upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
        max_corr = upper.max().max()
        if pd.isna(max_corr):
            return None

        return float(max_corr)

    def _apply_pca(self, df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object]]:
        feature_count = df.shape[1]
        details: dict[str, object] = {
            "variance_target": self.pca_variance_target,
            "original_features": feature_count,
        }

        if feature_count < 1000:
            pca_model = CovarianceMatrixPCA(n_components=self.pca_variance_target)
            transformed = pca_model.run(df)
            explained_variance_ratio = pca_model.pca.explained_variance_ratio_.tolist()
            cumulative_variance = (
                pca_model.pca.explained_variance_ratio_.cumsum().tolist()
            )
        else:
            pca_model = SVD(n_components=None, threshold=self.pca_variance_target)
            transformed = pca_model.run(df)
            explained_variance_ratio = pca_model.explained_variance_ratio.tolist()
            cumulative_variance = pca_model.cumulative_variance.tolist()

        component_count = transformed.shape[1]
        columns = [f"PC{i + 1}" for i in range(component_count)]
        pca_df = pd.DataFrame(transformed, columns=columns)

        details.update(
            {
                "pca_features": component_count,
                "explained_variance_ratio": explained_variance_ratio,
                "cumulative_variance": cumulative_variance,
            }
        )

        return pca_df, details

    def _summarize_labels(
        self, labels: list[int], algorithm: ClusteringAlgorithm
    ) -> tuple[int, int | None]:
        """
        Summarize the clustering labels by counting the number of clusters and noise points (if applicable).
        Args:
            labels (list[int]): The list of cluster labels.
            algorithm (ClusteringAlgorithm): The clustering algorithm used, to determine if noise points should be counted.
        Returns:
            tuple[int, int | None]: The number of clusters and the number of noise points (if applicable).
        """
        label_set = set(labels)
        noise_points = None

        if algorithm == ClusteringAlgorithm.DBSCAN:
            noise_points = labels.count(-1)
            label_set.discard(-1)

        return len(label_set), noise_points

    def _build_output_path(self, file_path: str, algorithm: str) -> Path:
        base_name = Path(file_path).stem
        return Path("clustered") / f"{base_name}_{algorithm}.csv"

    def _save_diagrams(
        self,
        upload_id: str,
        df: pd.DataFrame,
        models: dict[ClusteringAlgorithm, object],
        labels_by_algorithm: dict[ClusteringAlgorithm, list[int]],
    ) -> None:
        """
        Save the clustering diagrams to the specified directory.
        Args:
            upload_id (str): The ID of the upload.
            df (pd.DataFrame): The input data as a DataFrame.
            models (dict[ClusteringAlgorithm, object]): The dictionary of clustering models.
            labels_by_algorithm (dict[ClusteringAlgorithm, list[int]]): The dictionary of cluster labels by algorithm.
        """
        output_dir = Path("digrams") / upload_id / "clustering"
        output_dir.mkdir(parents=True, exist_ok=True)

        kmeans_labels = labels_by_algorithm[ClusteringAlgorithm.KMEANS]
        feature_x, feature_y = self._select_scatter_features(df, kmeans_labels)

        self._plot_kmeans(
            output_dir,
            df,
            feature_x,
            feature_y,
            kmeans_labels,
        )

        dbscan_labels = labels_by_algorithm[ClusteringAlgorithm.DBSCAN]
        feature_x, feature_y = self._select_scatter_features(df, dbscan_labels)

        self._plot_dbscan(
            output_dir,
            df,
            feature_x,
            feature_y,
            models[ClusteringAlgorithm.DBSCAN],
            dbscan_labels,
        )

        self._plot_hierarchical_dendrograms(output_dir, df)

    def _select_scatter_features(
        self, df: pd.DataFrame, labels: list[int]
    ) -> tuple[str, str]:
        columns = list(df.columns)
        if len(columns) < 2:
            raise ValueError("Need at least two features to plot clustering diagrams.")

        ranked = self._rank_features_by_cluster(df, labels, 2)
        if len(ranked) >= 2:
            return ranked[0], ranked[1]

        return columns[0], columns[1]

    def _plot_kmeans(
        self,
        output_dir: Path,
        df: pd.DataFrame,
        feature_x: str,
        feature_y: str,
        labels: list[int],
    ) -> None:
        plt.figure(figsize=(8, 6))
        plt.title("K-Means Clustering")
        plt.xlabel(feature_x)
        plt.ylabel(feature_y)

        scatter = plt.scatter(df[feature_x], df[feature_y], c=labels, cmap="tab10")
        plt.legend(*scatter.legend_elements(), title="Cluster", loc="best")
        plt.tight_layout()
        plt.savefig(output_dir / "kmeans.png", dpi=160)
        plt.close()

    def _plot_dbscan(
        self,
        output_dir: Path,
        df: pd.DataFrame,
        feature_x: str,
        feature_y: str,
        model: object,
        labels: list[int],
    ) -> None:
        eps = getattr(model, "model", model).eps
        min_samples = getattr(model, "model", model).min_samples

        plt.figure(figsize=(8, 6))
        plt.title(f"DBSCAN Clustering (eps={eps}, min_samples={min_samples})")
        plt.xlabel(feature_x)
        plt.ylabel(feature_y)

        labels_array = np.array(labels)
        noise_mask = labels_array == -1
        cluster_mask = labels_array != -1

        if cluster_mask.any():
            plt.scatter(
                df.loc[cluster_mask, feature_x],
                df.loc[cluster_mask, feature_y],
                c=labels_array[cluster_mask],
                cmap="tab10",
                label="Cluster",
            )

        if noise_mask.any():
            plt.scatter(
                df.loc[noise_mask, feature_x],
                df.loc[noise_mask, feature_y],
                marker="x",
                c="#9aa0a6",
                label="Noise",
            )

        plt.legend(loc="best")
        plt.tight_layout()
        plt.savefig(output_dir / "dbscan.png", dpi=160)
        plt.close()

    def _plot_hierarchical_dendrograms(
        self,
        output_dir: Path,
        df: pd.DataFrame,
    ) -> None:
        if len(df.index) > 300:
            df = df.sample(n=300, random_state=42)

        values = df.to_numpy()
        linkages = ["single", "average", "complete"]

        fig, axes = plt.subplots(1, 3, figsize=(18, 6))

        for ax, method in zip(axes, linkages, strict=False):
            linkage_matrix = linkage(values, method=method)
            ax.set_title(f"Dendrogram ({method} linkage)")
            dendrogram(linkage_matrix, ax=ax, no_labels=True, color_threshold=None)
            ax.set_ylabel("Distance")

        fig.tight_layout()
        fig.savefig(output_dir / "hierarchical_dendrograms.png", dpi=160)
        plt.close(fig)
