from sklearn.decomposition import PCA

from .base_pca import BasePCA


class CovarianceMatrixPCA(BasePCA):
    """
    PCA implementation using the covariance matrix.
    This class implements PCA by computing the covariance matrix of the input data and then performing eigen decomposition to find the principal components. The `run` method fits the PCA model to the data and returns the transformed data along with the fitted PCA model.
    """

    def __init__(self, n_components):
        """
        Initialize the CovarianceMatrixPCA model with the specified number of components.
        Args:
            n_components (int): The number of principal components to compute.
        """
        super().__init__(n_components)
        self.pca = None

    def run(self, data):
        """
        Run the PCA algorithm on the input data.
        Args:
            data (array-like): The input data to transform.
        Returns:
            np.ndarray: The transformed data.
        """
        self.pca = PCA(n_components=self.n_components)
        transformed_data = self.pca.fit_transform(data)
        return transformed_data
