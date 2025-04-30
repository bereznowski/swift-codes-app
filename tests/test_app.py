"""This module includes unit tests for functions from src/app.py"""

from sqlmodel import Session, select

from src.app import create_banks, create_countries
from src.models import Bank, Country

from .utils import (
    get_countries,
    query_created_relationship_banks_country,
    query_created_relationship_branches_headquarter,
)


def test_create_banks(
    session: Session,
    banks_data_after_excel: list[dict],
    countries_data_after_excel: list[dict],
):
    """Tests banks creation.

    Parameters
    ----------
    session : sqlmodel.Session
        SQLModel Session used to interact with in-memory database.
    banks_data_after_excel : list[dict]
        List of dicts used for creating table models of banks.
    countries_data_after_excel : list[dict]
        List of dicts used for creating table models of countries.
    """
    create_countries(session=session, countries_data=countries_data_after_excel)
    create_banks(session=session, banks_data=banks_data_after_excel)

    query_created_relationship_banks_country(session)
    query_created_relationship_branches_headquarter(session)

    assert (
        len(session.exec(select(Country)).all()) == 2
    ), "There should be 2 countries in the database"
    assert (
        len(session.exec(select(Bank)).all()) == 8
    ), "There should be 8 countries in the database"


def test_create_countries(session: Session, countries_data_after_excel: list[dict]):
    """Tests countries creation.

    Parameters
    ----------
    session : sqlmodel.Session
        SQLModel Session used to interact with in-memory database.
    countries_data_after_excel : list[dict]
        List of dicts used for creating table models of countries.
    """
    create_countries(session=session, countries_data=countries_data_after_excel)

    get_countries(session)  # checks if germany and poland are present exactly once
    assert (
        len(session.exec(select(Country)).all()) == 2
    ), "There should be 2 countries in the database"
