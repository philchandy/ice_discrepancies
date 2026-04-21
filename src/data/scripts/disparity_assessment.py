"""
Utilities for building a weighted disparity/favorability score for detention outcomes.

This module is intended to work row-wise on ``clean_detention_stays_df`` and supports
custom weighting across the four requested attributes:
    - domestic_miles_traveled (lower is better)
    - days_in_detention (lower is better)
    - bond_posted_amount_usd (None/missing is best, higher is worse)
    - detention_release_reason_most_general (mapped to badness 1-10)
"""

from __future__ import annotations

import numpy as np
import pandas as pd

DEFAULT_RELEASE_REASON_BADNESS = {
    "Departure / Deportation": 8,
    "Detention": 5,
    "Died": 10,
    "Escape": 5,
    "Released (long-term stay in USA likely)": 1,
    "Released temporarily (long-term stay in USA possible)": 2,
    "Released with no status change (further proceedings likely)": 4,
    "Unknown": 5,
}

DEFAULT_WEIGHTS = {
    "domestic_miles_traveled": 0.25,
    "days_in_detention": 0.25,
    "bond_posted_amount_usd": 0.25,
    "detention_release_reason_most_general": 0.25,
}


# -----------------------------
# Core helpers
# -----------------------------
def _normalize_series_to_badness_0_1(series: pd.Series, lower_is_better: bool = True) -> pd.Series:
    """
    Min-max normalize numeric data to a 0..1 badness score.

    0 = most favorable, 1 = least favorable.
    When all non-null values are identical, returns 0 for non-null rows.
    """

    numeric = pd.to_numeric(series, errors="coerce")
    min_val = numeric.min(skipna=True)
    max_val = numeric.max(skipna=True)

    if pd.isna(min_val) or pd.isna(max_val):
        return pd.Series(np.nan, index=series.index)

    if max_val == min_val:
        out = pd.Series(0.0, index=series.index)
        out[numeric.isna()] = np.nan
        return out

    scaled = (numeric - min_val) / (max_val - min_val)
    if lower_is_better:
        return scaled

    # For completeness: if higher is better, invert to convert to badness.
    return 1 - scaled


def _build_bond_badness(series: pd.Series) -> pd.Series:
    """
    Build badness score for bond amount where:
    - missing/None -> best (0 badness)
    - higher numeric amount -> worse (approaches 1)
    """

    numeric = pd.to_numeric(series, errors="coerce")

    # Missing is explicitly best.
    filled = numeric.fillna(0)

    max_val = filled.max(skipna=True)
    if pd.isna(max_val) or max_val == 0:
        return pd.Series(0.0, index=series.index)

    return filled / max_val


def _normalize_weights(weight_map: dict[str, float]) -> dict[str, float]:
    """Return a copy of weights normalized to sum to 1."""

    weight_series = pd.Series(weight_map, dtype="float64")
    if (weight_series < 0).any():
        raise ValueError("Weights must be non-negative.")

    total = weight_series.sum()
    if total <= 0:
        raise ValueError("At least one weight must be greater than 0.")

    return (weight_series / total).to_dict()


# -----------------------------
# Public API
# -----------------------------
def add_outcome_disparity_score(
    df: pd.DataFrame,
    weights: dict[str, float] | None = None,
    release_reason_badness: dict[str, float] | None = None) -> pd.DataFrame:
    """
    Add a weighted row-wise outcome disparity/favorability score.

    The returned score is on a 0..1 scale where:
        - 0 is most favorable
        - 1 is least favorable

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing required columns.
    weights : dict[str, float] | None
        Relative weights for the four attributes. Values can be any non-negative
        numbers and are normalized to sum to 1.
    release_reason_badness : dict[str, float] | None
        Optional override map for ``detention_release_reason_most_general``.
        Expected scale is typically 1..10 where higher is worse.

    Returns
    -------
    pd.DataFrame
        Copy of ``df`` with helper badness columns and outcome_disparity_score column.
    """

    required_cols = [
        "domestic_miles_traveled",
        "days_in_detention",
        "bond_posted_amount_usd",
        "detention_release_reason_most_general",
    ]

    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"DataFrame is missing required columns: {missing}")

    reason_badness = release_reason_badness or DEFAULT_RELEASE_REASON_BADNESS
    use_weights = _normalize_weights(weights or DEFAULT_WEIGHTS)

    for feature_name in required_cols:
        if feature_name not in use_weights:
            raise ValueError(f"Missing weight for feature '{feature_name}'.")

    out = df.copy()

    out["badness_domestic_miles_traveled"] = _normalize_series_to_badness_0_1(
        out["domestic_miles_traveled"], lower_is_better=True
    )
    out["badness_days_in_detention"] = _normalize_series_to_badness_0_1(
        out["days_in_detention"], lower_is_better=True
    )
    out["badness_bond_posted_amount_usd"] = _build_bond_badness(out["bond_posted_amount_usd"])

    reason_raw = out["detention_release_reason_most_general"].map(reason_badness)
    reason_numeric = pd.to_numeric(reason_raw, errors="coerce")
    # 1..10 -> 0..1 badness
    out["badness_detention_release_reason_most_general"] = (reason_numeric - 1) / 9

    # Weighted score (NaN badness values are treated neutrally as 0 in this sum).
    out["outcome_disparity_score"] = (
        out["badness_domestic_miles_traveled"].fillna(0) * use_weights["domestic_miles_traveled"]
        + out["badness_days_in_detention"].fillna(0) * use_weights["days_in_detention"]
        + out["badness_bond_posted_amount_usd"].fillna(0) * use_weights["bond_posted_amount_usd"]
        + out["badness_detention_release_reason_most_general"].fillna(0)
        * use_weights["detention_release_reason_most_general"]
    )

    return out


if __name__ == "__main__":
    clean_detention_stays_df = pd.read_pickle(r"assets/deportation_data_project/detention_stays_df.pkl")

    custom_weights = {
        "domestic_miles_traveled": 0.20,
        "days_in_detention": 0.35,
        "bond_posted_amount_usd": 0.20,
        "detention_release_reason_most_general": 0.25,
    }

    scored = add_outcome_disparity_score(clean_detention_stays_df, weights=custom_weights)
    print(scored[["outcome_disparity_score"]].describe())
