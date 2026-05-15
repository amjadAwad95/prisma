import json
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

from models.pca.covariance_matrix import CovarianceMatrixPCA
from models.pca.svd import SVD
from models.agent.groq import GroqModel

from preprocessing.preprocessing import Preprocessing

from dto.pca_dto import PCAMethodType

from prompts.pca import build_pca_prompt
from utils.read_file import read_file


class PCAService:
    """
    Service class for handling PCA operations.
    This class is responsible for orchestrating the preprocessing of data and the execution of PCA algorithms (Covariance Matrix and SVD) to reduce the dimensionality of the dataset while retaining as much variance as possible.
    """

    def __init__(self):
        """
        Initializes the PCAService with preprocessing and model instances.
        """
        self.processor = Preprocessing()
        self.model = GroqModel()

    def run(self, file_path: str, upload_id: str, n_components: int = 0.99) -> str:
        prompt_fun = build_pca_prompt

        preprocessed_path = self.processor.run(
            file_path=file_path,
            prompt_fun=prompt_fun,
            model=self.model,
        )

        preprocessed_df = read_file(str(preprocessed_path))

        num_coulmns = preprocessed_df.shape[1]
        if num_coulmns < 1000:
            pca_type = PCAMethodType.COVARIANCE_MATRIX
            pca_model = CovarianceMatrixPCA(n_components=n_components)
        else:
            pca_type = PCAMethodType.SVD
            pca_model = SVD(n_components=n_components)

        transformed_data = pca_model.run(preprocessed_df)

        ## take explained_variance_ratio: list, cumulative_variance: list

        if pca_type == PCAMethodType.COVARIANCE_MATRIX:
            pca = pca_model.pca
            explained_variance_ratio = pca.explained_variance_ratio_
            cumulative_variance = explained_variance_ratio.cumsum()
        else:
            explained_variance_ratio = pca_model.explained_variance_ratio
            cumulative_variance = pca_model.cumulative_variance

        output_path = Path(
            f"pca_output/{file_path.split('_')[0].split('/')[-1]}/pca_result_{preprocessed_path.stem}.csv"
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)

        component_count = transformed_data.shape[1]
        columns = [f"PC{i + 1}" for i in range(component_count)]
        transformed_df = pd.DataFrame(transformed_data, columns=columns)
        transformed_df.to_csv(output_path, index=False)

        explained_variance_ratio_list = explained_variance_ratio.tolist()
        cumulative_variance_list = cumulative_variance.tolist()

        metrics_dir = Path("pca_output") / upload_id
        metrics_dir.mkdir(parents=True, exist_ok=True)

        metrics_payload = {
            "explained_variance_ratio_list": explained_variance_ratio_list,
            "cumulative_variance_list": cumulative_variance_list,
        }
        (metrics_dir / "variance_metrics.json").write_text(
            json.dumps(metrics_payload), encoding="utf-8"
        )

        self._save_diagrams(
            upload_id=upload_id,
            transformed_df=transformed_df,
            explained_variance_ratio=explained_variance_ratio_list,
            cumulative_variance=cumulative_variance_list,
        )

        return (
            str(output_path),
            pca_type,
            explained_variance_ratio_list,
            cumulative_variance_list,
        )

    def _save_diagrams(
        self,
        upload_id: str,
        transformed_df: pd.DataFrame,
        explained_variance_ratio: list[float],
        cumulative_variance: list[float],
    ) -> None:
        output_dir = Path("digrams") / upload_id / "pca"
        output_dir.mkdir(parents=True, exist_ok=True)

        if not explained_variance_ratio:
            return

        component_count = len(explained_variance_ratio)
        components = list(range(1, component_count + 1))
        labels = [f"PC{i}" for i in components]

        if transformed_df.shape[1] >= 2:
            plt.figure(figsize=(8, 6))
            plt.title("PCA - 2D Visualization")
            plt.xlabel("Principal Component 1")
            plt.ylabel("Principal Component 2")
            plt.scatter(
                transformed_df["PC1"],
                transformed_df["PC2"],
                s=20,
                alpha=0.8,
            )
            plt.tight_layout()
            plt.savefig(output_dir / "pca_2d.png", dpi=160)
            plt.close()

        ratio_percent = [value * 100 for value in explained_variance_ratio]
        plt.figure(figsize=(8, 6))
        plt.title("Scree Plot (PCA)")
        plt.ylabel("Explained Variance (%)")
        plt.xlabel("Principal Component")
        plt.bar(components, ratio_percent)
        plt.xticks(components, labels, rotation=45)
        plt.tight_layout()
        plt.savefig(output_dir / "pca_scree.png", dpi=160)
        plt.close()

        cumulative_percent = [value * 100 for value in cumulative_variance]
        plt.figure(figsize=(8, 6))
        plt.title("Cumulative Variance (PCA)")
        plt.ylabel("Cumulative Explained Variance (%)")
        plt.xlabel("Principal Component")
        plt.plot(components, cumulative_percent, marker="o")
        plt.axhline(80, linestyle="--", color="#1f77b4", label="80% threshold")
        plt.xticks(components, labels, rotation=45)
        plt.legend(loc="best")
        plt.tight_layout()
        plt.savefig(output_dir / "pca_cumulative_variance.png", dpi=160)
        plt.close()
