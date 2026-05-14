from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from kneed import KneeLocator
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
from utils.prompts import get_clustering_prompt_builder
from utils.read_file import read_file


class ClusteringService:
    """ "
    Service for running clustering algorithms on uploaded data. Handles preprocessing, model fitting, scoring, and diagram generation.

    """

    def __init__(self) -> None:
        self.preprocessor = Preprocessing()
        self.model = GroqModel()

    def run(
        self,
        file_path: str,
        algorithm: ClusteringAlgorithm,
        params: dict[str, object] | None = None,
    ) -> tuple[Path, list[int]]:
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
        cluster_model, labels = self._fit_model(algorithm, df)

        result_df = df.copy()
        result_df["cluster"] = labels

        output_path = self._build_output_path(file_path, algorithm.value)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        result_df.to_csv(output_path, index=False)

        return output_path, labels

    def run_best(
        self, file_path: str, upload_id: str
    ) -> tuple[Path, list[int], ClusteringAlgorithm, list[dict[str, object]]]:
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
        values = df.to_numpy()

        best_score = -1.0
        best_algorithm = ClusteringAlgorithm.KMEANS
        best_labels: list[int] = []
        results: list[dict[str, object]] = []
        models: dict[ClusteringAlgorithm, object] = {}
        labels_by_algorithm: dict[ClusteringAlgorithm, list[int]] = {}

        for algorithm in ClusteringAlgorithm:
            model, labels = self._fit_model(algorithm, df)
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

        result_df = df.copy()
        result_df["cluster"] = best_labels

        self._save_diagrams(upload_id, df, models, labels_by_algorithm)

        output_path = self._build_output_path(file_path, best_algorithm.value)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        result_df.to_csv(output_path, index=False)

        return output_path, best_labels, best_algorithm, results

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

        feature_x, feature_y = self._select_scatter_features(df)

        self._plot_kmeans(
            output_dir,
            df,
            feature_x,
            feature_y,
            labels_by_algorithm[ClusteringAlgorithm.KMEANS],
        )

        self._plot_dbscan(
            output_dir,
            df,
            feature_x,
            feature_y,
            models[ClusteringAlgorithm.DBSCAN],
            labels_by_algorithm[ClusteringAlgorithm.DBSCAN],
        )

        self._plot_hierarchical_dendrograms(output_dir, df)

    def _select_scatter_features(self, df: pd.DataFrame) -> tuple[str, str]:
        columns = list(df.columns)
        if len(columns) < 2:
            raise ValueError("Need at least two features to plot clustering diagrams.")
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
