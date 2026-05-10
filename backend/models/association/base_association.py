from abc import ABC, abstractmethod


class BaseAssociation(ABC):
    def __init__(
        self,
        min_support: float = 0.01,
        min_confidence: float = 0.5,
        min_lift: float = 1.0,
    ):
        self.min_support = min_support
        self.min_confidence = min_confidence
        self.min_lift = min_lift

    @abstractmethod
    def run(self, data):
        """
        Run the association rule mining algorithm.

        Parameters:
            data: Preprocessed transactional dataset

        Returns:
            dict: Association rules and frequent itemsets
        """
        pass
