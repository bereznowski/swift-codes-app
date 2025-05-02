"""This module is responsible for connecting all parts of the app."""

import os

from contextlib import asynccontextmanager
from typing import Union

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from .database import create_db_and_tables, engine
from .data_processing import extract_banks_data, extract_countries_data
from .models import (
    Bank,
    BankCreate,
    BankHeadquarter,
    BankBranch,
    Country,
    CountryWithBanks,
)
from .utils import (
    create_banks,
    create_countries,
    check_country_iso2_code_correctness,
    check_country_name_correctness,
    check_if_exists_in_db,
    check_swift_code_correctness,
    get_session,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Connects all parts of the application.

    Parameters
    ----------
    app : FastAPI
        FastApi to be used.
    """
    excel_file_path = "./data/swift_codes.xlsx"
    database_file_path = "./data/database.db"
    banks_data = extract_banks_data(excel_file_path)
    countries_data = extract_countries_data(excel_file_path)
    if not os.path.exists(database_file_path):
        create_db_and_tables()
        with Session(engine) as session:
            create_countries(session=session, countries_data=countries_data)
            create_banks(session=session, banks_data=banks_data)
    yield


app = FastAPI(lifespan=lifespan)


@app.get(
    "/v1/swift-codes/{swift_code}",
    status_code=status.HTTP_200_OK,
    response_model=Union[BankHeadquarter, BankBranch],
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
    BankHeadquarter or BankBranch
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
        return BankHeadquarter.from_bank(bank)
    else:
        return BankBranch.from_bank(bank)


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

    last_three_symbols_in_swift = bank_create.swiftCode[-3:]

    if (last_three_symbols_in_swift == "XXX" and not bank_create.isHeadquarter) or (
        last_three_symbols_in_swift != "XXX" and bank_create.isHeadquarter
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Headquarter's SWIFT codes must end with XXX and branches' cannot and with XXX.",
        )

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

    if bank_create.isHeadquarter:
        bank.branches = session.exec(
            select(Bank).where(
                Bank.swift_code.like(
                    bank_create.swiftCode[:8] + "___"
                )  # This is a workaround for a lack of LIKE support in the current version of SQLModel
                # like() from SQLAlchemy is used (causes linting error)
            )
        ).all()

    else:
        bank.headquarter = session.exec(
            select(Bank).where(Bank.swift_code == bank_create.swiftCode[:8] + "XXX")
        ).first()

    try:
        session.add(bank)
        session.commit()
    except IntegrityError as e:
        session.rollback()
        if "UNIQUE constraint failed" in str(e.orig):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"{e.orig}",
            ) from e

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
