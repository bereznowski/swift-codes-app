"""This module includes unit tests for functions from src/data_processing.py"""

from io import BytesIO

import pandas as pd

from src.data_processing import extract_banks_data, extract_countries_data


def test_extract_banks_data(mock_df, banks_data_after_excel):
    """Tests extracting banks data.

    Parameters
    ----------
    mock_df : pandas.DataFrame
        The data used in mock Excel file.
    banks_data_after_excel : list[dict]
        List of dicts representing expected results.
    """
    output = BytesIO()

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        mock_df.to_excel(writer, sheet_name="Sheet1", index=False)

    xslx_data = extract_banks_data(output)

    assert xslx_data == banks_data_after_excel, "Extracted banks' data is incorrect"


def test_extract_countries_data(mock_df, countries_data_after_excel):
    """Tests extracting countries data.

    Parameters
    ----------
    mock_df : pandas.DataFrame
        The data used in mock Excel file.
    countries_data_after_excel : list[dict]
        List of dicts representing expected results.
    """
    output = BytesIO()

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        mock_df.to_excel(writer, sheet_name="Sheet1", index=False)

    xslx_data = extract_countries_data(output)

    assert (
        xslx_data == countries_data_after_excel
    ), "Extracted countries' data is incorrect"
