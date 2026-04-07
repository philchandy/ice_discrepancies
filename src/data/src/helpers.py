"""
All-purpose helpers for the project.

"""
import os
import pandas as pd


def get_raw_dataset_df(data_set_name):
    """
    Given a data set name, get the raw dataset df.

    tbd - decide on reading in everything as strings. I don't think we need to for most of these sets

    :param data_set_name: data set name
    :return: a raw dataframe with no cleaning
    """
    data_lookup = {
        "detention_stays": r"assets/deportation_data_project/detention-stays-latest.csv",
        "detention_stints": r"assets/deportation_data_project/detention-stints-latest.csv"
    }

    # Print warning with helpful reminder of data sets
    if data_set_name not in data_lookup.keys():
        raise ValueError(f"You attempted to get the data set {data_set_name}.\nThis isn't a valid data set. "
                         f"Valid data sets are: {list(data_lookup.keys())}")

    # return the raw dataFrame
    return pd.read_csv(data_lookup[data_set_name])


def clean_data_set(data_set_name, raw_df):
    """
    Given a data set name, clean it according to the specified cleaning procedure for that dataset.

    TBD - make the cleanings for other sets

    :param raw_df: uncleaned raw dataFrame
    :param data_set_name: data set name
    :return: cleaned dataFrame
    """
    from detention_data_cleaning import clean_detention_stays

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


def pickle_cleaned_dataset(data_set_name):
    """
    Given a data set name, do the following:
        (1) get raw dataFrame
        (2) clean dataframe
        (3) pickle and save the cleaned dataFrame
        (4) return the df

    :param data_set_name: data set name
    :return: the cleaned dataFrame (which was also pickled!)
    """

    data_lookup = {
        "detention_stays" : {
            "pickle_path": r"assets/deportation_data_project/detention_stays_df.pkl"
        },
        "detention_stints": {
            "pickle_path": r"assets/deportation_data_project/detention_stints_df.pkl"
        }
    }

    pickle_path = data_lookup[data_set_name]["pickle_path"]
    raw_df = get_raw_dataset_df(data_set_name=data_set_name)
    clean_df = clean_data_set(data_set_name=data_set_name, raw_df=raw_df)
    clean_df.to_pickle(pickle_path)
    return clean_df


def get_cleaned_pickle_data(data_set_name, extract_clean_and_pickle_on_error=False):
    """
    Get the cleaned dataFrame associated with the given data_set_name.

    :param data_set_name: data set name
    :param extract_clean_and_pickle_on_error: if True, this will go through and get the df, clean it,
                                              pickle it, and return that cleaned df.
    :return: usable cleaned dataFrame
    """

    data_lookup = {
        "detention_stays": {
            "pickle_path": r"assets/deportation_data_project/detention_stays_df.pkl"
        },
        "detention_stints": {
            "pickle_path": r"assets/deportation_data_project/detention_stints_df.pkl"
        }
    }

    pickle_path = data_lookup[data_set_name]["pickle_path"]

    if os.path.exists(pickle_path):
        return pd.read_pickle(pickle_path)
    else:
        if extract_clean_and_pickle_on_error:
            print(f"There's no existing pickle at {pickle_path}\nfor data {data_set_name}. "
                  f"Creating one (may take several minutes)")
            cleaned_df = pickle_cleaned_dataset(data_set_name=data_set_name)
            return cleaned_df
        else:
            raise ValueError(f"Couldn't find the file at {pickle_path}. Resolve that issue by finding the file, "
                             f"fixing paths, or by setting extract_clean_and_pickle_on_error=True.")


def flag_old_data_to_project_member():
    """
    The deportation data project data is too large to git commit, so we download it from Google Drive.

    If there is a filename that Sarah is working with that Phil or Max do not have, flag it.
    :return:
    """

    # To do - grow this list
    required_files = [
        r"assets/deportation_data_project/detention-stints-latest.csv",
        r"assets/deportation_data_project/detention-stints-latest.csv",
        "new one"
    ]

    file_existence_tracking = {}

    for file in required_files:
        file_existence_tracking[file] = os.path.exists(file)

    # Print helpful reminder to us to update files from the Drive
    drive_link = r"https://drive.google.com/drive/u/1/folders/1a6TteZgnC1xzOpxMujLFvVdzbZL2osia"

    # ~ ChatGPT below ~
    missing_files = [f for f, exists in file_existence_tracking.items() if not exists]
    if missing_files:
        files = "\n".join(missing_files)
        print(f"⚠️ Missing required data files:\n{files}\n"
              f"Download enter assets folder from Google Drive and replace/combine with YOUR assets folder:"
              f"\n{drive_link}")
    else:
        print("✅ All required data files are present.")


# Example call
df = get_cleaned_pickle_data(data_set_name="detention_stays", extract_clean_and_pickle_on_error=True)