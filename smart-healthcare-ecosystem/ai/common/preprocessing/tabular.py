from __future__ import annotations

import pandas as pd


def clean_numeric_columns(
    dataframe: pd.DataFrame,
    columns: list[str],
) -> pd.DataFrame:
    result = dataframe.copy()

    for column in columns:
        if column not in result.columns:
            raise ValueError(
                f"Column not found: {column}"
            )

        result[column] = pd.to_numeric(
            result[column],
            errors="coerce",
        )

    result = result.dropna(
        subset=columns
    )

    return result.reset_index(
        drop=True
    )