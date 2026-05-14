import json
import pandas as pd
import io


def build_clustering_prompt_for_algorithm(
    df: pd.DataFrame,
    algorithm: str,
    params: dict[str, object] | None = None,
) -> str:
    buffer = io.StringIO()
    df.info(buf=buffer)
    info_string = buffer.getvalue()

    params_line = ""
    if params:
        params_line = f"\nALGORITHM PARAMETERS:\n{params}"

    return f"""
You are a senior data preprocessing expert preparing data specifically for clustering analysis.

CLUSTERING ALGORITHM:
{algorithm}{params_line}

DATASET INFO:
{info_string}

STATISTICAL SUMMARY:
{df.describe(include='all').to_string()}

SAMPLE ROWS:
{df.head(5).to_string()}

OBJECTIVE:
Transform this dataset into a CLEAN numerical feature matrix optimized for clustering.

The preprocessing pipeline must preserve meaningful cluster structure while removing noise, redundancy, and harmful features.

FINAL OUTPUT REQUIREMENTS:
- Final dataframe variable must be named: df
- Final dataframe must contain ONLY numeric features
- Final dataframe must contain NO missing values
- Final dataframe must be properly scaled/normalized for clustering
- Final dataframe must be directly usable for clustering algorithms
- Preserve informative variance and cluster separability

------------------------------------------------------------
CLUSTERING PREPROCESSING STRATEGY
------------------------------------------------------------
Before preprocessing, analyze the dataset carefully and determine:

1. FEATURE RELEVANCE
   - Remove irrelevant columns
   - Remove IDs, UUIDs, indexes
   - Remove constant or near-constant columns
   - Remove duplicated columns if necessary

2. DATA TYPE HANDLING
   - Numerical columns:
       • impute missing values appropriately
       • scale or normalize when required
       • handle skewness/outliers if necessary

   - Categorical columns:
       • encode appropriately
       • remove high-cardinality categorical columns if harmful
       • preserve meaningful categorical information

3. MISSING VALUE STRATEGY
   - Handle missing values appropriately based on column type
   - Avoid dropping excessive rows unless necessary

4. FEATURE SCALING
   - Apply scaling appropriate for distance-based clustering
   - Prefer:
       • StandardScaler
       • MinMaxScaler
       • RobustScaler
     depending on data characteristics

5. DIMENSIONALITY REDUCTION
   - Remove redundant/highly correlated features if needed
   - Apply PCA only if beneficial for clustering quality

6. OUTLIER HANDLING
   - Detect and handle severe outliers if they would distort clustering
   - Avoid aggressive filtering unless justified

------------------------------------------------------------
ALGORITHM-AWARE PREPROCESSING RULES
------------------------------------------------------------
Adjust preprocessing according to the clustering algorithm:

- KMeans / Agglomerative / Spectral:
    • strong scaling required
    • remove extreme outliers
    • avoid sparse noisy dimensions

- DBSCAN:
    • scaling is critical
    • noise/outlier handling is very important

- Gaussian Mixture:
    • preserve continuous distributions
    • avoid excessive discretization

- Hierarchical Clustering:
    • reduce redundant correlated features

------------------------------------------------------------
COLUMN CLASSIFICATION RULE
------------------------------------------------------------
Classify columns into:

1. USEFUL FEATURES
   - informative numerical/categorical variables

2. REMOVE ALWAYS
   - IDs
   - UUIDs
   - row indexes
   - free-text columns
   - URLs/emails
   - timestamps unless engineered meaningfully

3. CONDITIONAL FEATURES
   - high-cardinality categoricals
   - highly sparse columns
   - leakage features

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
    - include clustering code

OUTPUT:
Return ONLY executable Python code.
"""


def get_clustering_prompt_builder(
    algorithm: str, params: dict[str, object] | None = None
) -> callable:
    def _builder(df: pd.DataFrame) -> str:
        return build_clustering_prompt_for_algorithm(df, algorithm, params)

    return _builder


def build_cluster_insights_prompt(facts: dict[str, object]) -> str:
    facts_json = json.dumps(facts, indent=2)
    return (
        "You are a data analyst writing short, plain-English insights for non-technical users.\n"
        "Use only the provided facts. Do not mention algorithm names.\n"
        "Return ONLY a JSON array of strings.\n\n"
        f"FACTS:\n{facts_json}\n\n"
        "RULES:\n"
        "- First sentence must be the summary from the facts.\n"
        "- Use simple words like higher/lower, more/less likely.\n"
        "- Keep decimals to at most 2 digits.\n"
        "- Prefer 1 to 3 features per cluster.\n"
        "- If a cluster has no highlights, say it looks similar to overall.\n"
    )
