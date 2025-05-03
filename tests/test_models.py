"""This module includes unit tests for functions from src/models.py"""

from sqlmodel import select

from src.models import Bank, Country
from .utils import (
    insert_exemplary_datainto_db,
    query_created_relationship_branches_headquarter,
    query_created_relationship_banks_country,
)


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
    insert_exemplary_datainto_db(session, banks_data, countries_data_after_excel)
    query_created_relationship_banks_country(session)
