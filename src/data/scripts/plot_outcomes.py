import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def outcome_disparity_plotting(df):
    """
    Plot outcome_disparity_score vs conviction_charge_badness, with point color
    based on citizenship_country_region.

    Skips rows with NaN outcome_disparity_score or conviction_charge_badness.
    Adds random horizontal jitter from -0.2 to 0.2.
    """

    plot_df = df[
        df["outcome_disparity_score"].notna()
        & df["conviction_charge_badness"].notna()
        & df["citizenship_country_region"] != "Unknown"
    ].copy()

    badness_order = [
        "0 - None",
        "1 - Minimal",
        "2 - Low",
        "3 - Moderate",
        "4 - High",
        "5 - Extreme",
    ]
    badness_to_x = {label: i for i, label in enumerate(badness_order)}

    plot_df = plot_df[plot_df["conviction_charge_badness"].isin(badness_order)].copy()
    plot_df["x_base"] = plot_df["conviction_charge_badness"].map(badness_to_x)

    rng = np.random.default_rng(42)
    plot_df["x_jitter"] = rng.uniform(-0.45, 0.45, size=len(plot_df))
    plot_df["x_plot"] = plot_df["x_base"] + plot_df["x_jitter"]

    subregions = sorted(plot_df["citizenship_country_region"].fillna("Unknown").unique())
    cmap = plt.get_cmap("tab20", len(subregions))
    color_map = {subregion: cmap(i) for i, subregion in enumerate(subregions)}

    plt.figure(figsize=(14, 8))

    for subregion in subregions:
        sub_df = plot_df[
            plot_df["citizenship_country_region"].fillna("Unknown") == subregion
        ]
        plt.scatter(
            sub_df["x_plot"],
            sub_df["outcome_disparity_score"],
            label=subregion,
            color=color_map[subregion],
            alpha=0.7,
            s=18,
        )

    plt.xticks(range(len(badness_order)), badness_order, rotation=20)
    plt.xlabel("Conviction Charge Badness")
    plt.ylabel("Outcome Disparity Score (lower is better)")
    plt.title("Outcome Disparity Score by Conviction Charge Badness")
    plt.ylim(0, 0.4)
    plt.grid(axis="y", alpha=0.3)

    plt.legend(
        title="Citizenship Country Sub-Region",
        bbox_to_anchor=(1.02, 1),
        loc="upper left",
        borderaxespad=0,
    )

    plt.tight_layout()
    plt.show()


clean_detention_stays_df = pd.read_pickle(
    r"C:\Users\witzi\OneDrive\Documents\neu_part_2\CS7250\CS7250_trends_in_american_immigration_enforcement\assets\deportation_data_project\detention_stays_df.pkl"
)

outcome_disparity_plotting(clean_detention_stays_df)