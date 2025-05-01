"""This module includes unit tests for functions from src/models.py"""

import pytest

from sqlmodel import select

from src.models import Bank, Country
from .utils import (
    query_created_relationship_branches_headquarter,
    query_created_relationship_banks_country,
)


@pytest.fixture(name="banks_data")
def fixture_banks_data():
    """Exemplary banks data inserted into database.

    The data includes following cases:
    - headquarter with branches (1 or 2 branches),
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


def test_relationship_branches_headquarter(session, banks_data):
    """Tests relationship between branches and headquarter.

    Parameters
    ----------
    session : sqlmodel.Session
        SQLModel Session used to interact with in-memory database.
    banks_data : list[dict]
        List of dicts used for creating table models of banks.
    """
    default_country = Country(
        iso2="00", name="Default"
    )  # country is required for Bank creation
    session.add(default_country)
    session.commit()

    for bank_data in banks_data:
        headquarter = session.exec(
            select(Bank).where(Bank.swift_code == bank_data["headquarter"])
        ).first()

        bank = Bank(
            swift_code=bank_data["swift_code"],
            name=bank_data["name"],
            address=bank_data["address"],
            is_headquarter=bank_data["is_headquarter"],
            country_id=default_country.id,
            headquarter_id=headquarter.id if headquarter is not None else None,
        )

        session.add(bank)
        session.commit()

    query_created_relationship_branches_headquarter(session)


def test_relationship_banks_country(session, banks_data, countries_data_after_excel):
    """Tests relationship between banks and country.

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

    query_created_relationship_banks_country(session)
