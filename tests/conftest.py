"""This module includes fixtures which are used by more than one test module."""

import pytest
import pandas as pd

from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool


@pytest.fixture(name="banks_data_after_excel")
def fixture_banks_data_after_excel():
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
            "country_iso2": "PL",
            "swift_code": "A1234567891",
            "name": "Alior Bank",
            "address": "Alior Bank Address",
            "is_headquarter": False,
            "potential_hq": "A1234567XXX",
        },
        {
            "country_iso2": "DE",
            "swift_code": "C1234567890",
            "name": "Commerzbank",
            "address": "",
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


@pytest.fixture(name="countries_data_after_excel")
def fixture_countries_data_after_excel():
    """Exemplary countries data inserted into database.

    Returns
    -------
    list[dict]
        List of dicts representing countries.
    """
    return [{"iso2": "DE", "name": "Germany"}, {"iso2": "PL", "name": "Poland"}]


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
            "COUNTRY ISO2 CODE": ["PL", "PL", "PL", "PL", "DE", "DE", "PL", "DE"],
            "SWIFT CODE": [
                "A1234567891",
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
                "Alior Bank",
                "Deutsche Bank",
                "Deutsche Bank",
                "PKO Bank",
                "Commerzbank",
            ],
            "ADDRESS": [
                "Alior Bank Address",
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
                "Poland",
                "Germany",
                "Germany",
                "Poland",
                "Germany",
            ],
        }
    )


@pytest.fixture(name="session")
def fixture_session():
    """Creates new session for in-memory database.

    Yields
    -------
    sqlmodel.Session
        SQLModel Session connected with in-memory database.
    """
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
