"""Build repeat-detention Sankey data from raw or cleaned detention stays data."""

import argparse
import json
from pathlib import Path

import pandas as pd

BASE = Path(__file__).parent
STAYS_CSV = BASE / "deportation_data_project_src" / "detention-stays-latest.csv"
PARTNER_XLSX = BASE / "super mini cleaned df.xlsx"
OUTPUT_JSON = BASE.parent.parent / "public" / "data" / "repeatDetentionSankey.json"

PROGRAM_MAP = {
    "Border Patrol": "Border Patrol",
    "ERO Criminal Alien Program": "Criminal Referral",
    "ERO Non-Criminal Alien Program": "ICE Arrest",
    "Non-Criminal Alien Removal Program": "ICE Arrest",
    "Asylum": "Asylum Intake",
    "Parole": "Asylum Intake",
}


def normalize_program(value):
    value = str(value).strip()
    if not value or value.lower() == "nan":
        return "Unknown"
    if value in PROGRAM_MAP:
        return PROGRAM_MAP[value]
    if "Criminal Alien" in value:
        return "Criminal Referral"
    if "Non-Criminal" in value:
        return "ICE Arrest"
    return value


def normalize_outcome(value):
    value = str(value).strip()
    if not value or value.lower() == "nan":
        return "Still Detained"

    lowered = value.lower()
    if "removed" in lowered or "voluntary return" in lowered or "deported" in lowered:
        return "Removed"
    if (
        "bond" in lowered
        or "recognizance" in lowered
        or "released" in lowered
        or "humanitarian" in lowered
        or "paroled" in lowered
        or "supervision" in lowered
    ):
        return "Released"
    if "transfer" in lowered:
        return "Transferred"
    return "Released"


def resolve_column(df, candidates, label):
    for candidate in candidates:
        if candidate in df.columns:
            return candidate
    raise ValueError(f"Missing {label} column. Tried: {candidates}")


def load_input_dataframe(input_path):
    input_path = Path(input_path)
    suffix = input_path.suffix.lower()

    if suffix == ".csv":
        return pd.read_csv(input_path, low_memory=False)
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(input_path)

    raise ValueError(f"Unsupported input file type: {input_path.suffix}")


def build_repeat_detention_sankey(df, min_stays=2):
    person_col = resolve_column(
        df,
        ["detainee_unique_identifier", "unique_identifier"],
        "person identifier",
    )
    time_col = resolve_column(df, ["stay_book_in_date_time"], "stay timestamp")
    program_col = resolve_column(df, ["final_program"], "program")
    outcome_col = resolve_column(df, ["stay_release_reason"], "outcome")

    working_df = df[[person_col, time_col, program_col, outcome_col]].copy()

    working_df[person_col] = working_df[person_col].astype(str).str.strip()
    working_df = working_df[working_df[person_col].ne("")]
    working_df[time_col] = pd.to_datetime(
        working_df[time_col],
        utc=True,
        errors="coerce",
    )
    working_df = working_df.dropna(subset=[person_col, time_col])

    working_df["program_stage"] = working_df[program_col].apply(normalize_program)
    working_df["outcome_stage"] = working_df[outcome_col].apply(normalize_outcome)

    stay_counts = working_df[person_col].value_counts()
    repeat_ids = stay_counts[stay_counts >= min_stays].index
    repeat_df = working_df[working_df[person_col].isin(repeat_ids)].copy()
    repeat_df = repeat_df.sort_values([person_col, time_col])

    grouped = repeat_df.groupby(person_col, sort=False)
    repeat_df["next_program_stage"] = grouped["program_stage"].shift(-1)
    transitions_df = repeat_df.dropna(subset=["next_program_stage"]).copy()

    links_map = {}
    node_names = []
    node_seen = set()

    def register_node(name):
        if name not in node_seen:
            node_seen.add(name)
            node_names.append(name)

    def bump_link(source, target):
        register_node(source)
        register_node(target)
        key = (source, target)
        if key not in links_map:
            links_map[key] = {"source": source, "target": target, "value": 0}
        links_map[key]["value"] += 1

    for _, row in transitions_df.iterrows():
        current_program = f"Stay N Program: {row['program_stage']}"
        current_outcome = f"Stay N Outcome: {row['outcome_stage']}"
        next_program = f"Stay N+1 Program: {row['next_program_stage']}"

        bump_link(current_program, current_outcome)
        bump_link(current_outcome, next_program)

    links = sorted(
        links_map.values(),
        key=lambda link: (-link["value"], link["source"], link["target"]),
    )
    nodes = [{"name": name} for name in node_names]

    return {
        "nodes": nodes,
        "links": links,
        "metadata": {
            "repeat_people": int(len(repeat_ids)),
            "transitions": int(len(transitions_df)),
            "min_stays": int(min_stays),
            "person_column": person_col,
            "time_column": time_col,
            "program_column": program_col,
            "outcome_column": outcome_col,
        },
    }


def parse_args():
    parser = argparse.ArgumentParser(
        description="Build repeat-detention Sankey JSON from raw or cleaned detention stays data.",
    )
    parser.add_argument(
        "--input",
        dest="input_path",
        default=str(STAYS_CSV),
        help="Path to a CSV/XLSX detention stays dataset. Supports raw and cleaned schemas.",
    )
    parser.add_argument(
        "--output",
        dest="output_path",
        default=str(OUTPUT_JSON),
        help="Path to write the Sankey JSON output.",
    )
    parser.add_argument(
        "--min-stays",
        dest="min_stays",
        type=int,
        default=2,
        help="Minimum number of stays required for a person to be included.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    input_path = Path(args.input_path)
    output_path = Path(args.output_path)

    print(f"Reading detention data for repeat-detention Sankey from {input_path.name} ...")
    df = load_input_dataframe(input_path)
    print(f"  {len(df):,} rows loaded")

    sankey_data = build_repeat_detention_sankey(df, min_stays=args.min_stays)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file_handle:
        json.dump(sankey_data, file_handle, separators=(",", ":"))

    print(
        "\n✓  Wrote "
        f"{output_path.name} "
        f"({len(sankey_data['nodes']):,} nodes, {len(sankey_data['links']):,} links, "
        f"{sankey_data['metadata']['transitions']:,} transitions)"
    )


if __name__ == "__main__":
    main()