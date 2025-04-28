"""
This module is responsible for extracting required information from the Excel Spreadsheet.
"""

import os
import numpy as np
import pandas as pd


def extract_banks_data(file_path: str):
    columns_to_use = ["SWIFT CODE", "NAME", "ADDRESS", "COUNTRY ISO2 CODE"]
    columns_renaming_dict = {
        "SWIFT CODE": "swift_code",
        "NAME": "name",
        "ADDRESS": "address",
        "COUNTRY ISO2 CODE": "iso2",
    }

    df_banks = (
        pd.read_excel(file_path, usecols=columns_to_use)
        .rename(columns=columns_renaming_dict)
        .replace({np.nan: None})
    )

    df_banks["is_headquarter"] = df_banks["swift_code"].str.endswith("XXX")
    df_banks["base_code"] = df_banks["swift_code"].str[:8]
    df_banks.loc[~df_banks["is_headquarter"], "hq_swift_code"] = df_banks[
        "base_code"
    ] + str("XXX")
    df_banks = df_banks.sort_values(by="is_headquarter", ascending=False)

    print(df_banks.head())
    print(df_banks.tail())


def extract_countries_data(file_path: str):
    columns_to_use = ["COUNTRY ISO2 CODE", "COUNTRY NAME"]
    columns_renaming_dict = {
        "COUNTRY ISO2 CODE": "country_iso2",
        "COUNTRY NAME": "country_name",
    }

    return (
        pd.read_excel(file_path, usecols=columns_to_use)
        .drop_duplicates()
        .rename(columns=columns_renaming_dict)
        .to_dict("records")
    )

extract_banks_data("../data/swift_codes.xlsx")
