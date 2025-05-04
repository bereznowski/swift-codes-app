"""This module includes fixtures which are used by more than one test module."""

import pytest
import pandas as pd

from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from src.app import app
from src.utils import get_session


@pytest.fixture(name="banks_data")
def fixture_banks_data():
    """Exemplary banks data inserted into the database.

    The data includes following cases:
    - headquarter with branches (1 or many branches),
    - headquarter without branches,
    - branch without headquarter,
    - many banks from different countries,
    - many banks from the same country,
    - empty address field.

    Returns
    -------
    list[dict]
        List of dicts representing banks.
    """
    return [
        {
            "swift_code": "A1234567XXX",
            "name": "Alior Bank",
            "address": "Alior Bank Address",
            "is_headquarter": True,
            "country_iso2": "PL",
            "headquarter": None,
        },
        {
            "swift_code": "D1234567XXX",
            "name": "Deutsche Bank",
            "address": "Deutsche Bank Address",
            "is_headquarter": True,
            "country_iso2": "DE",
            "headquarter": None,
        },
        {
            "swift_code": "P1234567XXX",
            "name": "PKO Bank",
            "address": "PKO Bank Address",
            "is_headquarter": True,
            "country_iso2": "PL",
            "headquarter": None,
        },
        {
            "swift_code": "A0987654321",
            "name": "Alior Bank",
            "address": " ",
            "is_headquarter": False,
            "country_iso2": "PL",
            "headquarter": None,
        },
        {
            "swift_code": "A1234567890",
            "name": "Alior Bank",
            "address": "Alior Bank Address",
            "is_headquarter": False,
            "country_iso2": "PL",
            "headquarter": "A1234567XXX",
        },
        {
            "swift_code": "A1234567891",
            "name": "Alior Bank",
            "address": "Alior Bank Address",
            "is_headquarter": False,
            "country_iso2": "PL",
            "headquarter": "A1234567XXX",
        },
        {
            "swift_code": "C1234567890",
            "name": "Commerzbank",
            "address": "",
            "is_headquarter": False,
            "country_iso2": "DE",
            "headquarter": "C1234567XXX",
        },
        {
            "swift_code": "D1234567890",
            "name": "Deutsche Bank",
            "address": "Deutsche Bank Address",
            "is_headquarter": False,
            "country_iso2": "DE",
            "headquarter": "D1234567XXX",
        },
    ]


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
    return [{"iso2": "DE", "name": "GERMANY"}, {"iso2": "PL", "name": "POLAND"}]


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
                "POLAND",
                "POLAND",
                "POLAND",
                "POLAND",
                "GERMANY",
                "GERMANY",
                "POLAND",
                "GERMANY",
            ],
        }
    )


@pytest.fixture(name="expected_results_of_reading_banks")
def fixture_expected_results_of_reading_banks():
    """Expected results of reading exemplary banks data from the database."""
    return {
        "A1234567XXX": {
            "address": "Alior Bank Address",
            "bankName": "Alior Bank",
            "countryISO2": "PL",
            "countryName": "POLAND",
            "isHeadquarter": True,
            "swiftCode": "A1234567XXX",
            "branches": {
                "A1234567890": {
                    "address": "Alior Bank Address",
                    "bankName": "Alior Bank",
                    "countryISO2": "PL",
                    "isHeadquarter": False,
                    "swiftCode": "A1234567890",
                },
                "A1234567891": {
                    "address": "Alior Bank Address",
                    "bankName": "Alior Bank",
                    "countryISO2": "PL",
                    "isHeadquarter": False,
                    "swiftCode": "A1234567891",
                },
            },
            "branches_len": 2,
        },
        "D1234567XXX": {
            "address": "Deutsche Bank Address",
            "bankName": "Deutsche Bank",
            "countryISO2": "DE",
            "countryName": "GERMANY",
            "isHeadquarter": True,
            "swiftCode": "D1234567XXX",
            "branches": {
                "D1234567890": {
                    "address": "Deutsche Bank Address",
                    "bankName": "Deutsche Bank",
                    "countryISO2": "DE",
                    "isHeadquarter": False,
                    "swiftCode": "D1234567890",
                },
            },
            "branches_len": 1,
        },
        "P1234567XXX": {
            "address": "PKO Bank Address",
            "bankName": "PKO Bank",
            "countryISO2": "PL",
            "countryName": "POLAND",
            "isHeadquarter": True,
            "swiftCode": "P1234567XXX",
            "branches": {},
            "branches_len": 0,
        },
        "A0987654321": {
            "address": " ",
            "bankName": "Alior Bank",
            "countryISO2": "PL",
            "countryName": "POLAND",
            "isHeadquarter": False,
            "swiftCode": "A0987654321",
            "branches": None,
        },
        "A1234567890": {
            "address": "Alior Bank Address",
            "bankName": "Alior Bank",
            "countryISO2": "PL",
            "countryName": "POLAND",
            "isHeadquarter": False,
            "swiftCode": "A1234567890",
            "branches": None,
        },
        "A1234567891": {
            "address": "Alior Bank Address",
            "bankName": "Alior Bank",
            "countryISO2": "PL",
            "countryName": "POLAND",
            "isHeadquarter": False,
            "swiftCode": "A1234567891",
            "branches": None,
        },
        "C1234567890": {
            "address": "",
            "bankName": "Commerzbank",
            "countryISO2": "DE",
            "countryName": "GERMANY",
            "isHeadquarter": False,
            "swiftCode": "C1234567890",
            "branches": None,
        },
        "D1234567890": {
            "address": "Deutsche Bank Address",
            "bankName": "Deutsche Bank",
            "countryISO2": "DE",
            "countryName": "GERMANY",
            "isHeadquarter": False,
            "swiftCode": "D1234567890",
            "branches": None,
        },
    }


@pytest.fixture(name="expected_results_of_reading_countries")
def fixture_expected_results_of_reading_countries():
    """Expected results of reading exemplary countries data from the database."""
    return {
        "PL": {
            "countryISO2": "PL",
            "countryName": "POLAND",
            "swiftCodes": {
                "A1234567XXX": {
                    "address": "Alior Bank Address",
                    "bankName": "Alior Bank",
                    "countryISO2": "PL",
                    "isHeadquarter": True,
                    "swiftCode": "A1234567XXX",
                },
                "P1234567XXX": {
                    "address": "PKO Bank Address",
                    "bankName": "PKO Bank",
                    "countryISO2": "PL",
                    "isHeadquarter": True,
                    "swiftCode": "P1234567XXX",
                },
                "A0987654321": {
                    "address": " ",
                    "bankName": "Alior Bank",
                    "countryISO2": "PL",
                    "isHeadquarter": False,
                    "swiftCode": "A0987654321",
                },
                "A1234567890": {
                    "address": "Alior Bank Address",
                    "bankName": "Alior Bank",
                    "countryISO2": "PL",
                    "isHeadquarter": False,
                    "swiftCode": "A1234567890",
                },
                "A1234567891": {
                    "address": "Alior Bank Address",
                    "bankName": "Alior Bank",
                    "countryISO2": "PL",
                    "isHeadquarter": False,
                    "swiftCode": "A1234567891",
                },
            },
            "swift_codes_len": 5,
        },
        "DE": {
            "countryISO2": "DE",
            "countryName": "GERMANY",
            "swiftCodes": {
                "D1234567XXX": {
                    "address": "Deutsche Bank Address",
                    "bankName": "Deutsche Bank",
                    "countryISO2": "DE",
                    "isHeadquarter": True,
                    "swiftCode": "D1234567XXX",
                },
                "C1234567890": {
                    "address": "",
                    "bankName": "Commerzbank",
                    "countryISO2": "DE",
                    "isHeadquarter": False,
                    "swiftCode": "C1234567890",
                },
                "D1234567890": {
                    "address": "Deutsche Bank Address",
                    "bankName": "Deutsche Bank",
                    "countryISO2": "DE",
                    "isHeadquarter": False,
                    "swiftCode": "D1234567890",
                },
            },
            "swift_codes_len": 3,
        },
    }


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


@pytest.fixture(name="client")
def fixture_client(session: Session):
    """Creates new FastAPI client for in-memory database.

    Yields
    -------
    fastapi.TestClient
        Test client used with in-memory database.
    """

    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
