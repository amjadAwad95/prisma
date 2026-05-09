from mlxtend.frequent_patterns import apriori, association_rules

from models.association.base_association import BaseAssociation


class AprioriAssociation(BaseAssociation):
    """Implementation of the Apriori algorithm for association rule mining."""

    def __init__(self, min_support=0.01, min_confidence=0.5, min_lift=1):
        """Initialize the AprioriAssociation with specified thresholds."""
        super().__init__(min_support, min_confidence, min_lift)

    def run(self, data) -> dict:
        """Run the Apriori algorithm to find frequent itemsets and generate association rules based on the specified thresholds.

        Args:
            data: Preprocessed transactional dataset in a one-hot encoded format.
        Returns:
            dict: A dictionary containing the frequent itemsets and the generated association rules.
        """
        # Run the Apriori algorithm to find frequent itemsets
        frequent_itemsets = apriori(
            data, min_support=self.min_support, use_colnames=True
        )

        # Generate association rules from the frequent itemsets
        rules = association_rules(
            frequent_itemsets, metric="confidence", min_threshold=self.min_confidence
        )[["antecedents", "consequents", "support", "confidence", "lift"]]

        # Filter rules based on lift
        filtered_rules = rules[rules["lift"] >= self.min_lift]

        return {
            "frequent_itemsets": frequent_itemsets,
            "association_rules": filtered_rules,
        }
