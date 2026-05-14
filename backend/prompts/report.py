import json
import pandas as pd
import io


def build_report_prompt(
    df: pd.DataFrame,
    schema: dict[str, object],
    algorithms: list[dict[str, object]],
) -> str:
    schema_json = json.dumps(schema, indent=2)
    algorithms_json = json.dumps(algorithms, indent=2)

    return f"""
You are a data analyst writing a friendly, non-technical report for general users.

DATA SCHEMA (JSON):
{schema_json}

ALGORITHMS INPUT (JSON):
{algorithms_json}

DATASET SUMMARY:
{df.describe(include='all').to_string()}

SAMPLE ROWS:
{df.head(5).to_string()}

TASK:
Create a report in Markdown with the following sections:
1) Dataset Overview
2) Data Schema
3) Algorithm Results (one subsection per algorithm in the input order)
4) Key Metrics and Measures
5) Notes and Recommendations

GUIDELINES:
- Use the provided schema and algorithm inputs.
- For each algorithm section, explain what was found in simple terms.
- Prefer plain-language interpretations and practical takeaways.
- If an item is missing, say "Not provided".
- Keep the report concise and clear.
- Use GitHub-flavored Markdown tables where tabular data is presented.
- Put a blank line before and after each table.
- Each table row must be on its own line and start with "|".
- Always include all five sections, even if they contain only "Not provided".
- Use the exact heading text shown in the template below.
- Add analysis that is NOT a restatement of inputs, but keep it non-technical:
    - Data quality in plain terms (missing values, possible ID columns).
    - What changed or stood out in the results.
    - Clear, actionable next steps in everyday language.
- Avoid technical jargon, equations, or metric-heavy explanations.

TEMPLATE (USE THIS STRUCTURE):
# Report

## 1) Dataset Overview
<short bullets>

<optional table>

## 2) Data Schema
<table>

## 3) Algorithm Results
### <Algorithm Name 1>
<bullets>
<optional table>

### <Algorithm Name 2>
<bullets>
<optional table>

## 4) Key Metrics and Measures
<bullets or table>

## 5) Notes and Recommendations
<bullets>

OUTPUT:
- Return ONLY Markdown.
"""
