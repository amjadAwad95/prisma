import json
import pandas as pd
import io


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
