"""This module is responsible for extracting required information from the Excel Spreadsheet."""

import numpy as np
import pandas as pd


def extract_banks_data(file_path: str):
    """Extracts banks data from the Excel file.

    Parameters
    ----------
    file_path : str
        The path of the Excel file.

    Returns
    -------
    list[dict]
        Dictionaries of values to be used during banks' table model creation.
        Structure of the dictionaries:
            {
                "country_iso2": str,
                "swift_code": str,
                "name": str,
                "address": str,
                "is_headquarter": bool,
                "potential_hq": str
            }

    Raises
    ------
    FileNotFoundError
        When incorrect file path.
    """
    columns_to_use = ["SWIFT CODE", "NAME", "ADDRESS", "COUNTRY ISO2 CODE"]
    columns_renaming_dict = {
        "SWIFT CODE": "swift_code",
        "NAME": "name",
        "ADDRESS": "address",
        "COUNTRY ISO2 CODE": "country_iso2",
    }

    try:
        df = (
            pd.read_excel(file_path, usecols=columns_to_use)
            .rename(columns=columns_renaming_dict)
            .replace({np.nan: ""})  # otherwise empty strings are nan
        )
    except FileNotFoundError:
        print("Path to the file containg banks data is incorrect.")
        print("No banks data extracted.")
        return [{}]

    df["is_headquarter"] = df["swift_code"].str.endswith("XXX")
    df["potential_hq"] = df["swift_code"].str[:8] + str(
        "XXX"
    )  # these are potential headquarters
    # branches without a headquarter exist (e.g., ALBPPLP1BMW)
    # checks are performed during DB insertion

    return df.sort_values(  # headquarters need to be inserted first for the referential integrity
        by=["is_headquarter", "swift_code"], ascending=[False, True]
    ).to_dict(
        "records"
    )


def extract_countries_data(file_path: str):
    """Extracts countries data from the Excel file.

    Parameters
    ----------
    file_path : str
        The path of the Excel file.

    Returns
    -------
    list[dict]
        Dictionaries of values to be used during countries' table model creation.
        Structure of the dictionaries:
            {
                "iso2": str,
                "name": str
            }

    Raises
    ------
    FileNotFoundError
        When incorrect file path.
    """
    columns_to_use = ["COUNTRY ISO2 CODE", "COUNTRY NAME"]
    columns_renaming_dict = {
        "COUNTRY ISO2 CODE": "iso2",
        "COUNTRY NAME": "name",
    }

    try:
        return (
            pd.read_excel(file_path, usecols=columns_to_use)
            .drop_duplicates()  # there can be many banks from the same country
            .rename(columns=columns_renaming_dict)
            .sort_values(by="iso2")
            .to_dict("records")
        )
    except FileNotFoundError:
        print("Path to the file containg countries data is incorrect.")
        print("No countries data extracted.")
        return {}
