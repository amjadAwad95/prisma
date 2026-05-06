import pandas as pd
import re
from pathlib import Path
from collections.abc import Callable

from models.base_model import BaseModel
from utils.read_file import read_file


class Preprocessing:
    def preprocess(
        self,
        file_path: str,
        prompt_fun: Callable,
        model: BaseModel,
        error_message: str | None = None,
    ) -> pd.DataFrame:
        dataframe = read_file(file_path)

        prompt = prompt_fun(dataframe)

        if error_message:
            prompt = (
                f"{prompt}\n\n"
                "The previous attempt failed with this error:\n"
                f"{error_message}\n"
                "Please fix the code and return only Python code that assigns the result to `df`."
            )

        code = model.generate(prompt=prompt)

        code = re.sub(r"^```(?:python)?\s*", "", code.strip(), flags=re.MULTILINE)
        code = re.sub(r"```$", "", code.strip(), flags=re.MULTILINE)

        ALLOWED = {"pandas", "numpy", "sklearn", "scikit-learn"}

        import_lines = re.findall(
            r"^\s*(?:import|from)\s+([\w]+)", code, flags=re.MULTILINE
        )

        for lib in import_lines:
            if lib not in ALLOWED:
                raise RuntimeError(
                    f"Forbidden import detected: `{lib}`. "
                    f"Only pandas, numpy, and sklearn are allowed."
                )

        output_path = Path("preprocessed") / file_path.replace("uploads/", "")

        sandbox = {
            "input_path": file_path,
            "df": None,
        }

        try:
            exec(code, sandbox)
        except Exception as e:
            raise RuntimeError(f"Code execution failed: {e}") from e

        df = sandbox.get("df")

        if df is None:
            raise RuntimeError(
                "Agent code did not assign a result to `df`. "
                "The code must end with: df = <your preprocessed dataframe>"
            )

        if not isinstance(df, pd.DataFrame):
            raise RuntimeError(
                f"Expected `df` to be a DataFrame, got {type(df).__name__}"
            )

        if df.empty:
            raise RuntimeError("The preprocessed DataFrame is empty.")

        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)

        return output_path

    def run(
        self,
        file_path: str,
        prompt_fun: Callable,
        model: BaseModel,
        max_retries: int = 3,
    ) -> pd.DataFrame:
        error_message = None

        for attempt in range(1, max_retries + 1):
            try:
                return self.preprocess(
                    file_path=file_path,
                    prompt_fun=prompt_fun,
                    model=model,
                    error_message=error_message,
                )
            except RuntimeError as e:
                error_message = str(e)

                if attempt == max_retries:
                    raise
