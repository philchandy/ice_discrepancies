"""
Data mappings - this goes column by column to either add helper columns or clean data.

Column cleaning - uses apply_column_cleaning to clean a column IN PLACE
New column mapping - uses apply data map to add a new column based off a single column.*
    * there may be more complicated cleaning functions applied for multi-column.

"""
import os
import itertools
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from tabulate import tabulate
import math
from geopy.distance import geodesic

from disparity_assessment import add_outcome_disparity_score
from helpers import get_cleaned_pickle_data, pickle_cleaned_dataset, print_column_counts

# For deportation - define locations
COUNTRY_COORDINATE_LOOKUP = {
    "USA": (40.7128, -74.0060),  # New York City
    "Canada": (43.6532, -79.3832),  # Toronto
    "Mexico": (19.4326, -99.1332),  # Mexico City
    "Brazil": (-23.5505, -46.6333),  # São Paulo
    "Argentina": (-34.6037, -58.3816),  # Buenos Aires
    "Colombia": (4.7110, -74.0721),  # Bogotá
    "Peru": (-12.0464, -77.0428),  # Lima
    "Chile": (-33.4489, -70.6693),  # Santiago
    "UK": (51.5074, -0.1278),  # London
    "France": (48.8566, 2.3522),  # Paris
    "Germany": (52.5200, 13.4050),  # Berlin
    "Spain": (40.4168, -3.7038),  # Madrid
    "Italy": (41.9028, 12.4964),  # Rome
    "Netherlands": (52.3676, 4.9041),  # Amsterdam
    "Sweden": (59.3293, 18.0686),  # Stockholm
    "Norway": (59.9139, 10.7522),  # Oslo
    "Denmark": (55.6761, 12.5683),  # Copenhagen
    "Finland": (60.1699, 24.9384),  # Helsinki
    "Poland": (52.2297, 21.0122),  # Warsaw
    "Ukraine": (50.4501, 30.5234),  # Kyiv
    "Russia": (55.7558, 37.6173),  # Moscow
    "Turkey": (41.0082, 28.9784),  # Istanbul
    "India": (19.0760, 72.8777),  # Mumbai
    "China": (31.2304, 121.4737),  # Shanghai
    "Japan": (35.6762, 139.6503),  # Tokyo
    "South Korea": (37.5665, 126.9780),  # Seoul
    "Indonesia": (-6.2088, 106.8456),  # Jakarta
    "Thailand": (13.7563, 100.5018),  # Bangkok
    "Vietnam": (21.0285, 105.8542),  # Hanoi
    "Philippines": (14.5995, 120.9842),  # Manila
    "Pakistan": (24.8607, 67.0011),  # Karachi
    "Bangladesh": (23.8103, 90.4125),  # Dhaka
    "Australia": (-33.8688, 151.2093),  # Sydney
    "New Zealand": (-36.8485, 174.7633),  # Auckland
    "South Africa": (-26.2041, 28.0473),  # Johannesburg
    "Nigeria": (6.5244, 3.3792),  # Lagos
    "Egypt": (30.0444, 31.2357),  # Cairo
    "Kenya": (-1.2921, 36.8219),  # Nairobi
    "Morocco": (33.5731, -7.5898),  # Casablanca
    "Ethiopia": (9.1450, 40.4897),  # Addis Ababa
    "Saudi Arabia": (24.7136, 46.6753),  # Riyadh
    "UAE": (25.2048, 55.2708),  # Dubai
    "Israel": (31.7683, 35.2137),  # Jerusalem
    "Iran": (35.6892, 51.3890),  # Tehran,
    "Not Applicable": (None, None)
}


def apply_column_cleaning(df):
    """

    This function cleans the following columns in place. It either uses cleaning maps (Excel files),
    minimaps (small dictionaries for very small subset), or simply does nan mapping.

    TBD - right now this just does nan mapping. Fine for now.

    :param df:
    :param column_name:
    :return:
    """

    def map_nans(df):
        # This map defines how nans should be handled when there is a simple 1-to-1 replacement
        # This dictionary needs to be carefully created to ensure there is no loss of data integrity
        nan_column_map = {
            "detention_release_reason": "Still in detention (no departure date)",
            "departure_country": "Not Applicable",
            "citizenship_country": "Unknown",
            "gender": "Unknown",
            "religion": "Unknown",
            "marital_status": "Unknown",
            "ethnicity": "Unknown",
            "case_status": "Unknown",
            "case_category": "Unknown",
        }

        # Iterate across to fill nans
        for column_name, nan_fill_value in nan_column_map.items():
            # Extract column series
            column = df[column_name]

            # Replace nan-like values with normalized numpy nan
            column = (
                column
                .replace([None, ""], np.nan)
                .replace(r"^\s*$", np.nan, regex=True)
            )

            nan_count = column.isna().sum()
            column = column.fillna(nan_fill_value)

            df[column_name] = column

            print(f"'{column_name}' had {nan_count} nan values ({round((nan_count / len(df)) * 100, 2)}% of data), "
                  f"which were replaced with '{nan_fill_value}'")

        return df

    # Apply nan mapping
    df = map_nans(df)

    # Apply a few custom cleanings

    # Title case for countries
    df["citizenship_country"] = df["citizenship_country"].str.title()
    df["departure_country"] = df["departure_country"].str.title()

    return df


def apply_data_maps(df):
    """
    Given a column name, this searches in the lookups folder for the associated map. this reduces
    the amount of code needed to map data.

    :param df: detention df
    :param column_name: the name of column used as mapped column
    :return: df with columns added to the right of the column defined by column_name
    """

    # Lookup df - each key represents an original column
    column_lookup = {
        "citizenship_country":
            {
                "source_col": "country",
                "map_filepath": r"lookups/country_to_region_map.xlsx",
                "mapping_columns": {"region": "citizenship_country_region",
                                    "sub_region": "citizenship_country_sub_region"},
                "nan_mapping_values": {
                    "citizenship_country_region": "Unknown",
                    "citizenship_country_sub_region": "Unknown"
                }
            },
        "departure_country":
            {
                "source_col": "country",
                "map_filepath": r"lookups/country_to_region_map.xlsx",
                "mapping_columns": {"region": "departure_country_region"},
                "nan_mapping_values": {
                    "departure_country_region": "Not Applicable"
                }
            },
        "religion":
            {
                "source_col": "religion",
                "map_filepath": r"lookups/religion_cleaning_map.xlsx",
                "mapping_columns": {"clean_religion": "clean_religion",
                                    "overarching_religion": "overarching_religion"},
                "nan_mapping_values": {
                    "clean_religion": "Unknown",
                    "overarching_religion": "Unknown"
                }
            }
    }

    for column_name in column_lookup.keys():

        # Build the maps
        column_details = column_lookup[column_name]
        mapping_df = pd.read_excel(column_details["map_filepath"])
        nan_map = column_details["nan_mapping_values"]

        # For each column in mapping columns, apply the map
        for value_col, new_column_name in column_details["mapping_columns"].items():
            nan_replacement_value = nan_map[new_column_name]

            source_col = column_details["source_col"]
            mapping_dict = mapping_df.set_index(source_col)[value_col].to_dict()
            mapping_dict = {
                str(k).strip().lower(): v
                for k, v in mapping_dict.items()
            }

            # map the series (pre normalize so we can do case-insensitive mappings)
            df_col_normalized = (
                df[column_name]
                .fillna(nan_replacement_value)
                .astype(str)
                .str.lower()
            )

            df[new_column_name] = df_col_normalized.map(mapping_dict)

    # return the df with the added columns!
    return df


def list_collapse_middle_codes(code_list):
    """
    Given a list of words, if length > 4 collapse adjacent words in the middle of the list. Don't include first
    or last element in any collapsing.

    [EAC, EAC]           --> [EAC, EAC]
    [EAC]                --> [EAC]
    [EAC, EAC, TAC]      --> [EAC EAC, TAC]
    [EAC, EAC, EAC]      --> [EAC, EAC, EAC]
    [EAC, EAC, EAC, EAC] --> [EAC, EAC, EAC]

    :param code_list: a list of facility codes
    :return: a list of facility codes with the center ones collapsed if there are adjacent codes.
    """

    # Quick return for None or short list
    if code_list is None:
        return None

    if len(code_list) <= 3:
        return code_list

    new_list = [code_list[0], code_list[1]]  # keep first two always!!

    for i in range(2, len(code_list) - 1):
        if code_list[i] != code_list[i - 1]:
            new_list.append(code_list[i])

    new_list.append(code_list[-1])  # keep last

    return new_list


def build_and_pickle_detention_stays(row_limit=None, use_mini=False):
    """
    Starts from raw detention-stays-latest.xlsx

    :param: row_limit: default None. if not None
    :return:
    """
    if use_mini:
        raw_df = pd.read_excel(r"assets/deportation_data_project/detention-stays-latest_mini.xlsx")
    else:
        raw_df = pd.read_excel(r"assets/deportation_data_project/detention-stays-latest.xlsx",
                               nrows=row_limit)

    if row_limit is not None:
        raw_df = raw_df.head(row_limit)

    cleaned_df = clean_detention_stays(raw_df)
    cleaned_df.to_pickle(r"assets/deportation_data_project/detention_stays_df.pkl")
    return cleaned_df


def clean_data_set(data_set_name, raw_df):
    """
    Given a data set name, clean it according to the specified cleaning procedure for that dataset.

    TBD - make the cleanings for other sets??

    :param raw_df: uncleaned raw dataFrame
    :param data_set_name: data set name
    :return: cleaned dataFrame
    """

    if raw_df is None:
        raise ValueError("clean_data_set: raw_df is None")

    data_lookup = {
        "detention_stays": clean_detention_stays
    }

    # Print warning with helpful reminder of data sets that have cleaning procedures
    if data_set_name not in data_lookup.keys():
        raise ValueError(f"You attempted to clean the data set {data_set_name}.\n but we don't yet have a cleaning "
                         f"procedure"
                         f"Cleaning procedures are available for: {list(data_lookup.keys())}")

    try:
        cleaned_df = data_lookup[data_set_name](raw_df)
        return cleaned_df

    except Exception as e:
        print(e)
        print(f"We ran into the issue with your dataset {data_set_name}. Is there a chance you have given a"
              f"data_set_name and raw_df which are incompatible? Your data's columns are: {list(raw_df.columns)}")


def list_collapse_all_codes(code_list):
    """
    Given a list of codes, this collapses ALL adjacent duplicates including beginning and end.
    :param code_list: list of facility codes
    :return: collapsed list
    """
    if code_list is None:
        return None

    if len(set(code_list)) == len(code_list):
        return code_list

    # Iterate through list
    new_list = [code_list[0]]

    for i in range(1, len(code_list)):
        if code_list[i] != new_list[-1]:
            new_list.append(code_list[i])

    return new_list


def get_estimated_facility_count_data(df):
    """
    TBD - finish this!!

    Given a detention dataframe, this looks at stay_book_in_date_time, stay_book_out_date_time as well
    as facility_codes (python list).

    If stay_book_out_date_time is nan or NaT, then we assume that the detainee was still in detention at
    the end of the data collection period, which was max(df["stay_book_out_date_time"].

    TBD - Note that the above assumption should be re-examined and discussed as a team.

    Hold duration can be nebulous, because people can have 1-20+ locations held during a single detention.
    However, the first and final detentions are defined more granularly with the columns:
     * book_in_date_time_first
     * book_out_date_time_first
     * book_in_date_time_last
     * book_out_date_time_last

    As well as times that represent the longest stay:
     * book_in_date_time_longest
     * book_out_date_time_longest

    LIMITATIONS OF METHODOLOGY__________________________________________________________________________
    With these 3 tuples (first, longest, last), we can calculate the exact duration of up to 3 stays.
    Other stays will have data interpolated, with an equal duration.

    The maximum number of stays per detention is 73, the mode is 1, the median is 2, the average is 2.4.

    The least accurate stay length calculation will be for HOLDs occurring in the middle of a detention.

    COLLAPSING METHODOLOGY______________________________________________________________________________
    Occasionally there will be duplicates of a hold

    :param df:
    :return:
    """

    # Start by collapsing each list. This doesn't affect first or last stay because those are
    # tracked in a specific way
    df["facility_codes_with_middle_duplicates_collapsed"] = df["facility_codes"].apply(list_collapse_middle_codes)

    return


def calculate_distances_traveled(df):
    """
    ~ Used ChatGPT for part of this ~

    Given a df with a column called facility_codes, use the facility_code_map to calculate the total distance
    traveled from the first facility to the intermediate ones, to the last. Then also calculate the deportation
    distance, and add the total distance.

    Faster version:
    - caches facility-to-facility distances
    - caches facility-to-country distances
    - avoids df.apply(axis=1) for deportation distance
    """

    facility_code_map = pd.read_csv(
        r"lookups/facility_code_map_with_coordinates.csv",
        encoding="latin1"
    )

    facility_code_map = facility_code_map[~facility_code_map["latitude"].isna()].copy()

    # Create quick lookup
    code_to_lat_long_lookup = dict(zip(
        facility_code_map["code"],
        zip(facility_code_map["latitude"], facility_code_map["longitude"])
    ))

    # Caches
    facility_pair_cache = {}
    facility_country_cache = {}

    def get_facility_pair_distance(code1, code2):
        """
        Distance between two facility codes.
        Uses canonicalized key because A->B distance == B->A distance.
        """
        if code1 is None or code2 is None:
            return 0

        key = tuple(sorted((code1, code2)))

        if key in facility_pair_cache:
            return facility_pair_cache[key]

        start = code_to_lat_long_lookup.get(code1)
        end = code_to_lat_long_lookup.get(code2)

        if start is None or end is None:
            miles = 0
        else:
            miles = int(geodesic(start, end).miles)

        facility_pair_cache[key] = miles
        return miles

    def get_facility_country_distance(code, country):
        """
        Distance from facility code to departure country representative coordinates.
        """
        if code is None or country is None or country == "Not Applicable":
            return 0

        key = (code, country)

        if key in facility_country_cache:
            return facility_country_cache[key]

        start = code_to_lat_long_lookup.get(code)
        end = COUNTRY_COORDINATE_LOOKUP.get(country)

        if start is None or end is None or None in end:
            miles = 0
        else:
            miles = int(geodesic(start, end).miles)

        facility_country_cache[key] = miles
        return miles

    def dissect_code_distance(code_list):
        """
        Iterate through a code list and add up the segment distances.
        """
        if code_list is None or len(code_list) <= 1:
            return 0

        total_miles = 0

        for i in range(len(code_list) - 1):
            total_miles += get_facility_pair_distance(code_list[i], code_list[i + 1])

        return total_miles

    # Domestic distances
    df["domestic_miles_traveled"] = df["facility_codes"].apply(dissect_code_distance)

    # Deportation distances
    dep_pairs = zip(df["detention_facility_code_last"], df["departure_country"])
    df["deportation_miles_traveled"] = [
        get_facility_country_distance(code, country)
        for code, country in dep_pairs
    ]

    # Total
    df["total_miles_traveled"] = (
            df["domestic_miles_traveled"].fillna(0)
            + df["deportation_miles_traveled"].fillna(0)
    )

    return df


def rename_columns_for_clarity(df):
    """
    Rename columns in detention df for clarity.

    :param df: detention dataframe
    :return:
    """

    python_rename_map = {
        "bond_posted_amount": "bond_posted_amount_usd",
        "final_order_yes_no": "final_order_of_removal",
        "initial_bond_set_amount": "initial_bond_set_amount_usd",
        "msc_charge": "most_serious_conviction_charge",
        "unique_identifier": "detainee_unique_identifier"
    }

    df = df.rename(columns=python_rename_map)
    return df


def reorder_and_group_columns_for_clarity(df):
    """
    Arranges the columns of a dataFrame in a more person-focused order:
      * demographics
      * crime
      * stay
      * departure
    :param df:
    :return:
    """

    # Combine all ordered columns
    ordered_cols = ["detainee_unique_identifier",
                    "stay_ID",
                    "birth_year",
                    "age_at_booking",
                    "age_group",
                    "gender",
                    "ethnicity",
                    "marital_status",
                    "religion",
                    "clean_religion",
                    "overarching_religion",
                    "citizenship_country",
                    "citizenship_country_region",
                    "citizenship_country_sub_region",
                    "entry_status",
                    "most_serious_conviction_code",
                    "most_serious_conviction_charge",
                    "most_serious_conviction_charge_general",
                    "conviction_charge_badness",
                    "final_charge",
                    "book_in_criminality",
                    "felon",
                    "case_status",
                    "case_category",
                    "case_threat_level",
                    "final_order_of_removal",
                    "final_order_date",
                    "departed_date",
                    "departure_country",
                    "departure_country_region",
                    "detention_release_reason",
                    "detention_release_reason_general",
                    "detention_release_reason_most_general",
                    "stay_release_reason",
                    "final_program",
                    "bond_posted_date",
                    "bond_posted_amount_usd",
                    "initial_bond_set_amount_usd",
                    "deportation_assessment_general",
                    "deportation_assessment_specific",
                    "n_stays",
                    "n_stints",
                    "stay_book_in_date_time",
                    "stay_book_out_date_time",
                    "stay_book_out_date",
                    "detention_facility_codes_all",
                    "detention_facility_first",
                    "detention_facility_code_first",
                    "book_in_date_time_first",
                    "book_out_date_time_first",
                    "detention_facility_longest",
                    "detention_facility_code_longest",
                    "book_in_date_time_longest",
                    "book_out_date_time_longest",
                    "detention_facility_last",
                    "detention_facility_code_last",
                    "book_in_date_time_last",
                    "book_out_date_time_last",
                    "days_in_detention",
                    "deportation_miles_traveled",
                    "domestic_miles_traveled",
                    "total_miles_traveled",
                    "facility_codes",
                    "facility_codes_with_middle_duplicates_collapsed",
                    "facility_codes_all_collapsed",
                    "stint_tuples",
                    "stint_duration_status",
                    "stint_tuples_collapsed",
                    "number_transfers_during_stay"]

    # Keep only columns that exist in df
    ordered_cols = [c for c in ordered_cols if c in df.columns]

    # Append any remaining columns not explicitly ordered
    remaining_cols = [c for c in df.columns if c not in ordered_cols]

    return df[ordered_cols + remaining_cols]


def assess_deportation(df):
    """


    Adds a column to df called deportation_assessment to track if person wasn't deported,
                    was deported home,
    or was deported to a 3rd country.
    :param df:
    :return:
    """

    df["deportation_assessment_general"] = np.select(
        [
            df["departure_country"] == "Not Applicable",
            df["departure_country"] == df["citizenship_country"],
            df["departure_country"] != df["citizenship_country"],
        ],
        [
            "not deported",
            "deported to country of citizenship",
            "deported to country other than country of citizenship"
        ],
        default=None
    )

    df["deportation_assessment_specific"] = np.select(
        [
            df["departure_country"] == "Not Applicable",
            df["departure_country"] == df["citizenship_country"],
            df["departure_country"] != df["citizenship_country"],
        ],
        [
            "not deported",
            "deported to country of citizenship",
            "3rd country deportation: citizen of "
            + df["citizenship_country"].astype(str)
            + " --> but deported to "
            + df["departure_country"].astype(str),
        ],
        default=None
    )
    return df


def map_detention_release_reason(df):
    """
    Given a df with column detention_release_reason, add
    (1) detention_release_reason_general
    (2) detention_release_reason_most_general
    :param df: detention df
    :return: df with added columns.

    """
    map_loc = r"lookups/detention_release_reason_map.xlsx"
    detention_map = pd.read_excel(map_loc)

    # Build mapping dicts
    general_map = dict(zip(
        detention_map["detention_release_reason"],
        detention_map["detention_release_reason_general"]
    ))

    most_general_map = dict(zip(
        detention_map["detention_release_reason"],
        detention_map["detention_release_reason_most_general"]
    ))

    # Map values
    df["detention_release_reason_general"] = df["detention_release_reason"].map(general_map)
    df["detention_release_reason_most_general"] = df["detention_release_reason"].map(most_general_map)

    # Insert columns immediately to the right of detention_release_reason
    source_col_index = df.columns.get_loc("detention_release_reason")

    columns = list(df.columns)
    columns.insert(source_col_index + 1, columns.pop(columns.index("detention_release_reason_general")))
    columns.insert(source_col_index + 2, columns.pop(columns.index("detention_release_reason_most_general")))

    df = df[columns]

    return df


def map_most_serious_conviction(df):
    """
    Given a df with column most_serious_conviction, add
    (1) most_serious_conviction_general
    :param df: detention df
    :return: df with added columns.

    """
    map_loc = r"lookups/most_serious_conviction_map.xlsx"
    detention_map = pd.read_excel(map_loc)

    # Build mapping dicts
    general_map = dict(zip(
        detention_map["most_serious_conviction_charge"],
        detention_map["most_serious_conviction_charge_general"]
    ))

    badness_map = dict(zip(
        detention_map["most_serious_conviction_charge_general"],
        detention_map["conviction_charge_badness"]
    ))

    # Map values
    df["most_serious_conviction_charge_general"] = (
        df["most_serious_conviction_charge"]
        .map(general_map)
        .fillna("No criminal history")
    )

    df["conviction_charge_badness"] = (
        df["most_serious_conviction_charge_general"]
        .map(badness_map)
    )

    # Override for no criminal history
    df.loc[
        df["most_serious_conviction_charge_general"] == "No criminal history",
        "conviction_charge_badness"
    ] = "0 - None"

    return df


def datetime_normalization_with_error_coercion(df):
    """

    :param df:
    :return:
    """

    # get all cols containing date_time
    datetime_cols = [x for x in df.columns if "date_time" in x]

    for col in datetime_cols:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    return df


def calculate_days_in_detention(df) -> pd.Series:
    """
    Compute days in detention.

    - Uses stay_book_out_date_time when available
    - If missing AND detention_release_reason == "Still in detention (no departure date)",
      fills with global max datetime across key date columns
    - Returns a Series of days (float)

    :param df: detention stays DataFrame
    :return: pd.Series of days in detention
    """

    seconds_per_day = 60 * 60 * 24

    date_cols_for_global_max = [
        "final_order_date",
        "departed_date",
        "bond_posted_date",
        "stay_book_in_date_time",
        "stay_book_out_date_time",
        "stay_book_out_date",
        "book_in_date_time_first",
        "book_out_date_time_first",
        "book_in_date_time_longest",
        "book_out_date_time_longest",
        "book_in_date_time_last",
        "book_out_date_time_last",
    ]

    # ensure datetime
    for col in date_cols_for_global_max:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    # global max datetime
    global_max_datetime = pd.concat(
        [df[col] for col in date_cols_for_global_max],
        axis=0
    ).max()

    # condition: still detained AND missing out date
    still_detained_mask = (
            (df["detention_release_reason_general"] == "Detention") &
            df["stay_book_out_date_time"].isna()
    )

    # effective end datetime with fallback logic
    effective_out = df["stay_book_out_date_time"].copy()

    # still detained override
    effective_out.loc[still_detained_mask] = global_max_datetime

    # effective end datetime with full fallback ordering
    effective_out = (
        df["stay_book_out_date_time"]
        .fillna(df["stay_book_out_date"])  # if datetime missing but date exists
        .fillna(df["book_out_date_time_last"])
        .fillna(df["book_out_date_time_first"])
        .fillna(df["book_out_date_time_longest"])

        # last resort fallbacks (NOT ideal, but avoids NaT)
        .fillna(df["stay_book_in_date_time"])
        .fillna(df["book_in_date_time_last"])
        .fillna(df["book_in_date_time_first"])
        .fillna(df["book_in_date_time_longest"])
    )

    # compute duration
    duration_days = (
                            effective_out - df["stay_book_in_date_time"]
                    ).dt.total_seconds() / seconds_per_day

    return duration_days


def clean_detention_stays(raw_df):
    """
    Simple cleaner for raw detention stays dataFrame.

    Calls variety of sub functions

    :param: raw detention stays df
    :return: detention stays dataFrame
    """

    # Basic column cleanings and mappings
    detention_stays_df = apply_column_cleaning(raw_df)
    detention_stays_df = apply_data_maps(detention_stays_df)
    detention_stays_df = rename_columns_for_clarity(detention_stays_df)
    detention_stays_df = datetime_normalization_with_error_coercion(detention_stays_df)
    detention_stays_df = map_detention_release_reason(detention_stays_df)
    detention_stays_df = map_most_serious_conviction(detention_stays_df)

    # Split detention lists
    detention_stays_df["facility_codes"] = detention_stays_df["detention_facility_codes_all"].str.split("; ")

    # days in detention calculations
    detention_stays_df["days_in_detention"] = calculate_days_in_detention(detention_stays_df)

    # age
    detention_stays_df["age_at_booking"] = (
            detention_stays_df["stay_book_in_date_time"].dt.year - detention_stays_df["birth_year"])
    detention_stays_df = get_age_group(detention_stays_df)

    # distances traveled
    detention_stays_df = calculate_distances_traveled(detention_stays_df)

    # Deportation status assessment (not deported, third country, deported to country of citizenship)
    detention_stays_df = assess_deportation(detention_stays_df)

    # Stint duration details
    # Collapse all codes and also just the middle codes (create 2 new columns)
    detention_stays_df["facility_codes_all_collapsed"] = detention_stays_df["facility_codes"].apply(
        list_collapse_all_codes)
    detention_stays_df["facility_codes_with_middle_duplicates_collapsed"] = detention_stays_df["facility_codes"].apply(
        list_collapse_middle_codes)

    # Use facility_codes_all_collapsed to count # of transfers.
    # todo - potentially use GPS data to limit to "actual transfers" (i.e. don't count bouncing around locations WITHIN
    # a facility as a transfer
    detention_stays_df["number_transfers_during_stay"] = detention_stays_df["facility_codes_all_collapsed"].apply(
        lambda x: len(x) - 1)

    # Add in the stint tuples
    results = list(map(create_stint_tuples, detention_stays_df.to_dict("records")))
    detention_stays_df["stint_tuples"] = [x[0] for x in results]
    detention_stays_df["stint_duration_status"] = [x[1] for x in results]

    # Further collapse
    detention_stays_df["stint_tuples_collapsed"] = detention_stays_df["stint_tuples"].apply(collapse_stint_tuples)

    # reorder things
    detention_stays_df = reorder_and_group_columns_for_clarity(detention_stays_df)

    # Add "badness" score
    detention_stays_df = add_outcome_disparity_score(detention_stays_df)

    return detention_stays_df


def split_gap(code_list, start_dt, end_dt):
    """
    Given a list of codes and an overall time window, split the window evenly
    into consecutive (code, start, end) tuples.
    """
    k = len(code_list)

    if k == 0:
        return []

    total = end_dt - start_dt
    segment = total / k

    output = []
    current_start = start_dt

    for i, code in enumerate(code_list):
        current_end = end_dt if i == k - 1 else current_start + segment
        output.append((code, current_start, current_end))
        current_start = current_end

    return output


def create_stint_tuples_original(row):
    """
    Given a row representing a detainee's singular stay, use
    facility_codes_with_middle_duplicates_collapsed and various datetimes
    to calculate stint durations.

    Returns:
        (stint_tuples, status)

    stint_tuples: list of (facility_code, start_datetime, end_datetime)
    status: "exact" or "some stint durations estimated"
    """

    collapsed_stints = row["facility_codes_with_middle_duplicates_collapsed"]

    if collapsed_stints is None:
        return None, "some stint durations estimated"

    n = len(collapsed_stints)
    if n == 0:
        return [], "some stint durations estimated"

    first_code = row["detention_facility_code_first"]
    last_code = row["detention_facility_code_last"]
    longest_code = row["detention_facility_code_longest"]

    first_stay = (first_code, row["book_in_date_time_first"], row["book_out_date_time_first"])
    last_stay = (last_code, row["book_in_date_time_last"], row["book_out_date_time_last"])
    longest_stay = (longest_code, row["book_in_date_time_longest"], row["book_out_date_time_longest"])

    # If longest stay is the same stint as first or last, don't use it separately
    if longest_stay == first_stay or longest_stay == last_stay:
        longest_stay = None

    # Exact base cases
    if n == 1:
        return [first_stay], "exact"

    if n == 2:
        return [first_stay, last_stay], "exact"

    if n == 3:
        return [
            first_stay,
            (collapsed_stints[1], first_stay[2], last_stay[1]),
            last_stay
        ], "exact"

    # Start with placeholders
    stints = [None] * n
    stints[0] = first_stay
    stints[-1] = last_stay

    # Try to locate the longest code inside collapsed_stints
    longest_idx = None
    if longest_stay is not None and longest_code is not None:
        matches = [i for i, code in enumerate(collapsed_stints) if code == longest_code]

        # If longest was already first/last, it was nulled out above.
        interior_matches = [i for i in matches if i not in (0, n - 1)]

        if len(interior_matches) == 1:
            longest_idx = interior_matches[0]
            stints[longest_idx] = longest_stay

    # Exact cases with anchored longest stint
    if n == 4 and longest_idx in (1, 2):
        if longest_idx == 1:
            # [first][longest][unknown][last]
            stints[2] = (collapsed_stints[2], longest_stay[2], last_stay[1])
        else:
            # [first][unknown][longest][last]
            stints[1] = (collapsed_stints[1], first_stay[2], longest_stay[1])
        return stints, "exact"

    if n == 5 and longest_idx == 2:
        # [first][unknown][longest][unknown][last]
        stints[1] = (collapsed_stints[1], first_stay[2], longest_stay[1])
        stints[3] = (collapsed_stints[3], longest_stay[2], last_stay[1])
        return stints, "exact"

    # Otherwise estimate unknown interior stints by splitting gaps evenly
    known_indices = [i for i, stint in enumerate(stints) if stint is not None]

    for left_idx, right_idx in zip(known_indices, known_indices[1:]):
        num_missing = right_idx - left_idx - 1
        if num_missing <= 0:
            continue

        left_end = stints[left_idx][2]
        right_start = stints[right_idx][1]

        missing_codes = collapsed_stints[left_idx + 1:right_idx]
        estimated = split_gap(missing_codes, left_end, right_start)

        for offset, idx in enumerate(range(left_idx + 1, right_idx)):
            stints[idx] = estimated[offset]

    # Fallback: if longest couldn't be placed uniquely, split whole interior
    if any(stint is None for stint in stints):
        stints = [first_stay]
        interior_codes = collapsed_stints[1:-1]
        interior = split_gap(interior_codes, first_stay[2], last_stay[1])
        stints.extend(interior)
        stints.append(last_stay)

    return stints, "some stint durations estimated"


def create_stint_tuples(row):
    """
    Given a row representing a detainee's singular stay, use
    facility_codes_with_middle_duplicates_collapsed and various datetimes
    to calculate stint durations.

    Returns:
        (stint_tuples, status)

    stint_tuples: list of (facility_code, start_datetime, end_datetime)
    status: "exact" or "some stint durations estimated"
    """

    collapsed_stints = row["facility_codes_with_middle_duplicates_collapsed"]

    if not collapsed_stints:
        if collapsed_stints is None:
            return None, "some stint durations estimated"
        return [], "some stint durations estimated"

    n = len(collapsed_stints)

    first_stay = (
        row["detention_facility_code_first"],
        row["book_in_date_time_first"],
        row["book_out_date_time_first"],
    )
    last_stay = (
        row["detention_facility_code_last"],
        row["book_in_date_time_last"],
        row["book_out_date_time_last"],
    )
    longest_stay = (
        row["detention_facility_code_longest"],
        row["book_in_date_time_longest"],
        row["book_out_date_time_longest"],
    )

    first_code = first_stay[0]
    last_code = last_stay[0]
    longest_code = longest_stay[0]

    # If longest stay is the same stint as first or last, don't use it separately
    if longest_stay == first_stay or longest_stay == last_stay:
        longest_stay = None
        longest_code = None

    # Exact base cases
    if n == 1:
        return [first_stay], "exact"

    if n == 2:
        return [first_stay, last_stay], "exact"

    if n == 3:
        return [
            first_stay,
            (collapsed_stints[1], first_stay[2], last_stay[1]),
            last_stay,
        ], "exact"

    # Start with placeholders
    stints = [None] * n
    stints[0] = first_stay
    stints[-1] = last_stay

    # Try to locate the longest code inside collapsed_stints
    longest_idx = None
    if longest_code is not None:
        interior_match_count = 0
        for i in range(1, n - 1):
            if collapsed_stints[i] == longest_code:
                interior_match_count += 1
                longest_idx = i
                if interior_match_count > 1:
                    longest_idx = None
                    break

        if longest_idx is not None:
            stints[longest_idx] = longest_stay

    # Exact cases with anchored longest stint
    if n == 4 and longest_idx in (1, 2):
        if longest_idx == 1:
            # [first][longest][unknown][last]
            stints[2] = (collapsed_stints[2], longest_stay[2], last_stay[1])
        else:
            # [first][unknown][longest][last]
            stints[1] = (collapsed_stints[1], first_stay[2], longest_stay[1])
        return stints, "exact"

    if n == 5 and longest_idx == 2:
        # [first][unknown][longest][unknown][last]
        stints[1] = (collapsed_stints[1], first_stay[2], longest_stay[1])
        stints[3] = (collapsed_stints[3], longest_stay[2], last_stay[1])
        return stints, "exact"

    # Otherwise estimate unknown interior stints by splitting gaps evenly
    known_indices = [i for i, stint in enumerate(stints) if stint is not None]

    for left_idx, right_idx in zip(known_indices, known_indices[1:]):
        if right_idx - left_idx <= 1:
            continue

        left_end = stints[left_idx][2]
        right_start = stints[right_idx][1]
        missing_codes = collapsed_stints[left_idx + 1:right_idx]
        estimated = split_gap(missing_codes, left_end, right_start)

        for idx, est in zip(range(left_idx + 1, right_idx), estimated):
            stints[idx] = est

    # Fallback: if longest couldn't be placed uniquely, split whole interior
    if any(stint is None for stint in stints):
        interior_codes = collapsed_stints[1:-1]
        interior = split_gap(interior_codes, first_stay[2], last_stay[1])
        stints = [first_stay, *interior, last_stay]

    return stints, "some stint durations estimated"


def collapse_stint_tuples(stint_tuples):
    """
    Given a list of (code, start, end) tuples, collapse adjacent tuples
    that have the same code into a single tuple spanning the full interval.

    Example:
    [
        ("EAC", t1, t2),
        ("EAC", t2, t3),
        ("TAC", t3, t4)
    ]
    -->
    [
        ("EAC", t1, t3),
        ("TAC", t3, t4)
    ]
    """
    if not stint_tuples:
        return stint_tuples

    collapsed = [stint_tuples[0]]

    for code, start, end in stint_tuples[1:]:
        last_code, last_start, last_end = collapsed[-1]

        if code == last_code:
            collapsed[-1] = (last_code, last_start, end)
        else:
            collapsed.append((code, start, end))

    return collapsed


def get_age_group(df):
    """
    Using the age_at_booking column of a df, create a new column called age_group.

    :param df: dataFrame with column age_at_booking
    :return: the same df with age_group added
    """

    age_group_lookup = {
        (0, 10): "0 - 10",
        (11, 18): "11 - 18",
        (19, 30): "19 - 30",
        (31, 50): "31 - 50",
        (51, 65): "51 - 65",
        (66, 130): "66+"
    }

    def age_to_age_group(age):
        if age is None:
            return "Unknown"
        for k, v in age_group_lookup.items():
            if int(age) in range(k[0], k[1] + 1):
                return v

    df["age_group"] = df["age_at_booking"].apply(age_to_age_group)

    return df


def expand_stint_tuples_with_geo(
        df,
        departure_country_col: str = "departure_country",
        deportation_datetime_col: str = "book_out_date_time_last",
):
    """
    Expand facility stints and attach latitude/longitude.
    Also add a synthetic final "country stint" for deported detainees.

    Assumptions
    -----------
    - df contains:
        - detainee_unique_identifier
        - stint_tuples_collapsed : list of (facility, start, end)
        - departure_country_col  : e.g. "departure_country"
        - deportation_datetime_col : e.g. "book_out_date_time_last"
    - A detainee is considered deported if departure_country_col != "Not Available"
    - Deportation begins at deportation_datetime_col
    - Deportation country stay lasts until the maximum date covered by the graph
    - COUNTRY_COORDINATE_LOOKUP maps country -> (latitude, longitude)

    Returns
    -------
    pd.DataFrame
        Columns:
        - uid
        - facility
        - start
        - end
        - latitude
        - longitude
    """

    code_coordinate_map = pd.read_csv(
        r"lookups/facility_code_map_with_coordinates.csv",
        encoding="latin1"
    )

    # -----------------------------
    # 1) Expand regular facility stints
    # -----------------------------
    out = df[["detainee_unique_identifier", "stint_tuples_collapsed"]].copy()

    out = out[out["stint_tuples_collapsed"].notna()]
    out = out[out["stint_tuples_collapsed"].map(len) > 0]

    out = out.explode("stint_tuples_collapsed", ignore_index=True)

    stint_parts = pd.DataFrame(
        out["stint_tuples_collapsed"].tolist(),
        columns=["facility", "start", "end"],
        index=out.index
    )

    out = pd.concat([out[["detainee_unique_identifier"]], stint_parts], axis=1)
    out = out.rename(columns={"detainee_unique_identifier": "uid"})

    out["start"] = pd.to_datetime(out["start"], errors="coerce")
    out["end"] = pd.to_datetime(out["end"], errors="coerce")

    geo = code_coordinate_map.rename(columns={"code": "facility"})[
        ["facility", "latitude", "longitude"]
    ]

    out = out.merge(geo, on="facility", how="left")

    # maximum graph date based on regular stints
    max_graph_date = out["end"].max()

    # -----------------------------
    # 2) Build synthetic deportation "country stints"
    # -----------------------------
    deport_cols = [
        "detainee_unique_identifier",
        departure_country_col,
        deportation_datetime_col
    ]
    deport_df = df[deport_cols].copy()

    deport_df = deport_df.rename(columns={
        "detainee_unique_identifier": "uid",
        departure_country_col: "facility",
        deportation_datetime_col: "start"
    })

    deport_df["facility"] = deport_df["facility"].astype("string").str.strip()
    deport_df["start"] = pd.to_datetime(deport_df["start"], errors="coerce")

    # deported only
    deport_df = deport_df[
        deport_df["facility"].notna() &
        (deport_df["facility"] != "") &
        (deport_df["facility"] != "Not Available") &
        deport_df["start"].notna()
        ].copy()

    # attach country coordinates from the global dict
    country_geo = pd.DataFrame(
        [
            {"facility": country, "latitude": lat, "longitude": lon}
            for country, (lat, lon) in COUNTRY_COORDINATE_LOOKUP.items()
        ]
    )

    deport_df = deport_df.merge(country_geo, on="facility", how="left")

    # only keep countries we can map
    deport_df = deport_df[
        deport_df["latitude"].notna() &
        deport_df["longitude"].notna()
        ].copy()

    # make country stay last until end of graphing period
    deport_df["end"] = max_graph_date

    # optional safety: only keep rows where deportation starts before graph end
    deport_df = deport_df[deport_df["start"] <= deport_df["end"]].copy()

    deport_df = deport_df[["uid", "facility", "start", "end", "latitude", "longitude"]]

    # -----------------------------
    # 3) Combine regular stays + country stays
    # -----------------------------
    out = out[["uid", "facility", "start", "end", "latitude", "longitude"]]
    out = pd.concat([out, deport_df], ignore_index=True)

    # Step 1: get earliest start per uid
    uid_order = (
        out.groupby("uid")["start"]
        .min()
        .sort_values()
    )

    # Step 2: make uid a categorical with that order
    out["uid"] = pd.Categorical(out["uid"], categories=uid_order.index, ordered=True)

    # Step 3: now sort
    out = out.sort_values(
        ["uid", "start", "end", "facility"],
        kind="stable"
    ).reset_index(drop=True)

    return out


def export_stays_csv(
        df,
        output_path: str = r"src/stays.csv"
) -> None:
    """
    Expects df with columns:
        uid, facility, start, end, latitude, longitude

    Removes any rows where start < Jan 1, 2021
    """

    cutoff = pd.Timestamp("2021-01-01")

    required = ["uid", "facility", "start", "end", "latitude", "longitude"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    out = df[required].copy()

    # ensure datetime
    out["start"] = pd.to_datetime(out["start"], errors="coerce")
    out["end"] = pd.to_datetime(out["end"], errors="coerce")

    # drop bad rows
    out = out.dropna(subset=["uid", "facility", "start", "end", "latitude", "longitude"])

    # 🔥 FILTER HERE
    out = out[out["start"] >= cutoff]

    # clean numeric
    out["latitude"] = pd.to_numeric(out["latitude"], errors="coerce")
    out["longitude"] = pd.to_numeric(out["longitude"], errors="coerce")
    out = out.dropna(subset=["latitude", "longitude"])

    # format
    out["start"] = out["start"].dt.strftime("%Y-%m-%dT%H:%M:%S")
    out["end"] = out["end"].dt.strftime("%Y-%m-%dT%H:%M:%S")

    out.to_csv(output_path, index=False)


def explore_df(df, top_n: int = 20):
    """
    Prints exploration info column-by-column so progress is visible.

    For each column:
      - number of unique values
      - top N most common values and their counts
    """

    total_cols = len(df.columns)

    for i, col in enumerate(df.columns, 1):
        print(f"\n{'=' * 80}")
        print(f"[{i}/{total_cols}] Column: {col}")
        print(f"{'=' * 80}")

        value_counts = df[col].value_counts(dropna=False)
        top_values = value_counts.head(top_n)

        # Prepare table rows
        table_rows = [
            [repr(idx), cnt] for idx, cnt in top_values.items()
        ]

        print(f"Unique Values: {df[col].nunique(dropna=False)}\n")

        print(tabulate(
            table_rows,
            headers=["Value", "Count"],
            tablefmt="fancy_grid",
            stralign="left"
        ))


def clean_detention_stays_into_stats_df_spec(
        cleaned_stays_df,
        person_level_outcomes_df
):
    """
    Given:
      (1) cleaned_stays_df (stay-level source, used for validation/context)
      (2) person_level_outcomes_df (one row per person with `final_outcome`)

    Populate a dataframe for 100-person calculations with columns:
        age_group
        gender
        citizenship_country_sub_region
        conviction_charge_badness

    Also include an "All" rollup option for each of the above.

    Outcome percentages are derived from person-level `final_outcome` values:
      - Released to USA - long term residence likely
      - Released to USA - long term residence possible
      - Released to USA - will be detained again
      - Deported
      - Other / unclassified

    :param cleaned_stays_df: cleaned stay-level dataframe
    :param person_level_outcomes_df: person-level output from
                                     get_person_level_outcomes_df_from_cleaned_stays_df
    :return: outcomes_df
    """

    grouping_dimensions = [
        "age_group",
        "gender",
        "citizenship_country_sub_region",
        "conviction_charge_badness",
    ]

    required_cols = ["detainee_unique_identifier", "final_outcome", "age_group",
                     "gender",
                     "citizenship_country_sub_region",
                     "conviction_charge_badness"]
    missing_cols = [c for c in required_cols if c not in person_level_outcomes_df.columns]
    if missing_cols:
        raise KeyError(f"Missing required columns in person_level_outcomes_df: {missing_cols}")

    duplicate_people = person_level_outcomes_df["detainee_unique_identifier"].duplicated(keep=False)
    if duplicate_people.any():
        duplicate_count = int(person_level_outcomes_df.loc[duplicate_people, "detainee_unique_identifier"].nunique())
        raise ValueError(
            "person_level_outcomes_df must contain exactly one row per detainee_unique_identifier. "
            f"Found duplicate rows for {duplicate_count} people."
        )

    working_df = person_level_outcomes_df[required_cols].copy()
    base_stats_df = clean_detention_stays_into_stats_df(cleaned_stays_df)

    outcome_labels = [
        "Released to USA - long term residence likely",
        "Released to USA - long term residence possible",
        "Released to USA - will be detained again",
        "Awaiting Deportation",
        "Deported",
    ]
    excluded_outcome = "Other / unclassified"

    def pct_excluding_other(sub_df, label: str) -> float:
        denominator = sub_df["final_outcome"].ne(excluded_outcome).sum()
        if denominator == 0:
            return np.nan
        numerator = sub_df["final_outcome"].eq(label).sum()
        return round((numerator / denominator) * 100, 2)

    output_rows = []
    for keep_count in range(len(grouping_dimensions), -1, -1):
        for kept_dims in itertools.combinations(grouping_dimensions, keep_count):
            kept_dims = list(kept_dims)

            if kept_dims:
                grouped = working_df.groupby(kept_dims, dropna=False, sort=True)
                for keys, sub_df in grouped:
                    if not isinstance(keys, tuple):
                        keys = (keys,)

                    label_values = {dim: "All" for dim in grouping_dimensions}
                    for dim, key in zip(kept_dims, keys):
                        label_values[dim] = key

                    row = {**label_values}
                    for label in outcome_labels:
                        row[label] = pct_excluding_other(sub_df, label)
                    output_rows.append(row)
            else:
                label_values = {dim: "All" for dim in grouping_dimensions}
                row = {**label_values}
                for label in outcome_labels:
                    row[label] = pct_excluding_other(working_df, label)
                output_rows.append(row)

    outcomes_df = pd.DataFrame(output_rows)

    stats_df = base_stats_df.drop(
        columns=[
            "USA - Long term residence likely",
            "USA - Stay in USA possible",
            "USA - Detained again",
            "Deported - country of citizenship",
            "Deported - 3rd country",
        ],
        errors="ignore",
    ).merge(
        outcomes_df,
        on=grouping_dimensions,
        how="left",
    )

    col_order = [
        "age_group",
        "gender",
        "citizenship_country_sub_region",
        "conviction_charge_badness",
        "n_records",
        "male_percent",
        "female_percent",
        "age_distribution",
        "crime_distribution",
        *outcome_labels,
        "Bond Percentage",
        "Average Bond Paid",
        "Number Transfers",
        "Miles Traveled",
        "Days spent prior to deportation",
        "Days spent prior to release",
    ]
    stats_df = stats_df[col_order]

    return stats_df

def clean_detention_stays_into_stats_df(df):
    """
    Given a df representing clean detention stays, return a stats dataframe with
    one row per combination of:
        age_group
        gender
        citizenship_country_sub_region
        conviction_charge_badness

    For each dimension, include an "All" rollup level.

    Expected output columns:
        age_group
        gender
        citizenship_country_sub_region
        conviction_charge_badness
        male_percent
        female_percent
        age_distribution
        crime_distribution
        USA - Long term residence likely
        USA - Stay in USA possible
        USA - Detained again
        Deported - country of citizenship
        Deported - 3rd country
        Bond Percentage
        Average Bond Paid
        Number Transfers
        Miles Traveled
        Days spent prior to deportation
        Days spent prior to release
        n_records

    Notes:
    - This function removes outlier / unusable rows first:
        * citizenship_country_sub_region == "Unknown"
        * gender == "Unknown"
        * birth_year is NA
        * detention_release_reason_general in {"Unknown", "Escape"}
    - Percent outputs are on a 0-100 scale.
    - Integer-style metrics are rounded and returned as nullable Int64 where practical.
    - The docstring the user provided seems to have the last two day metrics swapped.
      This implementation uses:
        * Days spent prior to deportation -> avg days where release reason == "Departure / Deportation"
        * Days spent prior to release -> avg days where release reason contains "release" (case-insensitive)
    """

    working_df = df.copy()

    # ------------------------------------------------------------------
    # Validate required columns
    # ------------------------------------------------------------------
    required_cols = [
        "age_group",
        "gender",
        "conviction_charge_badness",
        "citizenship_country_sub_region",
        "birth_year",
        "detention_release_reason_general",
        "deportation_assessment_general",
        "bond_posted_amount_usd",
        "number_transfers_during_stay",
        "domestic_miles_traveled",
        "days_in_detention",
        "age_at_booking"
    ]
    missing_cols = [c for c in required_cols if c not in working_df.columns]
    if missing_cols:
        raise KeyError(f"Missing required columns: {missing_cols}")

    # ------------------------------------------------------------------
    # Remove outliers / schema mismatches
    # ------------------------------------------------------------------
    working_df = working_df[
        working_df["citizenship_country_sub_region"].ne("Unknown")
        & working_df["gender"].ne("Unknown")
        & working_df["birth_year"].notna()
        & ~working_df["detention_release_reason_general"].isin(["Unknown", "Escape"])
        ].copy()

    # Normalize strings used in filters
    for col in [
        "age_group",
        "gender",
        "citizenship_country_sub_region",
        "detention_release_reason_general",
        "conviction_charge_badness",
        "deportation_assessment_general",
    ]:
        working_df[col] = working_df[col].astype("string")

    dims = [
        "age_group",
        "gender",
        # "citizenship_country_region",
        "citizenship_country_sub_region",
        "conviction_charge_badness"
    ]

    def pct(mask: pd.Series) -> float:
        """Percent of True values in mask, 0-100."""
        n = len(mask)
        if n == 0:
            return np.nan
        return round(mask.fillna(False).mean() * 100, 2)

    def avg(series: pd.Series) -> float:
        """Mean with NaN if no non-null values."""
        s = pd.to_numeric(series, errors="coerce").dropna()
        if len(s) == 0:
            return np.nan
        return s.mean()

    def avg_int(series: pd.Series):
        """Rounded mean returned as int-like or NA."""
        value = avg(series)
        if pd.isna(value):
            return pd.NA
        return int(round(value))

    def avg_float(series: pd.Series):
        """Rounded mean returned as int-like or NA."""
        value = avg(series)
        if pd.isna(value):
            return pd.NA
        return float(round(value, 2))

    def age_distribution(series: pd.Series) -> dict:
        """
        Returns dict:
            {integer_age: percent, ...}

        Notes:
        - Ages are coerced to numeric and rounded to the nearest integer age.
        - Percentages keep fractional precision so rare ages are not rounded away.
        """
        s = pd.to_numeric(series, errors="coerce").dropna()
        if len(s) == 0:
            return {}

        age_int = s.round().astype(int)
        dist = (
            age_int.value_counts(normalize=True, dropna=True)
            .mul(100)
            .round(4)
            .sort_index()
        )
        return dist.to_dict()

    def crime_distribution(series: pd.Series) -> dict:
        """
        Returns dict:
            {crime_category: integer_percent, ...}
        summing approximately to 100.
        """
        ordered_categories = [
            "0 - None",
            "1 - Minimal",
            "2 - Low",
            "3 - Moderate",
            "4 - High",
            "5 - Extreme",
        ]
        s = series.dropna().astype("string")
        if len(s) == 0:
            return {category: 0 for category in ordered_categories}

        dist = (
            s.value_counts(normalize=True, dropna=True)
            .mul(100)
            .round()
            .astype(int)
            .reindex(ordered_categories, fill_value=0)
        )
        return dist.to_dict()

    def summarize_subset(sub_df, label_values: dict) -> dict:
        n = len(sub_df)

        release_reason = sub_df["detention_release_reason_general"]
        deport_assess = sub_df["deportation_assessment_general"]

        release_mask = release_reason.str.contains("release", case=False, na=False)
        deport_mask = release_reason.eq("Departure / Deportation")

        bond_non_na_release_pct = (
            np.nan
            if release_mask.sum() == 0
            else round(
                sub_df.loc[release_mask, "bond_posted_amount_usd"].notna().mean() * 100,
                2,
            )
        )

        row = {
            **label_values,
            "n_records": n,
            "male_percent": pct(sub_df["gender"].eq("Male")),
            "female_percent": pct(sub_df["gender"].eq("Female")),
            "age_distribution": age_distribution(sub_df["age_at_booking"]),
            "crime_distribution": crime_distribution(sub_df["conviction_charge_badness"]),
            "USA - Long term residence likely": pct(
                release_reason.eq("Released (long-term stay in USA likely)")
            ),
            "USA - Stay in USA possible": pct(
                release_reason.eq("Released temporarily (long-term stay in USA possible)")
            ),
            "USA - Detained again": pct(
                release_reason.eq("Detention")
            ),
            "Deported - country of citizenship": pct(
                deport_assess.eq("deported to country of citizenship")
            ),
            "Deported - 3rd country": pct(
                deport_assess.eq("deported to country other than country of citizenship")
            ),
            "Bond Percentage": bond_non_na_release_pct,
            "Average Bond Paid": avg_int(sub_df["bond_posted_amount_usd"]),
            "Number Transfers": avg_float(sub_df["number_transfers_during_stay"]),
            "Miles Traveled": avg_int(sub_df["domestic_miles_traveled"]),
            "Days spent prior to deportation": avg_int(
                sub_df.loc[deport_mask, "days_in_detention"]
            ),
            "Days spent prior to release": avg_int(
                sub_df.loc[release_mask, "days_in_detention"]
            )
        }
        return row

    # ------------------------------------------------------------------
    # Build all "All" rollups
    # Example:
    #   group by all 4 dims
    #   then all 3-dim combinations with one set to "All"
    #   ...
    #   then fully aggregated row with all dims = "All"
    # ------------------------------------------------------------------
    output_rows = []

    for keep_count in range(len(dims), -1, -1):
        for kept_dims in itertools.combinations(dims, keep_count):
            kept_dims = list(kept_dims)

            if kept_dims:
                grouped = working_df.groupby(kept_dims, dropna=False, sort=True)
                for keys, sub_df in grouped:
                    if not isinstance(keys, tuple):
                        keys = (keys,)

                    label_values = {dim: "All" for dim in dims}
                    for dim, key in zip(kept_dims, keys):
                        label_values[dim] = key

                    output_rows.append(summarize_subset(sub_df, label_values))
            else:
                label_values = {dim: "All" for dim in dims}
                output_rows.append(summarize_subset(working_df, label_values))

    outcomes_df = pd.DataFrame(output_rows)

    # ------------------------------------------------------------------
    # Clean dtypes / ordering
    # ------------------------------------------------------------------
    col_order = [
        "age_group",
        "gender",
        "citizenship_country_sub_region",
        "conviction_charge_badness",
        "n_records",
        "male_percent",
        "female_percent",
        "age_distribution",
        "crime_distribution",
        "USA - Long term residence likely",
        "USA - Stay in USA possible",
        "USA - Detained again",
        "Deported - country of citizenship",
        "Deported - 3rd country",
        "Bond Percentage",
        "Average Bond Paid",
        "Number Transfers",
        "Miles Traveled",
        "Days spent prior to deportation",
        "Days spent prior to release",
    ]
    outcomes_df = outcomes_df[col_order]

    # Use nullable integer dtype where appropriate
    int_cols = [
        "Average Bond Paid",
        "Miles Traveled",
        "Days spent prior to deportation",
        "Days spent prior to release",
        "n_records",
    ]
    for col in int_cols:
        outcomes_df[col] = outcomes_df[col].astype("Int64")

    # Nice deterministic sort: detailed rows first, then rollups
    def _sort_key(series: pd.Series) -> pd.Series:
        return series.eq("All").astype(int), series.astype(str)

    outcomes_df = outcomes_df.sort_values(
        by=dims,
        key=lambda s: pd.Series(list(zip(s.eq("All").astype(int), s.astype(str)))),
        kind="stable",
    ).reset_index(drop=True)

    return outcomes_df


def get_person_level_outcomes_df_from_cleaned_stays_df(
        clean_detention_stays_df):
    """
    Create person-level outcomes (for the 100-person outcome calculation) from a
    cleaned detention stays dataframe.
    """
    dims = [
        "age_group",
        "gender",
        "citizenship_country_sub_region",
        "conviction_charge_badness",
    ]

    if clean_detention_stays_df is None:
        clean_detention_stays_df = pd.read_pickle(
            r"assets/deportation_data_project/detention_stays_df.pkl"
        )

    required_columns = [
        "detainee_unique_identifier",
        "stay_book_in_date_time",
        "stay_book_out_date",
        "book_out_date_time_last",
        "departed_date",
        "final_order_date",
        "detention_release_reason_general",
        *dims,
    ]
    missing_columns = [c for c in required_columns if c not in clean_detention_stays_df.columns]
    if missing_columns:
        raise KeyError(f"Missing required columns: {missing_columns}")

    working_df = clean_detention_stays_df.copy()

    for date_col in [
        "stay_book_in_date_time",
        "stay_book_out_date",
        "book_out_date_time_last",
        "departed_date",
        "final_order_date",
    ]:
        working_df[date_col] = pd.to_datetime(working_df[date_col], errors="coerce")

    working_df = working_df.sort_values(
        by=["detainee_unique_identifier", "stay_book_in_date_time"],
        kind="stable",
    ).reset_index(drop=True)

    person_key = "detainee_unique_identifier"
    usa_release_values = {
        "Released (long-term stay in USA likely)",
        "Released temporarily (long-term stay in USA possible)",
    }

    # Precompute row-level booleans once
    working_df["_is_departed_date"] = working_df["departed_date"].notna()
    working_df["_is_departure_release"] = (
            working_df["detention_release_reason_general"] == "Departure / Deportation"
    )
    working_df["_has_final_order"] = working_df["final_order_date"].notna()
    working_df["_is_usa_release"] = working_df["detention_release_reason_general"].isin(usa_release_values)

    # First and last stay per person
    first_stays = working_df.groupby(person_key, sort=False, dropna=False).first().reset_index()
    last_stays = working_df.groupby(person_key, sort=False, dropna=False).last().reset_index()

    # Person-level aggregates
    person_agg = working_df.groupby(person_key, sort=False, dropna=False).agg(
        num_stays=(person_key, "size"),
        has_departed=("_is_departed_date", "any"),
        has_departure_release=("_is_departure_release", "any"),
        has_final_order_any=("_has_final_order", "any"),
    ).reset_index()

    # Has prior release to USA: mark prior rows, then any() by person
    working_df["_row_num_within_person"] = working_df.groupby(person_key, sort=False, dropna=False).cumcount()
    working_df["_group_size"] = working_df.groupby(person_key, sort=False, dropna=False)[person_key].transform("size")
    working_df["_is_prior_row"] = working_df["_row_num_within_person"] < (working_df["_group_size"] - 1)
    working_df["_prior_usa_release_flag"] = working_df["_is_prior_row"] & working_df["_is_usa_release"]

    prior_release_agg = working_df.groupby(person_key, sort=False, dropna=False).agg(
        has_prior_release_to_usa=("_prior_usa_release_flag", "any")
    ).reset_index()

    # Merge person-level frame
    person_level_outcomes_df = (
        person_agg
        .merge(
            first_stays[
                [person_key, "stay_book_in_date_time", *dims]
            ].rename(columns={"stay_book_in_date_time": "first_stay_book_in_date_time"}),
            on=person_key,
            how="left",
        )
        .merge(
            last_stays[
                [
                    person_key,
                    "stay_book_in_date_time",
                    "stay_book_out_date",
                    "book_out_date_time_last",
                    "detention_release_reason_general",
                ]
            ].rename(columns={
                "stay_book_in_date_time": "last_stay_book_in_date_time",
                "stay_book_out_date": "last_stay_book_out_date",
                "book_out_date_time_last": "last_book_out_date_time_last",
                "detention_release_reason_general": "final_release_reason",
            }),
            on=person_key,
            how="left",
        )
        .merge(prior_release_agg, on=person_key, how="left")
    )

    person_level_outcomes_df["detainee_Unique_identifier"] = person_level_outcomes_df[person_key]

    # Derived flags
    person_level_outcomes_df["is_deported"] = (
            person_level_outcomes_df["has_departed"]
            | person_level_outcomes_df["has_departure_release"]
    )

    person_level_outcomes_df["final_still_detained"] = (
            person_level_outcomes_df["last_book_out_date_time_last"].isna()
            & person_level_outcomes_df["last_stay_book_out_date"].isna()
    )

    person_level_outcomes_df["outcome_rule_applied"] = None
    person_level_outcomes_df["unclassified_reason"] = None
    person_level_outcomes_df["final_outcome"] = "Other / unclassified"

    # Rule masks in precedence order
    mask_awaiting_deportation = (
            person_level_outcomes_df["has_final_order_any"]
            & ~person_level_outcomes_df["has_departed"]
    )

    mask_deported = (
            ~mask_awaiting_deportation
            & person_level_outcomes_df["is_deported"]
    )

    mask_repeat_detention = (
            ~mask_awaiting_deportation
            & ~mask_deported
            & (person_level_outcomes_df["num_stays"] >= 2)
            & person_level_outcomes_df["has_prior_release_to_usa"]
            & person_level_outcomes_df["final_still_detained"]
    )

    mask_no_status_change = (
            ~mask_awaiting_deportation
            & ~mask_deported
            & ~mask_repeat_detention
            & (
                    person_level_outcomes_df["final_release_reason"]
                    == "Released with no status change (further proceedings likely)"
            )
    )

    mask_single_likely = (
            ~mask_awaiting_deportation
            & ~mask_deported
            & ~mask_repeat_detention
            & ~mask_no_status_change
            & (person_level_outcomes_df["num_stays"] == 1)
            & (
                    person_level_outcomes_df["final_release_reason"]
                    == "Released (long-term stay in USA likely)"
            )
    )

    mask_single_possible = (
            ~mask_awaiting_deportation
            & ~mask_deported
            & ~mask_repeat_detention
            & ~mask_no_status_change
            & ~mask_single_likely
            & (person_level_outcomes_df["num_stays"] == 1)
            & (
                    person_level_outcomes_df["final_release_reason"]
                    == "Released temporarily (long-term stay in USA possible)"
            )
    )

    # Apply outcomes
    person_level_outcomes_df.loc[mask_awaiting_deportation, "final_outcome"] = "Awaiting Deportation"
    person_level_outcomes_df.loc[mask_awaiting_deportation, "outcome_rule_applied"] = "final_order_no_departure"

    person_level_outcomes_df.loc[mask_deported, "final_outcome"] = "Deported"
    person_level_outcomes_df.loc[mask_deported, "outcome_rule_applied"] = "deported_precedence"

    person_level_outcomes_df.loc[mask_repeat_detention, "final_outcome"] = "Released to USA - will be detained again"
    person_level_outcomes_df.loc[mask_repeat_detention, "outcome_rule_applied"] = "repeat_detention_after_release"

    person_level_outcomes_df.loc[mask_no_status_change, "final_outcome"] = "Released to USA - will be detained again"
    person_level_outcomes_df.loc[mask_no_status_change, "outcome_rule_applied"] = "released_with_no_status_change"

    person_level_outcomes_df.loc[mask_single_likely, "final_outcome"] = "Released to USA - long term residence likely"
    person_level_outcomes_df.loc[mask_single_likely, "outcome_rule_applied"] = "single_stay_long_term_likely"

    person_level_outcomes_df.loc[
        mask_single_possible, "final_outcome"] = "Released to USA - long term residence possible"
    person_level_outcomes_df.loc[mask_single_possible, "outcome_rule_applied"] = "single_stay_long_term_possible"

    # Unclassified reasons
    unclassified_mask = person_level_outcomes_df["final_outcome"].eq("Other / unclassified")
    final_release_reason = person_level_outcomes_df["final_release_reason"]

    person_level_outcomes_df.loc[
        unclassified_mask & final_release_reason.isna(),
        "unclassified_reason"
    ] = "missing_final_release_reason"

    person_level_outcomes_df.loc[
        unclassified_mask & final_release_reason.isin(["Unknown", "Escape", "Died"]),
        "unclassified_reason"
    ] = "excluded_terminal_status:" + final_release_reason.fillna("")

    person_level_outcomes_df.loc[
        unclassified_mask & final_release_reason.isin(["Departure / Deportation", "Detention"]),
        "unclassified_reason"
    ] = "terminal_status_not_mapped:" + final_release_reason.fillna("")

    person_level_outcomes_df.loc[
        unclassified_mask
        & (person_level_outcomes_df["num_stays"] > 1)
        & final_release_reason.isin(list(usa_release_values)),
        "unclassified_reason"
    ] = "released_to_usa_but_not_single_stay"

    remaining_unclassified = (
            unclassified_mask
            & person_level_outcomes_df["unclassified_reason"].isna()
    )
    person_level_outcomes_df.loc[
        remaining_unclassified,
        "unclassified_reason"
    ] = "no_matching_rule:" + final_release_reason.fillna("")

    person_level_outcomes_df = person_level_outcomes_df.sort_values(
        by=[person_key],
        kind="stable",
    ).reset_index(drop=True)

    # Build missing_dims_df from first stays, vectorized
    missing_dims_df = (
        first_stays[[person_key, "stay_book_in_date_time", *dims]]
        .melt(
            id_vars=[person_key, "stay_book_in_date_time"],
            value_vars=dims,
            var_name="missing_dim",
            value_name="dim_value",
        )
    )
    missing_dims_df = missing_dims_df[missing_dims_df["dim_value"].isna()].copy()

    if len(missing_dims_df) > 0:
        missing_dims_df["detainee_Unique_identifier"] = missing_dims_df[person_key]
        missing_dims_df = missing_dims_df.rename(
            columns={"stay_book_in_date_time": "first_stay_book_in_date_time"}
        )[
            [
                "detainee_unique_identifier",
                "detainee_Unique_identifier",
                "missing_dim",
                "first_stay_book_in_date_time",
            ]
        ].sort_values(
            by=["detainee_unique_identifier", "missing_dim"],
            kind="stable",
        ).reset_index(drop=True)
    else:
        missing_dims_df = pd.DataFrame(
            columns=[
                "detainee_unique_identifier",
                "detainee_Unique_identifier",
                "missing_dim",
                "first_stay_book_in_date_time",
            ]
        )

    # Optional cleanup of helper columns happened before merge, so nothing extra here
    return person_level_outcomes_df, missing_dims_df


def summarize_unclassified_person_level_outcomes(person_level_outcomes_df):
    """
    Summarize root causes of "Other / unclassified" rows produced by
    get_person_level_outcomes_df_from_cleaned_stays_df.

    Returns counts grouped by:
      - unclassified_reason
      - final_release_reason
    """
    required_cols = ["final_outcome", "unclassified_reason", "final_release_reason"]
    missing_cols = [c for c in required_cols if c not in person_level_outcomes_df.columns]
    if missing_cols:
        raise KeyError(f"Missing required columns: {missing_cols}")

    unclassified_df = person_level_outcomes_df[
        person_level_outcomes_df["final_outcome"].eq("Other / unclassified")
    ].copy()

    if len(unclassified_df) == 0:
        return pd.DataFrame(columns=["unclassified_reason", "final_release_reason", "n_people"])

    summary_df = (
        unclassified_df
        .groupby(["unclassified_reason", "final_release_reason"], dropna=False)
        .size()
        .rename("n_people")
        .reset_index()
        .sort_values("n_people", ascending=False, kind="stable")
        .reset_index(drop=True)
    )
    return summary_df


if __name__ == "__main__":
    # Get the data:
    print("cleaning detention stay data")
    clean_detention_stays_df = build_and_pickle_detention_stays(row_limit=None)
    clean_detention_stays_df.to_csv("assets/deportation_data_project/detention-stays_cleaned.csv")
    clean_detention_stays_df.to_pickle(r"assets/deportation_data_project/detention_stays_df.pkl")

    # Make the mini
    # tic()
    # clean_detention_stays_df_mini = clean_detention_stays_df.sample(n=50000, random_state=42)
    # toc("sample mini df")
    #
    # tic()
    # clean_detention_stays_df_mini.to_csv("assets/deportation_data_project/detention-stays_cleaned_mini.csv")
    # toc("write mini csv")

    print("making outcomes df")

    outcomes_df, troubleshoot = get_person_level_outcomes_df_from_cleaned_stays_df(clean_detention_stays_df)

    outcomes_df.to_pickle(
        r"C:\Users\witzi\OneDrive\Documents\neu_part_2\CS7250\CS7250_trends_in_american_immigration_enforcement\assets\deportation_data_project\person_level_outcomes_df.pkl")

    print("run export_stats_df_for_infographic!!")

    # Get data from pickle
    # clean_detention_stays_df = pd.read_pickle(r"assets/deportation_data_project/detention_stays_df.pkl")
    # stays_df = expand_stint_tuples_with_geo(clean_detention_stays_df)
    # export_stays_csv(stays_df)
