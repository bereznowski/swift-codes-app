"""This module includes helper functions used by more than one module."""

from typing import Callable, Literal

from sqlmodel import select
from starlette.responses import Response

from src.models import Bank, Country


def check_if_expected_banks_in_list(request_banks: list[dict], expected_banks: dict):
    """Checks if expected banks are on the list of headquarter's branches or country's banks.

    Parameters
    ----------
    request_banks : list[dict]
        List of banks returned as part of a get request.
    expected_banks : dict[str, dict[str, str | bool]]
        Dict showing expected values of expected banks
    """
    for _, expected_bank in expected_banks.items():
        banks = request_banks

        found_expected_bank = False

        for bank in banks:
            if bank["swiftCode"] == expected_bank["swiftCode"]:
                found_expected_bank = True

                keys = [
                    "address",
                    "bankName",
                    "countryISO2",
                    "isHeadquarter",
                    "swiftCode",
                ]

                for key in keys:
                    assert bank[key] == expected_bank[key], f"Bank {key} is different"
                break

        assert found_expected_bank, "Did not found all expected banks"


def check_bank_data_correctness(request_result: dict, expected_result: dict):
    """Checks correctness of bank data received via request.

    Parameters
    ----------
    request_result : dict
        Dict showing banks values received from request.
    expected_result : dict[str, dict[str, str | bool]]
        Dict showing expected values for banks.
    """
    for key in [
        "address",
        "bankName",
        "countryISO2",
        "countryName",
        "isHeadquarter",
        "swiftCode",
    ]:
        assert request_result[key] == expected_result[key], f"{key} is different"

    if not expected_result["isHeadquarter"]:
        assert request_result.get("branches") is expected_result.get(
            "branches"
        ), "No branches were expected"
    else:
        assert (
            len(request_result["branches"]) == expected_result["branches_len"]
        ), "Different number of branches expected"

        check_if_expected_banks_in_list(
            request_banks=request_result["branches"],
            expected_banks=expected_result["branches"],
        )


def check_country_data_correctness(request_result: dict, expected_result: dict):
    """Checks correctness of country data received via request.

    Parameters
    ----------
    request_result : dict
        Dict showing countries values received from request.
    expected_result : dict[str, dict[str, str | bool]]
        Dict showing expected values for countries.
    """
    keys = ["countryISO2", "countryName"]

    for key in keys:
        assert request_result[key] == expected_result[key], f"{key} codes are different"

    check_if_expected_banks_in_list(
        request_banks=request_result["swiftCodes"],
        expected_banks=expected_result["swiftCodes"],
    )


def get_banks(session):
    """Gets bank objects from the database.

    Parameters
    ----------
    session : sqlmodel.Session
        SQLModel Session used to interact with in-memory database.
    """
    deutsche_bank1 = session.exec(
        select(Bank).where(Bank.swift_code == "D1234567890")
    ).one()
    deutsche_bank2 = session.exec(
        select(Bank).where(Bank.swift_code == "D1234567XXX")
    ).one()
    commerzbank = session.exec(
        select(Bank).where(Bank.swift_code == "C1234567890")
    ).one()
    alior_bank1 = session.exec(
        select(Bank).where(Bank.swift_code == "A1234567890")
    ).one()
    alior_bank2 = session.exec(
        select(Bank).where(Bank.swift_code == "A1234567XXX")
    ).one()
    alior_bank3 = session.exec(
        select(Bank).where(Bank.swift_code == "A0987654321")
    ).one()
    alior_bank4 = session.exec(
        select(Bank).where(Bank.swift_code == "A1234567891")
    ).one()
    pko_bank = session.exec(select(Bank).where(Bank.swift_code == "P1234567XXX")).one()

    return (
        deutsche_bank1,
        deutsche_bank2,
        commerzbank,
        alior_bank1,
        alior_bank2,
        alior_bank3,
        alior_bank4,
        pko_bank,
    )


def get_countries(session):
    """Gets country objects from the database.

    Parameters
    ----------
    session : sqlmodel.Session
        SQLModel Session used to interact with in-memory database.
    """
    germany = session.exec(select(Country).where(Country.iso2 == "DE")).one()
    poland = session.exec(select(Country).where(Country.iso2 == "PL")).one()

    return (germany, poland)


def insert_exemplary_data_into_db(session, banks_data, countries_data_after_excel):
    """Inserts exemplary data into the database.

    Parameters
    ----------
    session : sqlmodel.Session
        SQLModel Session used to interact with in-memory database.
    banks_data : list[dict]
        List of dicts used for creating table models of banks.
    countries_data_after_excel : list[dict]
        List of dicts used for creating table models of countries.
    """
    for country_data in countries_data_after_excel:
        country = Country(iso2=country_data["iso2"], name=country_data["name"])
        session.add(country)
        session.commit()

    for bank_data in banks_data:
        country = session.exec(
            select(Country).where(Country.iso2 == bank_data["country_iso2"])
        ).first()
        headquarter = session.exec(
            select(Bank).where(Bank.swift_code == bank_data["headquarter"])
        ).first()

        bank = Bank(
            swift_code=bank_data["swift_code"],
            name=bank_data["name"],
            address=bank_data["address"],
            is_headquarter=bank_data["is_headquarter"],
            country_id=country.id if country is not None else None,
            headquarter_id=headquarter.id if headquarter is not None else None,
        )

        session.add(bank)
        session.commit()


def diff_between_codes(code_type: Literal["SWIFT", "ISO2"]):
    """Helper function for differentiating between SWIFT and ISO2 codes.

    Parameters
    ----------
    code_type : str {"SWIFT", "ISO2"}
        Type of the code.

    Returns
    ----------
    info_incorrect_len: string
        Expected error message for code of incorrect length.
    info_incorrect_upper : string
        Expected error message for code of incorrect uppercase.
    info_special_characters : string
        Expected error message for code with special characters.
    """
    code_len = 11 if code_type == "SWIFT" else 2
    type_of_characters = "alphanumeric" if code_type == "SWIFT" else "letters"

    info_incorrect_len = f"{code_type} code should consist of {code_len} characters."
    info_incorrect_upper = f"All characters in {code_type} code should be uppercase."
    info_special_characters = (
        f"All characters in {code_type} code should be {type_of_characters}."
    )

    return info_incorrect_len, info_incorrect_upper, info_special_characters


def send_request_with_incorrect_code(
    code_type: Literal["SWIFT", "ISO2"],
    request_path: str,
    client_request: Callable[..., Response],
):
    """Sends requests with incorrect SWIFT/ISO2 codes.

    Parameters
    ----------
    code_type : str {"SWIFT", "ISO2"}
        Type of code to be checked.
    request_path : str
        Path for which the request is send.
    client_request : Callable
        Request send by FastAPI client.
    """
    info_incorrect_len, info_incorrect_upper, info_special_characters = (
        diff_between_codes(code_type)
    )

    wrong_codes = [  # SWIFT
        {"SWIFT": "wrongswiftcode", "message": info_incorrect_len},
        {"SWIFT": "WRONGSWIFTCODE", "message": info_incorrect_len},
        {"SWIFT": "fafaniifjkk", "message": info_incorrect_upper},
        {"SWIFT": "FNDKOSHEIk1", "message": info_incorrect_upper},
        {"SWIFT": "!@#$%^&*()P", "message": info_special_characters},
        {"SWIFT": "%NDKOSHEXXX", "message": info_special_characters},
    ]

    if code_type == "ISO2":
        wrong_codes = [
            {"ISO2": "wrongcode", "message": info_incorrect_len},
            {"ISO2": "WRONGCODE", "message": info_incorrect_len},
            {"ISO2": "fd", "message": info_incorrect_upper},
            {"ISO2": "ff", "message": info_incorrect_upper},
            {"ISO2": "!@", "message": info_special_characters},
            {"ISO2": "%N", "message": info_special_characters},
        ]

    for example in wrong_codes:
        request = client_request(request_path + example[code_type])
        data = request.json()

        assert data["detail"] == example["message"], "Response is incorrect."


def send_request_with_nonexisting_code(
    code_type: Literal["SWIFT", "ISO2"],
    request_path: str,
    client_request: Callable[..., Response],
):
    """Sends requests with nonexisting SWIFT/ISO2 codes.

    Parameters
    ----------
    code_type : str {"SWIFT", "ISO2"}
        Type of code to be checked.
    request_path : str
        Path for which the request is send.
    client_request : Callable
        Request send by FastAPI client.
    """
    nonexisting_codes = (
        ["WRONGSWIFT1", "WRONGSWIXXX"] if code_type == "SWIFT" else ["QW", "WR"]
    )

    for example in nonexisting_codes:
        request = client_request(request_path + example)
        data = request.json()

        assert data["detail"] == "Item does not exist.", "Response is incorrect."


def query_created_relationship_branches_headquarter(session):
    """Evaluates correctness of branches-headquarter relationship.

    Parameters
    ----------
    session : sqlmodel.Session
        SQLModel Session used to interact with in-memory database.
    """
    (
        deutsche_bank1,
        deutsche_bank2,
        commerzbank,
        alior_bank1,
        alior_bank2,
        alior_bank3,
        alior_bank4,
        pko_bank,
    ) = get_banks(session)

    banks_branches_and_headquarter = [
        {"bank": deutsche_bank1, "branches": [], "headquarter": deutsche_bank2},
        {"bank": deutsche_bank2, "branches": [deutsche_bank1], "headquarter": None},
        {"bank": commerzbank, "branches": [], "headquarter": None},
        {"bank": alior_bank1, "branches": [], "headquarter": alior_bank2},
        {
            "bank": alior_bank2,
            "branches": [alior_bank1, alior_bank4],
            "headquarter": None,
        },
        {"bank": alior_bank3, "branches": [], "headquarter": None},
        {"bank": alior_bank4, "branches": [], "headquarter": alior_bank2},
        {"bank": pko_bank, "branches": [], "headquarter": None},
    ]

    for bank_bh in banks_branches_and_headquarter:
        assert len(bank_bh["bank"].branches) == len(
            bank_bh["branches"]
        ), f"{bank_bh['bank'].swift_code} should have {len(bank_bh['branches'])} branches."
        assert bank_bh["bank"].headquarter == bank_bh["headquarter"], (
            f"{bank_bh['headquarter'].swift_code} should be "
            f"a headquarter of {len(bank_bh['bank'].swift_code)}"
        )
        for branch in bank_bh["branches"]:
            assert (
                branch in bank_bh["bank"].branches
            ), f"{branch.swift_code} should be a branch of {bank_bh['bank'].swift_code}"


def query_created_relationship_banks_country(session):
    """Evaluates correctness of banks-country relationship.

    Parameters
    ----------
    session : sqlmodel.Session
        SQLModel Session used to interact with in-memory database.
    """
    germany, poland = get_countries(session)

    (
        deutsche_bank1,
        deutsche_bank2,
        commerzbank,
        alior_bank1,
        alior_bank2,
        alior_bank3,
        alior_bank4,
        pko_bank,
    ) = get_banks(session)

    bank_country_pairs = [
        {"bank": deutsche_bank1, "country": germany},
        {"bank": deutsche_bank1, "country": germany},
        {"bank": deutsche_bank2, "country": germany},
        {"bank": commerzbank, "country": germany},
        {"bank": alior_bank1, "country": poland},
        {"bank": alior_bank2, "country": poland},
        {"bank": alior_bank3, "country": poland},
        {"bank": alior_bank4, "country": poland},
        {"bank": pko_bank, "country": poland},
    ]

    for bc_pair in bank_country_pairs:
        assert (
            bc_pair["bank"] in bc_pair["country"].banks
        ), f"{bc_pair['bank'].swift_code} not in {bc_pair['country'].name} banks."
        assert (
            bc_pair["bank"].country == bc_pair["country"]
        ), f"{bc_pair['bank'].swift_code} country is not {bc_pair['country'].name}."
        assert (
            bc_pair["bank"].country_id == bc_pair["country"].id
        ), f"{bc_pair['bank'].swift_code} does not refer to {bc_pair['country'].name} ID."
