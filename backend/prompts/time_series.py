import json
import pandas as pd
import io


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


def build_time_series_insights_prompt(facts: dict[str, object]) -> str:
    facts_json = json.dumps(facts, indent=2)
    return (
        "You are a data analyst writing short, plain-English insights for non-technical users.\n"
        "Use only the provided facts. Do not mention algorithm names.\n"
        "Return ONLY a JSON array of strings.\n\n"
        f"FACTS:\n{facts_json}\n\n"
        "RULES:\n"
        "- Start with the summary sentence from the facts.\n"
        "- Describe the recent direction and the forecast direction.\n"
        "- If forecast points are provided, mention the next points with their dates.\n"
        "- Avoid technical metrics and avoid percentages.\n"
        "- Keep sentences short and clear.\n"
    )
