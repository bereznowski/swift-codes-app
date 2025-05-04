"""This module includes integration test for the whole project."""

from io import BytesIO

import pytest
import pandas as pd

from fastapi import status

from unit.utils import check_bank_data_correctness, check_country_data_correctness

from src.data_processing import extract_banks_data, extract_countries_data
from src.utils import create_banks, create_countries


@pytest.fixture(name="expected_results_of_reading_banks_after_post")
def fixture_expected_results_of_reading_banks_after_post():
    """Expected results of reading banks data from the database after post."""
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
            "branches": {
                "P1234567890": {
                    "address": "PKO Bank Address",
                    "bankName": "PKO Bank",
                    "countryISO2": "PL",
                    "isHeadquarter": False,
                    "swiftCode": "P1234567890",
                },
            },
            "branches_len": 1,
        },
        "C1234567XXX": {
            "address": "Commerzbank address",
            "bankName": "Commerzbank",
            "countryISO2": "DE",
            "countryName": "GERMANY",
            "isHeadquarter": True,
            "swiftCode": "C1234567XXX",
            "branches": {
                "C1234567890": {
                    "address": "",
                    "bankName": "Commerzbank",
                    "countryISO2": "DE",
                    "isHeadquarter": False,
                    "swiftCode": "C1234567890",
                },
            },
            "branches_len": 1,
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


@pytest.fixture(name="expected_results_of_reading_countries_after_post")
def fixture_expected_results_of_reading_countries_after_post():
    """Expected results of reading countries data from the database after post."""
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
                "P1234567890": {
                    "address": "PKO Bank Address",
                    "bankName": "PKO Bank",
                    "countryISO2": "PL",
                    "isHeadquarter": False,
                    "swiftCode": "P1234567890",
                },
            },
            "swift_codes_len": 6,
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
                "C1234567XXX": {
                    "address": "Commerzbank address",
                    "bankName": "Commerzbank",
                    "countryISO2": "DE",
                    "isHeadquarter": True,
                    "swiftCode": "C1234567XXX",
                },
            },
            "swift_codes_len": 4,
        },
    }


def test_swift_codes_app(
    mock_df,
    session,
    client,
    countries_data_after_excel,
    expected_results_of_reading_banks_after_post,
    expected_results_of_reading_countries_after_post,
    expected_results_of_reading_banks,
    expected_results_of_reading_countries,
):
    """Tests the whole flow of the application from loading.

    mock_df : pandas.DataFrame
        The data used in mock Excel file.
    session : sqlmodel.Session
        SQLModel Session used to interact with in-memory database.
    fastapi.TestClient
        Test client used with in-memory database.
    countries_data_after_excel : list[dict]
        List of dicts representing countries data.
    expected_results_of_reading_banks_after_post : dict{dict}
        Dict of dicts presenting expected banks data of retrieving
        banks data after POST operation.
    expected_results_of_reading_countries_after_post : dict{dict}
        Dict of dicts presenting expected countries data of retrieving
        banks data after POST operation.
    expected_results_of_reading_banks : dict{dict}
        Dict of dicts presenting expected banks data of retrieving
        banks data after DELETE operation.
    expected_results_of_reading_countries : dict{dict}
        Dict of dicts presenting expected countries data of retrieving
        banks data after DELETE operation.
    """
    output = BytesIO()

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        mock_df.to_excel(writer, sheet_name="Sheet1", index=False)

    banks_data = extract_banks_data(output)
    countries_data = extract_countries_data(output)

    create_countries(session=session, countries_data=countries_data)
    create_banks(session=session, banks_data=banks_data)

    commerzbank_hq = {
        "address": "Commerzbank address",
        "bankName": "Commerzbank",
        "countryISO2": "DE",
        "countryName": "GERMANY",
        "isHeadquarter": True,
        "swiftCode": "C1234567XXX",
    }
    pko_bank_branch = {
        "address": "PKO Bank Address",
        "bankName": "PKO Bank",
        "countryISO2": "PL",
        "countryName": "POLAND",
        "isHeadquarter": False,
        "swiftCode": "P1234567890",
    }

    response = client.post(
        "/v1/swift-codes",
        json=commerzbank_hq,
    )
    assert response.status_code == status.HTTP_200_OK

    response = client.post(
        "/v1/swift-codes",
        json=pko_bank_branch,
    )
    assert response.status_code == status.HTTP_200_OK

    for bank in banks_data:
        swift_code = bank["swift_code"]
        expected_result = expected_results_of_reading_banks_after_post[swift_code]

        response = client.get(f"/v1/swift-codes/{swift_code}")
        data = response.json()

        assert response.status_code == status.HTTP_200_OK

        check_bank_data_correctness(
            request_result=data, expected_result=expected_result
        )

    for country in countries_data_after_excel:
        iso2_code = country["iso2"]
        expected_result = expected_results_of_reading_countries_after_post[iso2_code]

        response = client.get(f"/v1/swift-codes/country/{iso2_code}")
        data = response.json()

        assert response.status_code == status.HTTP_200_OK

        check_country_data_correctness(
            request_result=data, expected_result=expected_result
        )

    response = client.delete(f"/v1/swift-codes/{commerzbank_hq['swiftCode']}")
    assert response.status_code == status.HTTP_200_OK

    response = client.delete(f"/v1/swift-codes/{pko_bank_branch['swiftCode']}")
    assert response.status_code == status.HTTP_200_OK

    for bank in banks_data:
        swift_code = bank["swift_code"]
        expected_result = expected_results_of_reading_banks[swift_code]

        response = client.get(f"/v1/swift-codes/{swift_code}")
        data = response.json()

        assert response.status_code == status.HTTP_200_OK

        check_bank_data_correctness(
            request_result=data, expected_result=expected_result
        )

    for country in countries_data_after_excel:
        iso2_code = country["iso2"]
        expected_result = expected_results_of_reading_countries[iso2_code]

        response = client.get(f"/v1/swift-codes/country/{iso2_code}")
        data = response.json()

        assert response.status_code == status.HTTP_200_OK

        check_country_data_correctness(
            request_result=data, expected_result=expected_result
        )

    assert (
        client.get(f"/v1/swift-codes/{commerzbank_hq['swiftCode']}").json()["detail"]
        == "Item does not exist."
    ), "Response is incorrect."

    assert (
        client.get(f"/v1/swift-codes/{pko_bank_branch['swiftCode']}").json()["detail"]
        == "Item does not exist."
    ), "Response is incorrect."
