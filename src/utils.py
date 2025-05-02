from fastapi import HTTPException, status
from sqlmodel import Session, select

from .database import engine

from .models import (
    Bank,
    Country,
    SWIFT_CODE_LEN,
    ISO2_LEN,
)


def get_session():
    """Gets new session."""
    with Session(engine) as session:
        yield session


def create_banks(*, session: Session, banks_data: list[dict]):
    """Adds banks data to database.

    Parameters
    ----------
    session : sqlmodel.Session
        SQLModel Session used to interact with the database.
    banks_data : list[dict]
        Dictionaries of values to be used during banks' table model creation.
        Structure of the dictionaries:
            {
                "country_iso2": str,
                "swift_code": str,
                "name": str,
                "address": str,
                "is_headquarter": bool,
                "potential_hq": str
            }
    """
    for bank in banks_data:
        country = session.exec(
            select(Country).where(Country.iso2 == bank["country_iso2"])
        ).first()
        headquarter = session.exec(
            select(Bank).where(Bank.swift_code == bank["potential_hq"])
        ).first()

        session.add(
            Bank(
                swift_code=bank["swift_code"],
                name=bank["name"],
                address=bank["address"],
                is_headquarter=bank["is_headquarter"],
                country=country,
                headquarter=headquarter,
            )
        )

        session.commit()


def create_countries(*, session: Session, countries_data: list[dict]):
    """Adds countries data to database.

    Parameters
    ----------
    session : sqlmodel.Session
        SQLModel Session used to interact with the database.
    countries_data : list[dict]
        Dictionaries of values to be used during countries' table model creation.
            Structure of the dictionaries:
            {
                "iso2": str,
                "name": str
            }
    """
    for country in countries_data:
        session.add(Country(iso2=country["iso2"], name=country["name"]))
    session.commit()


def check_swift_code_correctness(swift_code: str):
    """Checks if the provided string has 11 uppercase characters.

    Parameters
    ----------
    swift_code : str
        String to be checked for correctness.

    Raises
    ------
    HTTPException
        Unprocessable entity (422) if the string is incorrect.
    """
    if len(swift_code) != SWIFT_CODE_LEN:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"SWIFT code should consist of {SWIFT_CODE_LEN} characters.",
        )

    if not swift_code.isupper():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="All characters in SWIFT code should be uppercase.",
        )


def check_country_iso2_code_correctness(country_iso2_code: str):
    """Checks if the provided string has 2 uppercase characters.

    Parameters
    ----------
    country_iso2_code : str
        String to be checked for correctness.

    Raises
    ------
    HTTPException
        Unprocessable entity (422) if the string is incorrect.
    """
    if len(country_iso2_code) != ISO2_LEN:  # TODO: simplify exception handling
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"ISO2 code should consist of {ISO2_LEN} characters.",
        )

    if not country_iso2_code.isupper():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="All characters in ISO2 code should be uppercase.",
        )


def check_country_name_correctness(country_name: str):
    """Checks if the provided string is uppercase.

    Parameters
    ----------
    country_name : str
        String to be checked for correctness.

    Raises
    ------
    HTTPException
        Unprocessable entity (422) if the string is not uppercase.
    """
    if not country_name.isupper():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="All characters in country name should be uppercase.",
        )


def check_if_exists_in_db(obj: Bank | Country):
    """Checks if the given object exists.

    Parameters
    ----------
    obj : Bank | Country
        Bank or Country object to be checked.

    Raises
    ------
    HTTPException
        Not found (404) if the object does not exist.
    """
    if not obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item does not exist.",
        )
