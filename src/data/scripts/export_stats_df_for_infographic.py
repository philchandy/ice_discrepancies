"""Build infographic-ready stats JSON from a cleaned detention stays pickle.

Usage:
  python src/export_stats_df_for_infographic.py
  python src/export_stats_df_for_infographic.py \
    --cleaned-stays-pickle assets/deportation_data_project/detention_stays_df.pkl \
    --json-output src/stats_df.json

Optional:
  --stats-csv-output /tmp/stats_df.csv   # also export the computed stats dataframe
"""

from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path

import pandas as pd

from detention_data_cleaning import (
    clean_detention_stays_into_stats_df_spec,
    get_person_level_outcomes_df_from_cleaned_stays_df,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def normalize_distribution(value):
    if isinstance(value, dict):
        return value
    if pd.isna(value):
        return {}
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            # Handles values serialized like "{2: 7, 3: 14}" (python dict repr)
            try:
                parsed = ast.literal_eval(value)
                return parsed if isinstance(parsed, dict) else {}
            except (SyntaxError, ValueError):
                return {}
    return {}


def build_stats_df(cleaned_stays_pickle: Path) -> pd.DataFrame:
    cleaned_stays_df = pd.read_pickle(cleaned_stays_pickle)
    outcomes_df, troubleshoot = get_person_level_outcomes_df_from_cleaned_stays_df(cleaned_stays_df)
    stats_df = clean_detention_stays_into_stats_df_spec(cleaned_stays_df, outcomes_df)
    return stats_df


def resolve_input_path(path: Path) -> Path:
    """
    Resolve input paths robustly when script is invoked from arbitrary working directories.

    Priority for relative paths:
    1) current working directory
    2) repository root (parent of src/)
    """
    if path.is_absolute():
        return path

    cwd_candidate = (Path.cwd() / path).resolve()
    if cwd_candidate.exists():
        return cwd_candidate

    repo_candidate = (REPO_ROOT / path).resolve()
    if repo_candidate.exists():
        return repo_candidate

    # Fall back to repo-root resolution for deterministic messaging.
    return repo_candidate


def export_json(stats_df: pd.DataFrame, json_output: Path) -> None:
    if stats_df.columns.duplicated().any():
        duplicate_cols = stats_df.columns[stats_df.columns.duplicated()].tolist()
        raise ValueError(
            "stats_df contains duplicate column names, which breaks JSON export. "
            f"Duplicate columns: {duplicate_cols}"
        )

    if "age_distribution" in stats_df.columns:
        stats_df["age_distribution"] = stats_df["age_distribution"].apply(normalize_distribution)
    if "crime_distribution" in stats_df.columns:
        stats_df["crime_distribution"] = stats_df["crime_distribution"].apply(normalize_distribution)

    records = json.loads(stats_df.to_json(orient="records"))
    json_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(records, indent=2), encoding="utf-8")
    print(f"Wrote {len(records)} records to {json_output}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--cleaned-stays-pickle",
        type=Path,
        default=Path("assets/deportation_data_project/detention_stays_df.pkl"),
        help="Path to cleaned detention stays pickle (input to clean_detention_stays_into_stats_df)",
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("src/stats_df.json"),
        help="Output JSON path for infographic.html",
    )
    parser.add_argument(
        "--stats-csv-output",
        type=Path,
        default=None,
        help="Optional output path for stats_df CSV",
    )
    args = parser.parse_args()

    resolved_cleaned_stays_pickle = resolve_input_path(args.cleaned_stays_pickle)

    if not resolved_cleaned_stays_pickle.exists():
        raise FileNotFoundError(
            f"Could not find cleaned stays pickle at: {resolved_cleaned_stays_pickle}\n"
            f"Current working directory: {Path.cwd()}\n"
            "Pass --cleaned-stays-pickle with the correct path."
        )

    stats_df = build_stats_df(resolved_cleaned_stays_pickle)

    if args.stats_csv_output is not None:
        args.stats_csv_output.parent.mkdir(parents=True, exist_ok=True)
        stats_df.to_csv(args.stats_csv_output, index=False)
        print(f"Wrote stats dataframe ({len(stats_df)} rows) to {args.stats_csv_output}")

    export_json(stats_df, args.json_output)


if __name__ == "__main__":
    main()
