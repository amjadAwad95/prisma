import json
import pandas as pd
import io


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


def get_association_rule_prompt_builder() -> callable:
    def _builder(df: pd.DataFrame) -> str:
        return build_association_rule_prompt(df)

    return _builder


def build_association_insights_prompt(facts: dict[str, object]) -> str:
    facts_json = json.dumps(facts, indent=2)
    return (
        "You are a data analyst writing short, plain-English insights for non-technical users.\n"
        "Use only the provided facts. Do not mention algorithm names.\n"
        "Return ONLY a JSON array of strings.\n\n"
        f"FACTS:\n{facts_json}\n\n"
        "RULES:\n"
        "- Start with the summary sentence from the facts.\n"
        "- Turn each rule into a practical, actionable suggestion.\n"
        "- Be explicit about the action: place together, bundle, recommend, cross-sell.\n"
        "- If multiple items exist, mention 1-2 items max per side.\n"
        "- Use short sentences, avoid numbers or metrics like confidence/lift.\n"
        "- Keep it very clear for non-technical users.\n"
    )
