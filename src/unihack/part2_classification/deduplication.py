from __future__ import annotations

import pandas as pd


def find_duplicate_candidates(
    df: pd.DataFrame,
) -> pd.DataFrame:

    required_columns = {
        "Mfg_Part_Num",
        "Part_Desc",
    }

    missing = (
        required_columns
        - set(df.columns)
    )

    if missing:

        raise ValueError(
            "Missing required columns: "
            f"{sorted(missing)}"
        )

    working = df.copy()

    working["_mpn_key"] = (
        working[
            "Mfg_Part_Num"
        ]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
    )

    duplicates = (
        working[
            working.duplicated(
                subset="_mpn_key",
                keep=False,
            )
        ]
        .copy()
    )

    return duplicates.drop(
        columns="_mpn_key"
    )