"""This module is responsible for connecting all parts of the app."""

from contextlib import asynccontextmanager
from typing import Union

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from sqlmodel import Session, select

from .database import create_db_and_tables, engine
from .data_processing import extract_banks_data, extract_countries_data
from .models import (
    Bank,
    BankCreate,
    BankWithBranches,
    BankWithoutBranches,
    Country,
    CountryWithBanks,
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Connects all parts of the application.

    Parameters
    ----------
    app : FastAPI
        FastApi to be used.
    """
    excel_file_path = "./data/swift_codes.xlsx"
    banks_data = extract_banks_data(excel_file_path)
    countries_data = extract_countries_data(excel_file_path)
    create_db_and_tables()
    with Session(engine) as session:  # TODO: to be dependent on existance of .db file
        create_countries(session=session, countries_data=countries_data)
        create_banks(session=session, banks_data=banks_data)
    yield


app = FastAPI(lifespan=lifespan)


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
    if len(country_iso2_code) != ISO2_LEN:
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


@app.get(
    "/v1/swift-codes/{swift_code}",
    status_code=status.HTTP_200_OK,
    response_model=Union[BankWithBranches, BankWithoutBranches],
)
def read_bank(*, session: Session = Depends(get_session), swift_code: str):
    """Gets information about the bank with the specified SWIFT code.

    Parameters
    ----------
    session : sqlmodel.Session
        SQLModel Session used to interact with the database.
    swift_code : str
        The SWIFT code of the bank.

    Returns
    -------
    BankWithBranches or BankWithoutBranches
        Bank information with branches if headquarter, otherwise without branches.

    Raises
    ------
    HTTPException
        Unprocessable entity (422) if the SWIFT code is incorrect.
        Not found (404) if a bank with a given SWIFT code does not exist in the database.
    """
    check_swift_code_correctness(swift_code)
    bank = session.exec(select(Bank).where(Bank.swift_code == swift_code)).first()
    check_if_exists_in_db(bank)

    if bank.is_headquarter:
        return BankWithBranches.from_bank(bank)
    else:
        return BankWithoutBranches.from_bank(bank)


@app.get(
    "/v1/swift-codes/country/{country_iso2_code}",
    status_code=status.HTTP_200_OK,
    response_model=CountryWithBanks,
)
def read_country(*, session: Session = Depends(get_session), country_iso2_code: str):
    """Gets information about the country with the specified ISO2 code.

    Parameters
    ----------
    session : sqlmodel.Session
        SQLModel Session used to interact with the database.
    country_iso2_code : str
        The ISO2 code of the country.

    Returns
    -------
    CountryWithBanks
        Country information with associated banks.

    Raises
    ------
    HTTPException
        Unprocessable entity (422) if the country ISO2 code is incorrect.
        Not found (404) if a country with a given ISO2 code does not exist in the database.
    """
    check_country_iso2_code_correctness(country_iso2_code)
    country = session.exec(
        select(Country).where(Country.iso2 == country_iso2_code)
    ).first()
    check_if_exists_in_db(country)

    return CountryWithBanks.from_country(country)


@app.post("/v1/swift-codes", status_code=status.HTTP_201_CREATED)
def create_bank(*, session: Session = Depends(get_session), bank_create: BankCreate):
    """Inserts a bank and a country (if needed) to the database.

    Parameters
    ----------
    session : sqlmodel.Session
        SQLModel Session used to interact with the database.
    bank_create : BankCreate
        JSON providing information about the bank and the country.

    Returns
    -------
    JSONResponse
        Information about successfull creation of the bank and the country (if needed).

    Raises
    ------
    HTTPException
        Unprocessable entity (422) if the country ISO2 code is incorrect.
        Unprocessable entity (422) if the country name is not uppercase.
        Unprocessable entity (422) if the bank SWIFT code is incorrect.
        Conflict (409) if provided country name is different from the one in the database.
    """
    check_country_iso2_code_correctness(bank_create.countryISO2)
    check_country_name_correctness(bank_create.countryName)
    check_swift_code_correctness(bank_create.swiftCode)

    country = session.exec(
        select(Country).where(Country.iso2 == bank_create.countryISO2)
    ).first()

    if not Country:  # new countries are created when needed
        country = Country(iso2=bank_create.countryISO2, name=bank_create.countryName)
        session.add(country)
        session.commit()
        session.refresh(country)
    else:
        if country.name != bank_create.countryName:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "In our database the countryName for countryISO2 ="
                    + f" {country.iso2} is {country.name}."
                ),
            )

    bank = Bank(
        swift_code=bank_create.swiftCode,
        name=bank_create.bankName,
        address=bank_create.address,
        is_headquarter=bank_create.isHeadquarter,
        country=country,
    )

    session.add(bank)
    session.commit()

    # TODO: adjust so it is properly presented in /docs
    return JSONResponse(
        content={
            "message": f"SWIFT CODE = {bank_create.swiftCode} successfully create."
        }
    )


@app.delete("/v1/swift-codes/{swift_code}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bank(*, session: Session = Depends(get_session), swift_code: str):
    """Deletes the bank with the given SWIFT code from the database

    Parameters
    ----------
    session : sqlmodel.Session
        SQLModel Session used to interact with the database.
    swift_code : str
        The SWIFT code of the bank.

    Returns
    -------
    JSONResponse
        Information about successfull deletion of the bank.

    Raises
    ------
    HTTPException
        Unprocessable entity (422) if the SWIFT code is incorrect.
        Not found (404) if a bank with a given SWIFT code does not exist in the database.
    """
    check_swift_code_correctness(swift_code)
    bank = session.exec(select(Bank).where(Bank.swift_code == swift_code)).first()
    check_if_exists_in_db(bank)
    deleted_swift_code = bank.swift_code
    session.delete(bank)
    session.commit()
    return JSONResponse(
        content={"message": f"SWIFT CODE = {deleted_swift_code} successfully deleted."}
    )
