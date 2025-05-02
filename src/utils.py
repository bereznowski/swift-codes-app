"""This module gathers helper functions."""
from typing import Literal

from fastapi import HTTPException, status
from sqlmodel import Session, select

from .database import engine

from .models import (
    Bank,
    Country,
    SWIFT_CODE_LEN,
    ISO2_CODE_LEN,
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


def check_code_length(code: str, code_type=Literal["SWIFT", "ISO2"]):
    """Checks if the provided code has correct lenght (11 for SWIFT, 2 for country ISO2).

    Parameters
    ----------
    code : str
        Code to be checked
    code_type : str {"SWIFT", "ISO2"}
        Type of code to be checked.

    Raises
    ------
    HTTPException
        Unprocessable entity (422) if the code length is incorrect.
    """
    length = SWIFT_CODE_LEN
    length_condition = len(code) != SWIFT_CODE_LEN

    if code_type == "ISO2":
        length = ISO2_CODE_LEN
        length_condition = len(code) != ISO2_CODE_LEN

    if length_condition:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"{code_type} code should consist of {length} characters.",
        )


def check_if_upper(
    text: str, text_type=Literal["SWIFT code", "ISO2 code", "country name"]
):
    """Checks if the provided text is uppercase.

    Parameters
    ----------
    text : str
        text to be checked
    text_type : str {"SWIFT code", "ISO2 code", "country name"}
        Type of text to be checked.

    Raises
    ------
    HTTPException
        Unprocessable entity (422) if the text is not uppercase.
    """
    if not text.isupper():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"All characters in {text_type} should be uppercase.",
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
