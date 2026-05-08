import pandas as pd
import io

from dto.preprocessing_dto import MethodType


def build_clustering_prompt(df: pd.DataFrame) -> str:
    buffer = io.StringIO()
    df.info(buf=buffer)
    info_string = buffer.getvalue()

    return f"""
You are a data preprocessing expert preparing a dataset for clustering.

DATASET:
{info_string}

Summary:
{df.describe().to_string()}

Sample:
{df.head(3).to_string()}

TASK:
Write Python code to preprocess this dataset for clustering.

GUIDELINES:
- Ensure the final dataframe `df`:
    • contains only numeric features
    • has no missing values
    • is properly scaled
- Remove irrelevant or harmful features if needed (e.g., IDs, high-cardinality categorical columns)
- Apply any preprocessing steps you find appropriate based on the data

CONSTRAINTS:
- Start with: df = pd.read_csv(input_path)
- Use only: pandas, numpy, sklearn
- Do not save the file
- Do not include clustering code
- Output ONLY Python code

Return the final cleaned dataframe as `df`.
"""


def build_clustering_prompt_for_algorithm(
    df: pd.DataFrame, algorithm: str, params: dict[str, object] | None = None
) -> str:
    buffer = io.StringIO()
    df.info(buf=buffer)
    info_string = buffer.getvalue()

    params_line = ""
    if params:
        params_line = f"\nAlgorithm parameters: {params}"

    return f"""
You are a data preprocessing expert preparing a dataset for clustering.

ALGORITHM:
{algorithm}{params_line}

DATASET:
{info_string}

Summary:
{df.describe().to_string()}

Sample:
{df.head(3).to_string()}

TASK:
Write Python code to preprocess this dataset specifically for the clustering algorithm above.

GUIDELINES:
- Ensure the final dataframe `df`:
    • contains only numeric features
    • has no missing values
    • is properly scaled for distance-based clustering
- Remove irrelevant or harmful features if needed (e.g., IDs, high-cardinality categorical columns)
- Apply any preprocessing steps you find appropriate based on the data

CONSTRAINTS:
- Start with: df = pd.read_csv(input_path)
- Use only: pandas, numpy, sklearn
- Do not save the file
- Do not include clustering code
- Output ONLY Python code

Return the final cleaned dataframe as `df`.
"""


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
- anomaly_detection
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


def get_prompt_for_method_type(method_type: str) -> str:
    if method_type == MethodType.CLUSTERING:
        return build_clustering_prompt
    else:
        raise ValueError(f"Unsupported method type: {method_type}")


def get_clustering_prompt_builder(
    algorithm: str, params: dict[str, object] | None = None
) -> callable:
    def _builder(df: pd.DataFrame) -> str:
        return build_clustering_prompt_for_algorithm(df, algorithm, params)

    return _builder
