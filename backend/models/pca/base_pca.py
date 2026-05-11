from abc import ABC, abstractmethod


class BasePCA(ABC):
    """
    Base class for PCA implementations.
    This class defines the interface for PCA models. Subclasses must implement the `run` method, which takes in data and returns the transformed data along with the PCA model.
    """

    def __init__(self, n_components):
        """
        Initialize the PCA model with the specified number of components.
        Args:
            n_components (int): The number of principal components to compute.
        """
        self.n_components = n_components

    @abstractmethod
    def run(self, data):
        """
        Run the PCA algorithm on the input data.
        Args:
            data (array-like): The input data to transform.
        Returns:
            tuple: A tuple containing the transformed data and the fitted PCA model.
        """
        pass
