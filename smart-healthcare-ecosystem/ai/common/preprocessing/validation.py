from __future__ import annotations

import pandas as pd


def validate_columns(
    dataframe: pd.DataFrame,
    required_columns: set[str],
) -> None:
    missing = required_columns - set(
        dataframe.columns
    )

    if missing:
        raise ValueError(
            f"Missing required columns: "
            f"{sorted(missing)}"
        )