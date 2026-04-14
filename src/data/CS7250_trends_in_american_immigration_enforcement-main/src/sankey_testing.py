import pandas as pd
import pandas as pd
import plotly.graph_objects as go


import pandas as pd
import plotly.graph_objects as go


import pandas as pd
import plotly.graph_objects as go


def plot_repeat_detention_sankey(df, max_stays=4):
    """
    Cleaner Sankey flow:
    first conviction -> first release ->
    Detained -> second release ->
    Detained -> third release ->
    ...

    Assumes df has:
    - detainee_unique_identifier
    - most_serious_conviction_charge_general
    - detention_release_reason_general
    - detention_release_reason_general2 ...
    """

    stage_cols = ["most_serious_conviction_charge_general", "detention_release_reason_general"]

    for i in range(2, max_stays + 1):
        rel_col = f"detention_release_reason_general{i}"
        if rel_col in df.columns:
            stage_cols.append(rel_col)

    sankey_df = df[["detainee_unique_identifier"] + stage_cols].copy()

    for c in stage_cols:
        sankey_df[c] = sankey_df[c].astype("string").str.strip()

    labels = []
    label_to_index = {}
    sources = []
    targets = []
    values = []

    def get_node_index(label):
        if label not in label_to_index:
            label_to_index[label] = len(labels)
            labels.append(label)
        return label_to_index[label]

    # ------------------------------------------------------------
    # 1. First conviction -> first release
    # ------------------------------------------------------------
    flow_df = sankey_df[
        [
            "detainee_unique_identifier",
            "most_serious_conviction_charge_general",
            "detention_release_reason_general",
        ]
    ].copy()

    flow_df = flow_df[
        flow_df["most_serious_conviction_charge_general"].notna() &
        flow_df["detention_release_reason_general"].notna()
    ]

    flow_df = (
        flow_df.groupby(
            ["most_serious_conviction_charge_general", "detention_release_reason_general"]
        )["detainee_unique_identifier"]
        .nunique()
        .reset_index(name="count")
    )

    for _, row in flow_df.iterrows():
        source_idx = get_node_index(f"First conviction: {row['most_serious_conviction_charge_general']}")
        target_idx = get_node_index(f"First release: {row['detention_release_reason_general']}")
        sources.append(source_idx)
        targets.append(target_idx)
        values.append(row["count"])

    # ------------------------------------------------------------
    # 2. For each later stay:
    #    previous release -> Detained -> next release
    # ------------------------------------------------------------
    for i in range(2, max_stays + 1):
        prev_rel_col = "detention_release_reason_general" if i == 2 else f"detention_release_reason_general{i-1}"
        curr_rel_col = f"detention_release_reason_general{i}"

        if curr_rel_col not in sankey_df.columns:
            continue

        # Only people who actually have another stay should continue
        loop_df = sankey_df[
            ["detainee_unique_identifier", prev_rel_col, curr_rel_col]
        ].copy()

        loop_df = loop_df[
            loop_df[prev_rel_col].notna() &
            loop_df[curr_rel_col].notna()
        ]

        if loop_df.empty:
            continue

        detained_label = f"Detained again before stay {i}"

        # previous release -> Detained
        left_flow = (
            loop_df.groupby(prev_rel_col)["detainee_unique_identifier"]
            .nunique()
            .reset_index(name="count")
        )

        for _, row in left_flow.iterrows():
            if i == 2:
                prev_release_label = f"First release: {row[prev_rel_col]}"
            else:
                prev_release_label = f"Release {i-1}: {row[prev_rel_col]}"

            source_idx = get_node_index(prev_release_label)
            target_idx = get_node_index(detained_label)
            sources.append(source_idx)
            targets.append(target_idx)
            values.append(row["count"])

        # Detained -> current release
        right_flow = (
            loop_df.groupby(curr_rel_col)["detainee_unique_identifier"]
            .nunique()
            .reset_index(name="count")
        )

        for _, row in right_flow.iterrows():
            curr_release_label = f"Release {i}: {row[curr_rel_col]}"
            source_idx = get_node_index(detained_label)
            target_idx = get_node_index(curr_release_label)
            sources.append(source_idx)
            targets.append(target_idx)
            values.append(row["count"])

    fig = go.Figure(
        data=[
            go.Sankey(
                arrangement="snap",
                node=dict(
                    pad=18,
                    thickness=18,
                    line=dict(width=0.5),
                    label=labels,
                ),
                link=dict(
                    source=sources,
                    target=targets,
                    value=values,
                ),
            )
        ]
    )

    fig.update_layout(
        title_text="First Conviction → Release → Repeat Detention → Later Releases",
        font_size=11,
        width=1500,
        height=850,
    )

    fig.show()
    return fig


df = pd.read_csv(r"assets/deportation_data_project/detention-stays_cleaned.csv")

# Sort so newest stay is first per detainee
df = df.sort_values(
    ["detainee_unique_identifier", "stay_book_in_date_time"],
    ascending=[True, False]
).copy()

# Create shifted columns (2nd–4th stays)
for i in range(2, 5):  # 2, 3, 4
    df[f"most_serious_conviction_charge_general{i}"] = (
        df.groupby("detainee_unique_identifier")["most_serious_conviction_charge_general"]
        .shift(-(i - 1))
    )

    df[f"detention_release_reason_general{i}"] = (
        df.groupby("detainee_unique_identifier")["detention_release_reason_general"]
        .shift(-(i - 1))
    )

# Keep only the most recent row per detainee (this is your main df)
df = df.drop_duplicates("detainee_unique_identifier", keep="first").copy()

plot_repeat_detention_sankey(df)