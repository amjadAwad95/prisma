from pathlib import Path

from models.association.apriori import AprioriAssociation
from preprocessing.preprocessing import Preprocessing
from models.groq import GroqModel
from utils.prompts import get_association_rule_prompt_builder
from utils.read_file import read_file


class AssociationService:
    """
    Service class for handling association rule mining operations.
    This class is responsible for orchestrating the preprocessing of data and the execution of the Apriori algorithm to find frequent itemsets and generate association rules based on specified thresholds.
    """

    def __init__(self):
        """Initialize the AssociationService with necessary components."""
        self.processor = Preprocessing()
        self.model = GroqModel()

    def run(
        self,
        file_path: str,
        min_support: float,
        min_confidence: float,
        min_lift: float,
    ) -> tuple[Path, Path]:
        """
        Run association rule mining on the uploaded data.

        Args:
            file_path (str): The path to the uploaded file.
            min_support (float): Minimum support threshold.
            min_confidence (float): Minimum confidence threshold.
            min_lift (float): Minimum lift threshold.

        Returns:
            tuple[Path, Path]: Paths to frequent itemsets and association rules files.
        """
        # Load the raw data to build the prompt
        df = read_file(file_path)
        # Build a callable prompt function for preprocessing
        prompt_fun = get_association_rule_prompt_builder()
        # Preprocess the data using the Groq model and the defined prompt
        preprocessed_path = self.processor.run(
            file_path=file_path,
            prompt_fun=prompt_fun,
            model=self.model,
        )
        # Read the preprocessed data into a DataFrame
        df = read_file(str(preprocessed_path))
        # Run the Apriori algorithm to find frequent itemsets and association rules
        apriori = AprioriAssociation(
            min_support=min_support,
            min_confidence=min_confidence,
            min_lift=min_lift,
        )
        result = apriori.run(df)
        frequent_itemsets = result["frequent_itemsets"]
        association_rules = result["association_rules"]
        # Save the results to CSV files and return their paths
        itemsets_path = self._build_output_path(file_path, "itemsets")
        rules_path = self._build_output_path(file_path, "rules")
        frequent_itemsets.to_csv(itemsets_path, index=False)
        association_rules.to_csv(rules_path, index=False)

        return itemsets_path, rules_path

    def _build_output_path(self, file_path: str, suffix: str) -> Path:
        """Build the output path for the association results.

        Args:
            file_path (str): The path to the input file.
            suffix (str): The suffix for the output file.

        Returns:
            Path: The path to the output file.
        """
        base_name = Path(file_path).stem
        output_dir = Path("association_results") / base_name
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir / f"{base_name}_{suffix}.csv"
