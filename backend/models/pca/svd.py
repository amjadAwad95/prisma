import numpy as np

from .base_pca import BasePCA


class SVD(BasePCA):
    """
    PCA implementation using Singular Value Decomposition (SVD).
    """

    def __init__(self, n_components=None, threshold=0.95):
        """
        Initialize the SVD model.

        Args:
            n_components (int, optional):
                Number of principal components.
                If None, components are selected automatically
                using the variance threshold.

            threshold (float):
                Cumulative explained variance threshold used
                when n_components is None.
        """
        super().__init__(n_components)

        self.threshold = threshold

        self.U = None
        self.S = None
        self.VT = None

        self.explained_variance = None
        self.explained_variance_ratio = None
        self.cumulative_variance = None

        self.components_ = None
        self.k = None

        self.execution_time = None

    def run(self, data):
        """
        Run PCA using Singular Value Decomposition (SVD).

        Args:
            data (array-like):
                Scaled numerical input data.

        Returns:
            np.ndarray:
                Reduced transformed dataset.
        """

        self.U, self.S, self.VT = np.linalg.svd(data, full_matrices=False)

        self.explained_variance = (self.S**2) / (data.shape[0] - 1)

        self.explained_variance_ratio = (
            self.explained_variance / self.explained_variance.sum()
        )

        self.cumulative_variance = np.cumsum(self.explained_variance_ratio)

        if self.n_components is None:
            self.k = np.argmax(self.cumulative_variance >= self.threshold) + 1
        else:
            self.k = self.n_components

        self.components_ = self.VT[: self.k].T

        transformed_data = data @ self.components_

        return transformed_data
