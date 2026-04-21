"""
Data mappings - this goes column by column to either add helper columns or clean data.

Column cleaning - uses apply_column_cleaning to clean a column IN PLACE
New column mapping - uses apply data map to add a new column based off a single column.*
    * there may be more complicated cleaning functions applied for multi-column.

"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from tabulate import tabulate
import math
from geopy.distance import geodesic

from helpers import get_cleaned_pickle_data


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
                .replace(r'^\s*$', np.nan, regex=True)
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
    Given a column name, this searches in the lookups folder for the associated map.
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
                "mapping_columns": {"region": "citizenship_country_region"},
                "nan_mapping_values": {
                    "citizenship_country_region": "Unknown"
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
        insertion_index = df.columns.get_loc(column_name) + 1
        nan_map = column_details["nan_mapping_values"]

        # For each column in mapping columns, apply the map
        # The columns are inserted directly after column_name or whatever was the recently inserted column
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

            mapped_series = df_col_normalized.map(mapping_dict)

            # Insert column at correct position
            df.insert(insertion_index, new_column_name, mapped_series)

            # Move insertion point to the right for next column
            insertion_index += 1

    # return the df with the added columns!
    return df


def print_column_counts(df, category_limit=50):
    """
    ~ChatGPT created~

    For each column in df:
    - Print column name (bold style)
    - If distinct values <= category_limit → print value counts in 4-column table
    - Else → print message + 10 sample distinct values (also in table)
    """
    for col in df.columns:
        print(f"\n\033[1m{col}\033[0m")  # bold

        unique_vals = df[col].drop_duplicates()
        n_unique = unique_vals.shape[0]

        if n_unique <= category_limit:
            counts = df[col].value_counts(dropna=False)

            # Prepare rows: pair up values into 4 columns (Value, Count, Value, Count)
            items = list(counts.items())
            rows = []
            for i in range(0, len(items), 2):
                left = items[i]
                right = items[i+1] if i+1 < len(items) else ("", "")

                rows.append([
                    left[0], left[1],
                    right[0], right[1]
                ])

            print(tabulate(
                rows,
                headers=["Value", "Count", "Value", "Count"],
                tablefmt="rounded_outline"
            ))

        else:
            print(f"{col} column has {n_unique} distinct values, so not showing counts.")
            print("Here are 10 distinct samples:")

            samples = unique_vals.head(10).tolist()

            # Format samples into 4 columns (just values)
            rows = []
            for i in range(0, len(samples), 4):
                row = samples[i:i+4]
                row += [""] * (4 - len(row))  # pad
                rows.append(row)

            print(tabulate(
                rows,
                headers=["Sample 1", "Sample 2", "Sample 3", "Sample 4"],
                tablefmt="rounded_outline"
            ))


def list_collapse(code_list):
    """
    Given a list of words, if length > 4 collapse adjacent words in the middle of the list. Don't include first
    or last element in any collapsing.

    [EAC, EAC]           --> [EAC, EAC]
    [EAC]                --> [EAC]
    [EAC, EAC, TAC]      --> [EAC, EAC, TAC]
    [EAC, EAC, EAC]      --> [EAC, EAC, EAC]
    [EAC, EAC, EAC, EAC] --> [EAC, EAC, EAC]

    :param code_list: a list of facility codes
    :return: a list of facility codes with the center ones collapsed if there are adjacent codes.
    """

    # Don't mutate input list
    code_list = code_list.copy()

    # Quick return for None or short list
    if code_list is None:
        return None

    if len(code_list) <= 3:
        return code_list

    # Iterate through list and create delete_indices
    delete_indices = []
    for i in range(2, len(code_list) - 1):
        if code_list[i] == code_list[i - 1]:
            delete_indices.append(i)

    # Quick return
    delete_indices.reverse()

    # Remove
    for index in delete_indices:
        del code_list[index]

    return code_list


def get_stint_start_and_stop_datetimes(df):
    """
    Iterate through the list in collapsed_facility_codes and create a list of stay times, where the first and last
    are exact stay times and the middles ones are estimated stay times, with an equal duration applied to each middle
    stay.

    :param df:
    :return: df with column added "stint_estimated_start_and_stop_datetimes"
    """

    return df


def get_estimated_facility_count_data(df):
    """
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
    Occasionally

    :param df:
    :return:
    """
    return


def calculate_distances_traveled(df):
    """
    Given a df with a column called facility_codes, use the facility_code_map to calculate the total distance
    traveled from the first facility to the intermediate ones, to the last. Then also calculate the deporation
    distance, and add the total distance.

    :param df:
    :return:
    """

    facility_code_map = pd.read_csv(r"lookups/factory_code_map_with_coordinates.csv", encoding="latin1")

    # Add a set representing the coordinates
    facility_code_map["(lat, long)"] = list(
        zip(facility_code_map["latitude"], facility_code_map["longitude"])
    )

    facility_code_map = facility_code_map[~facility_code_map["latitude"].isna()]

    # Create a quick lookup
    code_to_lat_long_lookup = (
        facility_code_map
        .set_index("code")["(lat, long)"]
        .to_dict()
    )

    def dissect_code_distance(code_list):
        """
        Iterate through a code list and add up the segment distances.

        When calculating each segment, if one of the (lat, long) pairs is (nan, nan), and
        the other isn't -> we assume 0 distance traveled and that the
        :param code_list: list of codes like ["FSF", "FLO"]
        :return: total distance in that list of codes
        """
        total_miles = 0

        # Single code --> quick return
        if len(code_list) == 1:
            return total_miles

        # Iterate across codes and sum distance
        for i in range(len(code_list) - 1):
            start = code_to_lat_long_lookup[code_list[i]]
            end = code_to_lat_long_lookup[code_list[i + 1]]
            total_miles += geodesic(start, end).miles

        return int(total_miles)

    def distance_from_last_code(last_facility_code, departure_country):
        # helper to do rowwise calcs to df
        last_coordinates = code_to_lat_long_lookup[last_facility_code]
        dest_coordinates = country_coordinate_lookup.get(departure_country)
        return int(geodesic(last_coordinates, dest_coordinates).miles)

    # For deportation - define locations
    country_coordinate_lookup = country_to_largest_city_coordinates = {
        "USA": (40.7128, -74.0060),          # New York City
        "Canada": (43.6532, -79.3832),       # Toronto
        "Mexico": (19.4326, -99.1332),       # Mexico City
        "Brazil": (-23.5505, -46.6333),      # São Paulo
        "Argentina": (-34.6037, -58.3816),   # Buenos Aires
        "Colombia": (4.7110, -74.0721),      # Bogotá
        "Peru": (-12.0464, -77.0428),        # Lima
        "Chile": (-33.4489, -70.6693),       # Santiago
        "UK": (51.5074, -0.1278),            # London
        "France": (48.8566, 2.3522),         # Paris
        "Germany": (52.5200, 13.4050),       # Berlin
        "Spain": (40.4168, -3.7038),         # Madrid
        "Italy": (41.9028, 12.4964),         # Rome
        "Netherlands": (52.3676, 4.9041),    # Amsterdam
        "Sweden": (59.3293, 18.0686),        # Stockholm
        "Norway": (59.9139, 10.7522),        # Oslo
        "Denmark": (55.6761, 12.5683),       # Copenhagen
        "Finland": (60.1699, 24.9384),       # Helsinki
        "Poland": (52.2297, 21.0122),        # Warsaw
        "Ukraine": (50.4501, 30.5234),       # Kyiv
        "Russia": (55.7558, 37.6173),        # Moscow
        "Turkey": (41.0082, 28.9784),        # Istanbul
        "India": (19.0760, 72.8777),         # Mumbai
        "China": (31.2304, 121.4737),        # Shanghai
        "Japan": (35.6762, 139.6503),        # Tokyo
        "South Korea": (37.5665, 126.9780),  # Seoul
        "Indonesia": (-6.2088, 106.8456),    # Jakarta
        "Thailand": (13.7563, 100.5018),     # Bangkok
        "Vietnam": (21.0285, 105.8542),      # Hanoi
        "Philippines": (14.5995, 120.9842),  # Manila
        "Pakistan": (24.8607, 67.0011),      # Karachi
        "Bangladesh": (23.8103, 90.4125),    # Dhaka
        "Australia": (-33.8688, 151.2093),   # Sydney
        "New Zealand": (-36.8485, 174.7633), # Auckland
        "South Africa": (-26.2041, 28.0473), # Johannesburg
        "Nigeria": (6.5244, 3.3792),         # Lagos
        "Egypt": (30.0444, 31.2357),         # Cairo
        "Kenya": (-1.2921, 36.8219),         # Nairobi
        "Morocco": (33.5731, -7.5898),       # Casablanca
        "Ethiopia": (9.1450, 40.4897),       # Addis Ababa
        "Saudi Arabia": (24.7136, 46.6753),  # Riyadh
        "UAE": (25.2048, 55.2708),           # Dubai
        "Israel": (31.7683, 35.2137),        # Jerusalem
        "Iran": (35.6892, 51.3890),          # Tehran
        "Not Applicable": (None, None)       # Won't allow distance calcs
    }

    # apply
    df["deportation_miles_traveled"] = df.apply(
        lambda row: distance_from_last_code(
            row["detention_facility_code_last"],
            row["departure_country"]
        ),
        axis=1
    )

    df["domestic_miles_traveled"] = df["facility_codes"].apply(dissect_code_distance)

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

    # --- 1. Identifier ---
    id_cols = [
        "unique_identifier"
    ]

    # --- 2. Demographics ---
    demo_cols = [
        "age_at_booking",
        "birth_year",
        "gender",
        "ethnicity",
        "marital_status",
        "religion",
        "clean_religion",
        "overarching_religion",
        "citizenship_country",
        "citizenship_country_region",
        "entry_status"
    ]

    # --- 3. Crime / legal status ---
    crime_cols = [
        "most_serious_conviction_code",
        "most_serious_conviction_charge",
        "final_charge",
        "book_in_criminality",
        "felon",
        "case_status",
        "case_category",
        "case_threat_level",
        "final_order_of_removal",
        "final_order_date"
    ]

    # --- 4. Departure / outcome ---
    departure_cols = [
        "departed_date",
        "departure_country",
        "departure_country_region",
        "detention_release_reason",
        "stay_release_reason",
        "final_program",
        "bond_posted_date",
        "bond_posted_amount_usd",
        "initial_bond_set_amount_usd"
    ]

    # --- 5. Stay summary ---
    stay_summary_cols = [
        "stay_ID",
        "n_stays",
        "n_stints",
        "days_in_detention"
    ]

    # --- 6. Stay timeline ---
    stay_time_cols = [
        "stay_book_in_date_time",
        "stay_book_out_date_time",
        "stay_book_out_date"
    ]

    # --- 7. Facility / movement ---
    facility_cols = [
        "facility_codes",
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
        "book_out_date_time_last"
    ]

    # Combine all ordered columns
    ordered_cols = (
        id_cols +
        demo_cols +
        crime_cols +
        departure_cols +
        stay_summary_cols +
        stay_time_cols +
        facility_cols
    )

    # Keep only columns that exist in df
    ordered_cols = [c for c in ordered_cols if c in df.columns]

    # Append any remaining columns not explicitly ordered
    remaining_cols = [c for c in df.columns if c not in ordered_cols]

    return df[ordered_cols + remaining_cols]


def assess_deportation(df):
    """
    Adds a column to df called deportation_assessment to track if person wasn't deported, was deported home,
    or was deported to a 3rd country.
    :param df:
    :return:
    """

    df["deporation_assessment"] = np.select(
        [
            df["departure_country"] == "Not Applicable",
            df["departure_country"] == df["citizenship_country"],
            df["departure_country"] != df["citizenship_country"],
        ],
        [
            "not deported",
            "deported to country of citizenship",
            "deported to another country than their citizenship: citizen of "
            + df["citizenship_country"].astype(str)
            + " --> but deported to "
            + df["departure_country"].astype(str),
        ],
        default=None
    )
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
    detention_stays_df = reorder_and_group_columns_for_clarity(detention_stays_df)
    detention_stays_df = datetime_normalization_with_error_coercion(detention_stays_df)

    # Split detention lists
    detention_stays_df["facility_codes"] = detention_stays_df["detention_facility_codes_all"].str.split("; ")

    # days in detention
    seconds_per_day = 60 * 60 * 24
    detention_stays_df["days_in_detention"] = (
                                                      detention_stays_df["stay_book_out_date_time"] -
                                                      detention_stays_df["stay_book_in_date_time"]
                                              ).dt.total_seconds() / seconds_per_day

    # age
    detention_stays_df["age_at_booking"] = (
            detention_stays_df["stay_book_in_date_time"].dt.year - detention_stays_df["birth_year"])

    # distances traveled
    detention_stays_df = calculate_distances_traveled(detention_stays_df)
    detention_stays_df=assess_deportation(detention_stays_df)

    return detention_stays_df
