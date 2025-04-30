"""This module is responsible for testing functions from app/data_processing.py"""

from io import BytesIO

import pytest
import pandas as pd

from src.data_processing import extract_banks_data, extract_countries_data


@pytest.fixture(name="mock_df")
def fixture_mock_df():
    """Exemplary data stored in Excel file.

    The data includes following cases:
    - headquarter with branches,
    - headquarter without branches,
    - branch without headquarter,
    - many banks from different countries,
    - many banks from the same country,
    - empty address field.

    Returns
    -------
    pandas.DataFrame
        Pandas DataFrame containig exemplary data.
    """
    return pd.DataFrame(
        {
            "COUNTRY ISO2 CODE": ["PL", "PL", "PL", "DE", "DE", "PL", "DE"],
            "SWIFT CODE": [
                "A1234567890",  # branch with headquarter
                "A1234567XXX",  # headquarter with branch
                "A0987654321",  # branch without headquarter
                "D1234567890",
                "D1234567XXX",
                "P1234567XXX",  # headquarter without branch
                "C1234567890",
            ],
            "NAME": [
                "Alior Bank",
                "Alior Bank",
                "Alior Bank",
                "Deutsche Bank",
                "Deutsche Bank",
                "PKO Bank",
                "Commerzbank",
            ],
            "ADDRESS": [
                "Alior Bank Address",
                "Alior Bank Address",
                " ",  # "empty" address (resembles actual file)
                "Deutsche Bank Address",
                "Deutsche Bank Address",
                "PKO Bank Address",
                "",  # empty address
            ],
            "COUNTRY NAME": [
                "Poland",
                "Poland",
                "Poland",
                "Germany",
                "Germany",
                "Poland",
                "Germany",
            ],
        }
    )


@pytest.fixture(name="expected_banks_result")
def fixture_expected_banks_result():
    """Expected result of extracting banks data.

    Returns
    -------
    list[dict]
        List of dicts representing banks.
    """
    return [
        {
            "country_iso2": "PL",
            "swift_code": "A1234567XXX",
            "name": "Alior Bank",
            "address": "Alior Bank Address",
            "is_headquarter": True,
            "potential_hq": "A1234567XXX",
        },
        {
            "country_iso2": "DE",
            "swift_code": "D1234567XXX",
            "name": "Deutsche Bank",
            "address": "Deutsche Bank Address",
            "is_headquarter": True,
            "potential_hq": "D1234567XXX",
        },
        {
            "country_iso2": "PL",
            "swift_code": "P1234567XXX",
            "name": "PKO Bank",
            "address": "PKO Bank Address",
            "is_headquarter": True,
            "potential_hq": "P1234567XXX",
        },
        {
            "country_iso2": "PL",
            "swift_code": "A0987654321",
            "name": "Alior Bank",
            "address": " ",
            "is_headquarter": False,
            "potential_hq": "A0987654XXX",
        },
        {
            "country_iso2": "PL",
            "swift_code": "A1234567890",
            "name": "Alior Bank",
            "address": "Alior Bank Address",
            "is_headquarter": False,
            "potential_hq": "A1234567XXX",
        },
        {
            "country_iso2": "DE",
            "swift_code": "C1234567890",
            "name": "Commerzbank",
            "address": None,
            "is_headquarter": False,
            "potential_hq": "C1234567XXX",
        },
        {
            "country_iso2": "DE",
            "swift_code": "D1234567890",
            "name": "Deutsche Bank",
            "address": "Deutsche Bank Address",
            "is_headquarter": False,
            "potential_hq": "D1234567XXX",
        },
    ]


@pytest.fixture(name="expected_countries_result")
def fixture_expected_countries_result():
    """Expected result of extracting countries data.

    Returns
    -------
    list[dict]
        List of dicts representing countries.
    """
    return [
        {"iso2": "DE", "name": "Germany"},
        {"iso2": "PL", "name": "Poland"},
    ]


def test_extract_banks_data(mock_df, expected_banks_result):
    """Tests extracting banks data.

    Parameters
    ----------
    mock_df : pandas.DataFrame
        The data used in mock Excel file.
    expected_banks_result : list[dict]
        List of dicts representing expected results.
    """
    output = BytesIO()

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        mock_df.to_excel(writer, sheet_name="Sheet1", index=False)

    xslx_data = extract_banks_data(output)

    assert xslx_data == expected_banks_result, "Extracted banks' data is incorrect"


def test_extract_countries_data(mock_df, expected_countries_result):
    """Tests extracting countries data.

    Parameters
    ----------
    mock_df : pandas.DataFrame
        The data used in mock Excel file.
    expected_countries_result : list[dict]
        List of dicts representing expected results.
    """
    output = BytesIO()

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        mock_df.to_excel(writer, sheet_name="Sheet1", index=False)

    xslx_data = extract_countries_data(output)

    assert (
        xslx_data == expected_countries_result
    ), "Extracted countries' data is incorrect"
