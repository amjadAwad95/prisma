import json
import pandas as pd


def build_report_prompt(
    df: pd.DataFrame,
    schema: dict[str, object],
    algorithms: list[dict[str, object]],
) -> str:
    schema_json = json.dumps(schema, indent=2)
    algorithms_json = json.dumps(algorithms, indent=2)

    return f"""
You are a professional business data analyst writing a report for non-technical readers such as:
- HR teams
- Managers
- Business teams
- Marketing teams
- Operations staff

The audience does NOT understand machine learning, statistics, clustering, forecasting, or association rules.

Your job is to explain the results in very simple business language.

IMPORTANT:
- Do NOT use technical jargon.
- Do NOT explain algorithms technically.
- Do NOT mention model tuning, preprocessing, PCA, hyperparameters, or mathematical details.
- Focus on WHAT was discovered and WHY it matters.
- Explain insights like you are speaking to a business manager.
- Every finding should answer:
    - What happened?
    - Why does it matter?
    - What action could someone take?

DATA SCHEMA (JSON):
{schema_json}

ALGORITHMS INPUT (JSON):
{algorithms_json}

DATASET SUMMARY:
{df.describe(include='all').to_string()}

SAMPLE ROWS:
{df.head(5).to_string()}

TASK:
Generate a professional Markdown report with the following sections:

1) Dataset Overview
2) Data Structure Summary
3) Findings and Insights
4) Business Impact
5) Recommendations and Next Steps

REPORT STYLE:
- Use clear, human-friendly language.
- Keep explanations short and practical.
- Avoid technical wording.
- Use examples when useful.
- Highlight patterns, trends, unusual behavior, and important observations.
- If information is missing, say "Not provided".
- Make the report feel like a business presentation summary.
- Focus more on interpretation than raw numbers.

SPECIAL INSTRUCTIONS FOR ALGORITHM RESULTS:
If algorithms are provided:
- Explain the results in simple business terms.
- Never explain how the algorithm works.
- Translate technical findings into real-world meaning.

Examples:
BAD:
"Cluster 2 has high variance and lower centroid density."

GOOD:
"This group contains customers with similar purchasing habits and may respond well to the same marketing strategy."

BAD:
"Association rules show support/confidence values."

GOOD:
"Customers who buy Product A often also buy Product B, suggesting a possible bundle opportunity."

BAD:
"Forecast values indicate seasonality."

GOOD:
"The data suggests demand may increase during certain periods, so teams should prepare resources in advance."

TABLE RULES:
- Use GitHub Markdown tables when useful.
- Put a blank line before and after each table.
- Each table row must start with "|".

TEMPLATE:

# Report

## 1) Dataset Overview
- Brief explanation of what the dataset appears to contain
- Important observations about the data

## 2) Data Structure Summary

| Column | Meaning | Notes |
|---|---|---|

## 3) Findings and Insights

### General Findings
- Main trends
- Interesting patterns
- Unusual observations

### Algorithm Results

#### <Algorithm Name>
- Simple explanation of findings
- Business meaning
- Important insights

## 4) Business Impact
- Explain how the findings could affect business decisions
- Mention possible opportunities or risks
- Explain who may benefit from the insights

## 5) Recommendations and Next Steps
- Clear actionable recommendations
- Suggested follow-up actions
- Areas worth monitoring

OUTPUT RULES:
- Return ONLY Markdown.
- Keep the report concise but insightful.
- Write like a professional analyst preparing a report for executives.
"""