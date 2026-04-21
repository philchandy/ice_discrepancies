"""Build Sankey links from conviction-charge-general to detention-release-reason-most-general."""

import json
from pathlib import Path

import pandas as pd

BASE = Path(__file__).parent
INPUT_XLSX = BASE / "super mini cleaned df.xlsx"
OUTPUT_JSON = BASE.parent.parent / "public" / "data" / "convictionReleaseSankey.json"

SOURCE_COL = "most_serious_conviction_charge_general"
TARGET_COL = "detention_release_reason_most_general"


def normalize(value, default_label):
    text = str(value).strip()
    if not text or text.lower() == "nan":
        return default_label
    return text


def build_sankey(df):
    if SOURCE_COL not in df.columns or TARGET_COL not in df.columns:
        raise ValueError(
            f"Input data must include columns '{SOURCE_COL}' and '{TARGET_COL}'."
        )

    links_map = {}
    node_names = []
    seen = set()

    def register(name):
        if name not in seen:
            seen.add(name)
            node_names.append(name)

    for _, row in df.iterrows():
        source = f"Conviction: {normalize(row[SOURCE_COL], 'No criminal history')}"
        target = f"Release: {normalize(row[TARGET_COL], 'Unknown')}"

        register(source)
        register(target)

        key = (source, target)
        if key not in links_map:
            links_map[key] = {"source": source, "target": target, "value": 0}
        links_map[key]["value"] += 1

    links = sorted(
        links_map.values(),
        key=lambda link: (-link["value"], link["source"], link["target"]),
    )
    nodes = [{"name": name} for name in node_names]

    return {
        "nodes": nodes,
        "links": links,
        "metadata": {
            "source_column": SOURCE_COL,
            "target_column": TARGET_COL,
            "rows": int(len(df)),
        },
    }


def main():
    print(f"Reading {INPUT_XLSX.name} ...")
    df = pd.read_excel(INPUT_XLSX)
    print(f"  {len(df):,} rows loaded")

    sankey_data = build_sankey(df)

    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_JSON.open("w", encoding="utf-8") as fh:
        json.dump(sankey_data, fh, separators=(",", ":"))

    print(
        f"\nWrote {OUTPUT_JSON.name} "
        f"({len(sankey_data['nodes']):,} nodes, {len(sankey_data['links']):,} links)"
    )


if __name__ == "__main__":
    main()
