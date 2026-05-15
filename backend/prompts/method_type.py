import json
import pandas as pd
import io


def build_get_method_type_prompt(df: pd.DataFrame) -> str:
    buffer = io.StringIO()
    df.info(buf=buffer)
    info_string = buffer.getvalue()

    return f"""
You are an expert data scientist specializing in exploratory data analysis and method selection.

Your task is to analyze the dataset based on the provided information and determine which analytical methods are applicable.

═══════════════════════════════
DATASET INFORMATION
═══════════════════════════════
{info_string}

═══════════════════════════════
SUMMARY STATISTICS
═══════════════════════════════
{df.describe().to_string()}

═══════════════════════════════
SAMPLE ROWS
═══════════════════════════════
{df.head(3).to_string()}

═══════════════════════════════
AVAILABLE METHODS
═══════════════════════════════
- clustering
- association_rule
- pca
- time_series

═══════════════════════════════
INSTRUCTIONS
═══════════════════════════════
1. Carefully analyze the dataset structure, column types, and statistical properties.
2. Decide which of the available methods are suitable for this dataset.
3. You may select one or more methods.
4. Only choose methods that are logically applicable based on the data.
5. Do NOT explain your reasoning.
6. Do NOT include any text outside the JSON.

═══════════════════════════════
OUTPUT FORMAT (STRICT)
═══════════════════════════════
Return ONLY a valid JSON object in this format:

{{
    "types": ["clustering", "association_rule"]
}}
"""
