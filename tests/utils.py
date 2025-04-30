"""This module includes helper functions used by more than one module."""

from sqlmodel import select
from src.models import Bank, Country


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
