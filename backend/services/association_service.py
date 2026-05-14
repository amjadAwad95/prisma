from pathlib import Path
import json

from models.association.apriori import AprioriAssociation
from preprocessing.preprocessing import Preprocessing
from models.agent.groq import GroqModel
from prompts.association_rule import (
    build_association_insights_prompt,
    get_association_rule_prompt_builder,
)
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
    ) -> tuple[Path, Path, dict[str, float], list[str]]:
        """
        Run association rule mining on the uploaded data.

        Args:
            file_path (str): The path to the uploaded file.

        Returns:
            tuple[Path, Path, dict[str, float]]: Paths to frequent itemsets and association rules files with chosen thresholds.
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
        thresholds = self._select_thresholds(df)

        # Run the Apriori algorithm to find frequent itemsets and association rules
        apriori = AprioriAssociation(
            min_support=thresholds["min_support"],
            min_confidence=thresholds["min_confidence"],
            min_lift=thresholds["min_lift"],
        )
        result = self._safe_run_apriori(apriori, df)
        frequent_itemsets = result["frequent_itemsets"]
        association_rules = result["association_rules"]
        # Save the results to CSV files and return their paths
        itemsets_path = self._build_output_path(file_path, "itemsets")
        rules_path = self._build_output_path(file_path, "rules")
        frequent_itemsets.to_csv(itemsets_path, index=False)
        association_rules.to_csv(rules_path, index=False)

        insights = self._build_association_insights(association_rules)

        base_name = Path(file_path).stem
        insights_path = (
            Path("association_results") / base_name / f"{base_name}_insights.json"
        )
        insights_path.write_text(
            json.dumps({"insights": insights}, ensure_ascii=True),
            encoding="utf-8",
        )

        return itemsets_path, rules_path, thresholds, insights

    def _select_thresholds(self, df) -> dict[str, float]:
        row_count = max(int(df.shape[0]), 1)
        min_support_floor = max(2 / row_count, 0.001)

        support_grid = [0.1, 0.05, 0.03, 0.02, 0.01, 0.005]
        support_grid = [value for value in support_grid if value >= min_support_floor]
        if not support_grid:
            support_grid = [min_support_floor]

        confidence_grid = [0.8, 0.7, 0.6, 0.5, 0.4]
        lift_grid = [1.2, 1.1, 1.0]

        target_min = 10
        target_max = 200
        target_mid = (target_min + target_max) / 2

        best_score = float("-inf")
        best_thresholds = {
            "min_support": support_grid[-1],
            "min_confidence": 0.5,
            "min_lift": 1.0,
        }

        for min_support in support_grid:
            for min_confidence in confidence_grid:
                for min_lift in lift_grid:
                    apriori = AprioriAssociation(
                        min_support=min_support,
                        min_confidence=min_confidence,
                        min_lift=min_lift,
                    )
                    result = self._safe_run_apriori(apriori, df)
                    rules = result["association_rules"]
                    rule_count = int(len(rules.index))

                    if rule_count == 0:
                        continue

                    avg_conf = float(rules["confidence"].mean())
                    avg_lift = float(rules["lift"].mean())

                    if target_min <= rule_count <= target_max:
                        size_bonus = 1000 - abs(rule_count - target_mid)
                    else:
                        size_bonus = -abs(rule_count - target_min) * 2

                    score = size_bonus + (avg_conf * 100) + (avg_lift * 10)

                    if score > best_score:
                        best_score = score
                        best_thresholds = {
                            "min_support": min_support,
                            "min_confidence": min_confidence,
                            "min_lift": min_lift,
                        }

        return best_thresholds

    def _safe_run_apriori(self, apriori: AprioriAssociation, df):
        try:
            return apriori.run(df)
        except (ValueError, KeyError):
            empty = df.iloc[0:0].copy()
            return {"frequent_itemsets": empty, "association_rules": empty}

    def _build_association_insights(self, rules_df) -> list[str]:
        facts = self._build_association_facts(rules_df)
        if not facts:
            return []

        llm_output = self._summarize_association_facts_with_llm(facts)
        if llm_output:
            return llm_output

        return self._format_association_facts(facts)

    def _build_association_facts(
        self, rules_df, max_rules: int = 5
    ) -> dict[str, object] | None:
        if rules_df is None or rules_df.empty:
            return {"summary": "No strong item associations were found.", "rules": []}

        def _stringify(value) -> str:
            if isinstance(value, (set, frozenset, list, tuple)):
                return ", ".join(sorted([str(item) for item in value]))
            return str(value)

        sorted_rules = rules_df.sort_values(
            ["lift", "confidence", "support"], ascending=False
        ).head(max_rules)

        rules: list[dict[str, object]] = []
        for _, row in sorted_rules.iterrows():
            rules.append(
                {
                    "antecedent": _stringify(row["antecedents"]),
                    "consequent": _stringify(row["consequents"]),
                    "support": float(row["support"]),
                    "confidence": float(row["confidence"]),
                    "lift": float(row["lift"]),
                }
            )

        return {
            "summary": f"Top {len(rules)} association patterns were found.",
            "rules": rules,
        }

    def _format_association_facts(self, facts: dict[str, object]) -> list[str]:
        summary = facts.get("summary")
        insights: list[str] = [str(summary)] if summary else []

        rules = facts.get("rules", [])
        if not isinstance(rules, list):
            return insights

        for rule in rules:
            antecedent = rule.get("antecedent", "")
            consequent = rule.get("consequent", "")
            insights.append(f"People who buy {antecedent} often also buy {consequent}.")

        return insights

    def _summarize_association_facts_with_llm(
        self, facts: dict[str, object]
    ) -> list[str] | None:
        summary = facts.get("summary")
        if isinstance(summary, str) and summary.startswith("No strong"):
            return [summary]

        prompt = build_association_insights_prompt(facts)

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
