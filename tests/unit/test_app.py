"""This module includes unit tests for functions from src/app.py"""

import pytest

from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from src.app import app
from src.utils import get_session


from .utils import (
    check_bank_data_correctness,
    check_country_data_correctness,
    diff_between_codes,
    get_banks,
    get_countries,
    insert_exemplary_data_into_db,
    send_request_with_incorrect_code,
)


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


def test_read_bank_correct_data(
    session: Session,
    client: TestClient,
    banks_data,
    countries_data_after_excel,
    expected_results_of_reading_banks,
):
    """Tests if information about banks is properly retrived.

    Parameters
    ----------
    session : sqlmodel.Session
        SQLModel Session used to interact with in-memory database.
    fastapi.TestClient
        Test client used with in-memory database.
    banks_data : list[dict]
        List of dicts used for creating table models of banks.
    countries_data_after_excel : list[dict]
        List of dicts used for creating table models of countries.
    expected_results_of_reading_banks : dict{dict}
        Dict of dicts presenting expected results of retrieving banks data.
    """
    insert_exemplary_data_into_db(session, banks_data, countries_data_after_excel)

    for bank in banks_data:
        swift_code = bank["swift_code"]
        expected_result = expected_results_of_reading_banks[swift_code]

        response = client.get(f"/v1/swift-codes/{swift_code}")
        data = response.json()

        assert response.status_code == status.HTTP_200_OK

        check_bank_data_correctness(
            request_result=data, expected_result=expected_result
        )


def test_read_bank_incorrect_swift_codes(
    client: TestClient,
):
    """Tests if incorrect SWIFT code results in correct response.

    Parameters
    ----------
    fastapi.TestClient
        Test client used with in-memory database.
    """
    send_request_with_incorrect_code(
        code_type="SWIFT", request_path="/v1/swift-codes/", client_request=client.get
    )


def test_read_bank_not_found(
    client: TestClient,
):
    """Tests if SWIFT code not in database results in correct response.

    Parameters
    ----------
    fastapi.TestClient
        Test client used with in-memory database.
    """
    send_request_with_incorrect_code(
        code_type="SWIFT", request_path="/v1/swift-codes/", client_request=client.get
    )


def test_read_country_correct_data(
    session: Session,
    client: TestClient,
    banks_data,
    countries_data_after_excel,
    expected_results_of_reading_countries,
):
    """Tests if information about countries is properly retrived.

    Parameters
    ----------
    session : sqlmodel.Session
        SQLModel Session used to interact with in-memory database.
    fastapi.TestClient
        Test client used with in-memory database.
    banks_data : list[dict]
        List of dicts used for creating table models of banks.
    countries_data_after_excel : list[dict]
        List of dicts used for creating table models of countries.
    expected_results_of_reading_countries : dict{dict}
        Dict of dicts presenting expected results of retrieving countries data.
    """
    insert_exemplary_data_into_db(session, banks_data, countries_data_after_excel)

    for country in countries_data_after_excel:
        iso2_code = country["iso2"]
        expected_result = expected_results_of_reading_countries[iso2_code]

        response = client.get(f"/v1/swift-codes/country/{iso2_code}")
        data = response.json()

        assert response.status_code == status.HTTP_200_OK

        check_country_data_correctness(
            request_result=data, expected_result=expected_result
        )


def test_read_country_incorrect_iso2_codes(
    client: TestClient,
):
    """Tests if incorrect ISO2 code results in correct response.

    Parameters
    ----------
    fastapi.TestClient
        Test client used with in-memory database.
    """
    send_request_with_incorrect_code(
        code_type="ISO2",
        request_path="/v1/swift-codes/country/",
        client_request=client.get,
    )


def test_read_country_not_found(
    client: TestClient,
):
    """Tests if ISO2 code not in database results in correct response.

    Parameters
    ----------
    fastapi.TestClient
        Test client used with in-memory database.
    """
    send_request_with_incorrect_code(
        code_type="ISO2",
        request_path="/v1/swift-codes/country/",
        client_request=client.get,
    )


def test_create_bank_correct_data(
    client: TestClient,
    banks_data,
    expected_results_of_reading_banks,
    expected_results_of_reading_countries,
):
    """Tests if banks and countries are properly created via POST request.

    Parameters
    ----------
    fastapi.TestClient
        Test client used with in-memory database.
    banks_data : list[dict]
        List of dicts used for creating table models of banks.
    expected_results_of_reading_banks : dict{dict}
        Dict of dicts presenting expected results of retrieving banks data.
    expected_results_of_reading_countries : dict{dict}
        Dict of dicts presenting expected results of retrieving countries data.
    """
    for bank in banks_data:
        response = client.post(
            "/v1/swift-codes",
            json={
                "address": bank["address"],
                "bankName": bank["name"],
                "countryISO2": bank["country_iso2"],
                "countryName": "GERMANY" if bank["country_iso2"] == "DE" else "POLAND",
                "isHeadquarter": bank["is_headquarter"],
                "swiftCode": bank["swift_code"],
            },
        )
        data = response.json()
        assert (
            data["message"]
            == f"SWIFT CODE = {bank['swift_code']} successfully created."
        ), "Response is incorrect."
        assert response.status_code == status.HTTP_200_OK

    for _, expected_result in expected_results_of_reading_banks.items():
        response = client.get(f"/v1/swift-codes/{expected_result['swiftCode']}")
        data = response.json()

        assert response.status_code == status.HTTP_200_OK

        check_bank_data_correctness(
            request_result=data, expected_result=expected_result
        )

    for iso2_code, expected_result in expected_results_of_reading_countries.items():
        response = client.get(f"/v1/swift-codes/country/{iso2_code}")
        data = response.json()

        assert response.status_code == status.HTTP_200_OK

        check_country_data_correctness(
            request_result=data, expected_result=expected_result
        )


def test_create_bank_incorrect_bank_data(client: TestClient):
    """Tests if correct responses are provided for incorrect data during bank creation.

    Parameters
    ----------
    fastapi.TestClient
        Test client used with in-memory database.
    """
    (
        _,
        iso2_info_incorrect_upper,
        iso2_info_special_characters,
    ) = diff_between_codes("ISO2")

    (
        _,
        swift_info_incorrect_upper,
        swift_info_special_characters,
    ) = diff_between_codes("SWIFT")

    

    incorrect_requests = [
        {
            "bank_data": {
                "address": "valid address",
                "bankName": "valid bank name",
                "countryISO2": "P#",
                "countryName": "POLAND",
                "isHeadquarter": False,
                "swiftCode": "SWIFTCODEEE",
            },
            "message": iso2_info_special_characters,
        },
        {
            "bank_data": {
                "address": "valid address",
                "bankName": "valid bank name",
                "countryISO2": "pl",
                "countryName": "POLAND",
                "isHeadquarter": False,
                "swiftCode": "SWIFTCODEEE",
            },
            "message": iso2_info_incorrect_upper,
        },
        {
            "bank_data": {
                "address": "valid address",
                "bankName": "valid bank name",
                "countryISO2": "PL",
                "countryName": "POLAND",
                "isHeadquarter": False,
                "swiftCode": "SWIFTCODE!@",
            },
            "message": swift_info_special_characters,
        },
        {
            "bank_data": {
                "address": "valid address",
                "bankName": "valid bank name",
                "countryISO2": "PL",
                "countryName": "POLAND",
                "isHeadquarter": False,
                "swiftCode": "SWIFTCODeee",
            },
            "message": swift_info_incorrect_upper,
        },
        {
            "bank_data": {
                "address": "valid address",
                "bankName": "valid bank name",
                "countryISO2": "PL",
                "countryName": "Poland",
                "isHeadquarter": False,
                "swiftCode": "SWIFTCODEEE",
            },
            "message": "All characters in country name should be uppercase.",
        },
        {
            "bank_data": {
                "address": "valid address",
                "bankName": "valid bank name",
                "countryISO2": "PL",
                "countryName": "POLAND",
                "isHeadquarter": False,
                "swiftCode": "SWIFTCODXXX",
            },
            "message": "Headquarter's SWIFT codes must end with XXX and branches' cannot and with XXX.",
        },
        {
            "bank_data": {
                "address": "valid address",
                "bankName": "valid bank name",
                "countryISO2": "PL",
                "countryName": "POLAND",
                "isHeadquarter": True,
                "swiftCode": "SWIFTCODEEE",
            },
            "message": "Headquarter's SWIFT codes must end with XXX and branches' cannot and with XXX.",
        },

    ]

    for incorrect_request in incorrect_requests:
        response = client.post(
                "/v1/swift-codes",
                json=incorrect_request["bank_data"],
            )
        data = response.json()

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert data["detail"] == incorrect_request["message"]

def test_create_bank_incorrect_contry_name(client: TestClient):
    """Tests if correct response is provided for incorrect country name during bank creation.

    Parameters
    ----------
    fastapi.TestClient
        Test client used with in-memory database.
    """
    request1 = {
                "address": "valid address",
                "bankName": "valid bank name",
                "countryISO2": "PL",
                "countryName": "POLAND",
                "isHeadquarter": False,
                "swiftCode": "SWIFTCODEE1",
            }
    request2 = {
                "address": "valid address",
                "bankName": "valid bank name",
                "countryISO2": "PL",
                "countryName": "POLANDD",
                "isHeadquarter": False,
                "swiftCode": "SWIFTCODEE2",
            }


    client.post("/v1/swift-codes", json=request1)
    response = client.post("/v1/swift-codes", json=request2)
    assert response.status_code == status.HTTP_409_CONFLICT, "Request should end with conflig (409)"
    assert response.json()["detail"] == "In the database the correct countryName for countryISO2 = PL is POLAND.", "Detail should be different"

def test_create_bank_unique_constraint_failed(client: TestClient):
    """Tests if correct response is provided for unique constraint failed during bank creation.

    Parameters
    ----------
    fastapi.TestClient
        Test client used with in-memory database.
    """
    request1 = {
                "address": "valid address",
                "bankName": "valid bank name",
                "countryISO2": "PL",
                "countryName": "POLAND",
                "isHeadquarter": False,
                "swiftCode": "SWIFTCODEEE",
            }
    request2 = {
                "address": "valid address",
                "bankName": "valid bank name",
                "countryISO2": "PL",
                "countryName": "POLAND",
                "isHeadquarter": False,
                "swiftCode": "SWIFTCODEEE",
            }


    client.post("/v1/swift-codes", json=request1)
    response = client.post("/v1/swift-codes", json=request2)
    assert response.status_code == status.HTTP_409_CONFLICT, "Request should end with conflig (409)"
    assert response.json()["detail"] == "UNIQUE constraint failed: bank.swift_code", "Detail should be different"

# TODO: create integration test from Excel to get, post, delete


def test_delete_bank_correct_data(
    session: Session, client: TestClient, banks_data, countries_data_after_excel
):
    """Tests if information about banks is properly deleted.

    Parameters
    ----------
    session : sqlmodel.Session
        SQLModel Session used to interact with in-memory database.
    fastapi.TestClient
        Test client used with in-memory database.
    banks_data : list[dict]
        List of dicts used for creating table models of banks.
    countries_data_after_excel : list[dict]
        List of dicts used for creating table models of countries.
    """
    insert_exemplary_data_into_db(session, banks_data, countries_data_after_excel)

    (
        deutsche_bank_branch,
        deutsche_bank_hq,
        commerzbank,
        alior_bank_branch1,
        alior_bank_hq,
        alior_bank_branch2,
        alior_bank_branch3,
        pko_bank,
    ) = get_banks(session)

    germany, poland = get_countries(session)

    swift_code_to_be_deleted1 = deutsche_bank_branch.swift_code
    swift_code_to_be_deleted2 = alior_bank_hq.swift_code

    response = client.delete(f"/v1/swift-codes/{swift_code_to_be_deleted1}")
    data = response.json()
    assert (
        data["message"]
        == f"SWIFT CODE = {swift_code_to_be_deleted1} successfully deleted."
    ), "Response is incorrect."
    assert response.status_code == status.HTTP_200_OK

    response = client.delete(f"/v1/swift-codes/{swift_code_to_be_deleted2}")
    data = response.json()
    assert (
        data["message"]
        == f"SWIFT CODE = {swift_code_to_be_deleted2} successfully deleted."
    ), "Response is incorrect."
    assert response.status_code == status.HTTP_200_OK

    assert (
        client.get(f"/v1/swift-codes/{swift_code_to_be_deleted1}").json()["detail"]
        == "Item does not exist."
    ), "Response is incorrect."
    assert (
        client.get(f"/v1/swift-codes/{swift_code_to_be_deleted2}").json()["detail"]
        == "Item does not exist."
    ), "Response is incorrect."

    session.refresh(deutsche_bank_hq)
    assert (
        len(deutsche_bank_hq.branches) == 0
    ), "Deutsche Bank should not have any branches"
    assert (
        len(
            client.get(f"/v1/swift-codes/{deutsche_bank_hq.swift_code}").json()[
                "branches"
            ]
        )
        == 0
    ), "Deutsche Bank should not have any branches"

    session.refresh(alior_bank_branch1)
    session.refresh(alior_bank_branch2)
    session.refresh(alior_bank_branch3)
    assert (
        alior_bank_branch1.headquarter is None
    ), "Alior Bank should not have a headquarter"
    assert (
        alior_bank_branch2.headquarter is None
    ), "Alior Bank should not have a headquarter"
    assert (
        alior_bank_branch3.headquarter is None
    ), "Alior Bank should not have a headquarter"

    session.refresh(germany)
    session.refresh(poland)

    assert len(germany.banks) == 2, "Germany should have 2 banks"
    assert len(poland.banks) == 4, "Poland should have 4 banks"

    assert (
        len(client.get(f"/v1/swift-codes/country/{germany.iso2}").json()["swiftCodes"])
        == 2
    ), "Germany should have 2 banks"
    assert (
        len(client.get(f"/v1/swift-codes/country/{poland.iso2}").json()["swiftCodes"])
        == 4
    ), "Poland should have 2 banks"

    germany_banks = client.get(f"/v1/swift-codes/country/{germany.iso2}").json()[
        "swiftCodes"
    ]
    poland_banks = client.get(f"/v1/swift-codes/country/{poland.iso2}").json()[
        "swiftCodes"
    ]

    for bank in germany_banks:
        assert (
            bank["swiftCode"] != swift_code_to_be_deleted1
        ), "This bank should not exist"

    for bank in poland_banks:
        assert (
            bank["swiftCode"] != swift_code_to_be_deleted2
        ), "This bank should not exist"

    for bank in [
        deutsche_bank_hq,
        commerzbank,
        alior_bank_branch1,
        alior_bank_branch2,
        alior_bank_branch3,
        pko_bank,
    ]:
        assert (
            client.get(f"/v1/swift-codes/{deutsche_bank_hq.swift_code}").status_code
            == status.HTTP_200_OK
        ), "This bank should exist"


def test_delete_bank_incorrect_swift_codes(
    client: TestClient,
):
    """Tests if incorrect SWIFT code results in correct response.

    Parameters
    ----------
    fastapi.TestClient
        Test client used with in-memory database.
    """
    send_request_with_incorrect_code(
        code_type="SWIFT", request_path="/v1/swift-codes/", client_request=client.delete
    )


def test_delete_bank_not_found(
    client: TestClient,
):
    """Tests if SWIFT code not in database results in correct response.

    Parameters
    ----------
    fastapi.TestClient
        Test client used with in-memory database.
    """
    send_request_with_incorrect_code(
        code_type="SWIFT", request_path="/v1/swift-codes/", client_request=client.delete
    )
