import json
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


def build_pca_prompt(df: pd.DataFrame) -> str:
    buffer = io.StringIO()
    df.info(buf=buffer)
    info_string = buffer.getvalue()

    return f"""
You are a senior data preprocessing expert preparing data for Principal Component Analysis (PCA).

DATASET INFO:
{info_string}

STATISTICAL SUMMARY:
{df.describe(include='all').to_string()}

SAMPLE ROWS:
{df.head(5).to_string()}

OBJECTIVE:
Transform this dataset into a CLEAN numerical feature matrix suitable for PCA dimensionality reduction.

The goal is to create a standardized dataset where:
- rows represent observations/samples
- columns represent meaningful numerical features
- features are scaled appropriately for PCA
- redundant or irrelevant information is removed

FINAL OUTPUT REQUIREMENTS:
- Final dataframe variable must be named: df
- Final dataframe must contain ONLY numerical features
- Final dataframe must NOT contain identifiers or meaningless metadata
- Final dataframe must NOT contain missing values
- Features must be scaled appropriately for PCA
- Final dataframe must be directly usable with sklearn PCA

------------------------------------------------------------
PCA PREPROCESSING OBJECTIVES
------------------------------------------------------------
The preprocessing pipeline should maximize:
- variance preservation
- feature consistency
- numerical stability
- meaningful latent structure extraction

The pipeline should minimize:
- noise
- redundant identifiers
- high-cardinality meaningless categorical features
- data leakage risks

------------------------------------------------------------
COLUMN CLASSIFICATION RULE
------------------------------------------------------------
Classify columns into:

1. NUMERICAL FEATURES (KEEP):
   - continuous variables
   - ordinal numerical variables
   - meaningful count-based features

2. CATEGORICAL FEATURES:
   - apply encoding ONLY if meaningful
   - low-cardinality categories may be one-hot encoded
   - high-cardinality identifiers should be removed

3. METADATA (REMOVE ALWAYS):
   - IDs
   - UUIDs
   - indexes
   - names
   - free-text descriptions
   - timestamps/dates unless transformed meaningfully

------------------------------------------------------------
PREPROCESSING RULES
------------------------------------------------------------
1. Remove duplicate rows if necessary
2. Handle missing values appropriately
3. Remove constant or near-constant columns
4. Remove duplicate columns if they exist
5. Detect and remove obvious identifier columns
6. Convert categorical variables into numerical form when useful
7. Avoid introducing excessive dimensionality from categorical encoding
8. Scale features using StandardScaler
9. Ensure all remaining columns are numerical
10. Preserve the most informative features for PCA

------------------------------------------------------------
CATEGORICAL FEATURE RULES
------------------------------------------------------------
- One-hot encode low-cardinality categorical columns
- Remove extremely high-cardinality categorical columns
- Avoid encoding columns that behave like unique identifiers
- Boolean columns may be converted to 0/1

------------------------------------------------------------
NUMERICAL FEATURE RULES
------------------------------------------------------------
- Handle missing numerical values appropriately
- Ensure numerical stability
- Remove highly problematic columns if necessary
- Standardize all numerical features before final output

------------------------------------------------------------
STRICT CONSTRAINTS
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
    - include PCA fitting/training code
    - visualize data

OUTPUT:
Return ONLY executable Python code.
"""


def build_time_series_prompt(df: pd.DataFrame) -> str:
    buffer = io.StringIO()
    df.info(buf=buffer)
    info_string = buffer.getvalue()

    return f"""
You are a senior data preprocessing expert preparing data for time series forecasting and temporal analysis.

DATASET INFO:
{info_string}

STATISTICAL SUMMARY:
{df.describe(include='all').to_string()}

SAMPLE ROWS:
{df.head(5).to_string()}

OBJECTIVE:
Transform this dataset into a CLEAN chronological time series dataset suitable for forecasting algorithms such as:
- Linear Regression Time Series
- ARIMA
- Future forecasting models

The final dataset must preserve temporal ordering and contain:
- EXACTLY ONE datetime column
- EXACTLY ONE primary target variable for forecasting
- clean chronological observations
- properly handled missing temporal values

FINAL OUTPUT REQUIREMENTS:
- Final dataframe variable must be named: df
- Final dataframe must contain:
    • one datetime column
    • one primary numerical target column
- Final dataframe must be sorted chronologically
- Final dataframe must contain NO invalid timestamps
- Final dataframe must contain NO duplicate timestamps
- Final dataframe must contain NO completely missing target values
- Final dataframe must be directly usable for forecasting models

------------------------------------------------------------
TIME SERIES STRUCTURE RULES
------------------------------------------------------------

The final dataframe should represent:

- rows = chronological observations
- datetime column = temporal index
- target column = variable to forecast

The preprocessing pipeline must preserve:
- temporal order
- sequential consistency
- forecasting integrity

NEVER shuffle the data.

------------------------------------------------------------
DATETIME COLUMN DETECTION RULE
------------------------------------------------------------

Detect the BEST datetime column by prioritizing:
1. timestamp columns
2. datetime columns
3. date columns
4. temporal index-like columns

Convert the selected column into pandas datetime format.

STRICT RULES:
- Keep ONLY ONE datetime column
- Remove redundant temporal columns
- Remove rows with invalid timestamps
- Remove timezone inconsistencies if necessary

------------------------------------------------------------
TARGET COLUMN SELECTION RULE
------------------------------------------------------------

Select EXACTLY ONE primary forecasting target column.

Priority:
1. continuous numerical measurements
2. sales/price/count/temperature/sensor-like variables
3. aggregated metrics over identifiers

DO NOT select:
- IDs
- UUIDs
- indexes
- categorical labels
- text columns
- near-unique identifiers

If multiple valid numerical columns exist:
- choose the most meaningful continuous variable
- remove irrelevant numerical metadata columns if necessary

------------------------------------------------------------
COLUMN CLASSIFICATION RULE
------------------------------------------------------------

Classify columns into:

1. DATETIME COLUMN (KEEP ONLY ONE)
2. TARGET COLUMN (KEEP ONLY ONE)
3. AUXILIARY FEATURES (OPTIONAL):
   - lag-safe numerical features
   - low-cardinality temporal helpers
4. REMOVE ALWAYS:
   - IDs
   - UUIDs
   - hashes
   - names
   - free text
   - extremely sparse columns
   - leakage columns
   - future-dependent columns

------------------------------------------------------------
MISSING VALUE RULES
------------------------------------------------------------

- Handle missing timestamps appropriately
- Handle missing target values using:
    • interpolation
    • forward fill
    • backward fill

Avoid aggressive row dropping unless necessary.

------------------------------------------------------------
TIME SERIES CLEANING RULES
------------------------------------------------------------

1. Sort chronologically
2. Remove duplicate timestamps
3. Remove constant columns
4. Remove highly irrelevant metadata
5. Ensure datetime parsing consistency
6. Preserve sequential integrity
7. Avoid data leakage
8. Preserve temporal granularity
9. Ensure target column is numerical
10. Ensure dataframe is forecasting-ready

------------------------------------------------------------
OPTIONAL FEATURE ENGINEERING
------------------------------------------------------------

You MAY create useful temporal features ONLY if beneficial:
- year
- month
- day
- weekday
- hour
- quarter

BUT:
- avoid excessive feature creation
- avoid exploding dimensionality
- preserve forecasting simplicity

------------------------------------------------------------
STRICT CONSTRAINTS
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
    - include forecasting model code
    - include ARIMA code
    - include plotting code
    - shuffle rows

OUTPUT:
Return ONLY executable Python code.

The final dataframe MUST remain assigned to:
    df
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


def get_prompt_for_method_type(method_type: str) -> str:
    if method_type == MethodType.CLUSTERING:
        return build_clustering_prompt
    elif method_type == MethodType.ASSOCIATION_RULE:
        return build_association_rule_prompt
    elif method_type == MethodType.PCA:
        return build_pca_prompt
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


def build_report_prompt(
    df: pd.DataFrame,
    schema: dict[str, object],
    algorithms: list[dict[str, object]],
) -> str:
    schema_json = json.dumps(schema, indent=2)
    algorithms_json = json.dumps(algorithms, indent=2)

    return f"""
You are a data science analyst writing a concise report.

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
- For each algorithm section, summarize parameters, measures, outputs, and notes.
- If an item is missing, say "Not provided".
- Keep the report concise and clear.
- Use GitHub-flavored Markdown tables where tabular data is presented.
- Put a blank line before and after each table.
- Each table row must be on its own line and start with "|".
- Always include all five sections, even if they contain only "Not provided".
- Use the exact heading text shown in the template below.
- Add analysis that is NOT a restatement of inputs:
    - Data quality: missingness, obvious ID columns to exclude, duplicates if inferable from schema.
    - Statistical notes: outlier-prone ranges, skew or scale differences visible in summary.
    - Algorithm interpretation: why the best algorithm likely won; what the metrics imply.
    - Actionable next steps: what to try next (e.g., normalize, remove ID, tune parameters).
- Be specific when possible; avoid generic advice.

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
