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


def build_association_rule_prompt(df: pd.DataFrame) -> str:
    buffer = io.StringIO()
    df.info(buf=buffer)
    info_string = buffer.getvalue()

    return f"""
You are a senior data preprocessing expert preparing data for association rule mining using the Apriori algorithm.

DATASET INFO:
{info_string}

STATISTICAL SUMMARY:
{df.describe(include='all').to_string()}

SAMPLE ROWS:
{df.head(5).to_string()}

OBJECTIVE:
Transform this dataset into a CLEAN transactional one-hot encoded dataframe suitable for association rule mining.

The goal is to build a CO-OCCURRENCE MODEL where each row represents a transaction/context and each column represents a single consistent type of ENTITY that can co-occur.

FINAL OUTPUT REQUIREMENTS:
- Final dataframe variable must be named: df
- Each row must represent a transaction/context
- Each column must represent a binary entity (0/1 or boolean)
- Final dataframe must contain ONLY ONE ENTITY TYPE (no mixing of semantics)
- Final dataframe must NOT contain continuous numerical values
- Final dataframe must be directly usable with Apriori

------------------------------------------------------------
ENTITY SCOPE SELECTION RULE (CRITICAL STEP)
------------------------------------------------------------
Before preprocessing, analyze the dataset and select EXACTLY ONE valid scope:

1. PRODUCT-BASED TRANSACTIONS:
   - entities are items/products/services (e.g., Apple, Bread, Milk)
   - REMOVE: user attributes, demographics, labels, segments

2. USER/SEGMENT CO-OCCURRENCE:
   - entities are users, groups, or segments (e.g., UserA, Student, Premium)
   - REMOVE: product/item data

3. EVENT/BEHAVIOR CO-OCCURRENCE:
   - entities are actions or behaviors (e.g., Click, View, PurchaseEvent)

STRICT RULE:
You MUST choose ONLY ONE scope. Do NOT mix scopes under any condition.

------------------------------------------------------------
FORBIDDEN MIXING RULE (HARD CONSTRAINT)
------------------------------------------------------------
The final dataset must NOT mix:
- products + user attributes
- products + segments
- users + products
- behaviors + demographic labels

If multiple types exist, keep ONLY the dominant transactional type and remove the rest.

------------------------------------------------------------
PREPROCESSING RULES:
------------------------------------------------------------
1. Identify the correct transaction/context grouping
2. Determine the correct entity scope (ONLY ONE)
3. Remove all non-scope columns
4. Handle missing values appropriately
5. If entities are stored as comma-separated values, split them into individual items
6. Apply one-hot encoding only to valid entities
7. If numerical features are relevant, discretize them into categorical bins first
8. Remove duplicate columns if created
9. Ensure final dataframe contains ONLY binary values (0/1 or boolean)

------------------------------------------------------------
COLUMN CLASSIFICATION RULE:
------------------------------------------------------------
Classify columns into:

- ENTITY (KEEP ONLY IF MATCHES SELECTED SCOPE)
- METADATA (REMOVE ALWAYS):
  - IDs, UUIDs, indexes
  - timestamps or dates (unless defining grouping logic)
- CONTINUOUS FEATURES:
  - must be discretized or removed

------------------------------------------------------------
CONSTRAINTS:
------------------------------------------------------------
- Start exactly with:
    df = pd.read_csv(input_path)

- Use ONLY:
    pandas
    numpy
    sklearn

- Do NOT:
    - save files
    - print explanations
    - include comments
    - include markdown
    - include association rule mining code

OUTPUT:
Return ONLY executable Python code.
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
    elif method_type == MethodType.ASSOCIATION_RULE:
        return build_association_rule_prompt
    else:
        raise ValueError(f"Unsupported method type: {method_type}")


def get_clustering_prompt_builder(
    algorithm: str, params: dict[str, object] | None = None
) -> callable:
    def _builder(df: pd.DataFrame) -> str:
        return build_clustering_prompt_for_algorithm(df, algorithm, params)

    return _builder


def get_association_rule_prompt_builder() -> callable:
    def _builder(df: pd.DataFrame) -> str:
        return build_association_rule_prompt(df)

    return _builder
