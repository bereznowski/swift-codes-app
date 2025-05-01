"""This module is responsible for connecting all parts of the app."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from sqlmodel import Session, select

from .database import create_db_and_tables, engine
from .data_processing import extract_banks_data, extract_countries_data
from .models import (
    Bank,
    BankBase,
    BankCreate,
    BankWithBranches,
    Country,
    CountryWithBanks,
)


def get_session():
    """Gets new session."""
    with Session(engine) as session:
        yield session


def create_banks(*, session: Session, banks_data: list[dict]):
    """Adds banks data to database.

    Parameters
    ----------
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
        address = None if bank["address"].strip() == "" else bank["address"].strip()
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
                address=address,
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


@asynccontextmanager  # TODO: ensure that countries and banks are correctly created
async def lifespan(app: FastAPI):
    """Connects all parts of the application."""
    excel_file_path = "./data/swift_codes.xlsx"
    banks_data = extract_banks_data(excel_file_path)
    countries_data = extract_countries_data(excel_file_path)
    create_db_and_tables()
    # create_countries(session=get_session(), countries_data=countries_data)
    # create_banks(session=get_session(), banks_data=banks_data)
    yield


app = FastAPI(lifespan=lifespan)  # TODO: ensure proper error handling and all use cases


@app.post("/v1/swift-codes")
def create_bank(bank_create: BankCreate):
    with Session(engine) as session:
        country = session.exec(
            select(Country).where(Country.iso2 == bank_create.countryISO2)
        ).first()

        # actually, this POST can create new countries
        if country is None:
            country = Country(
                iso2=bank_create.countryISO2, name=bank_create.countryName
            )
            session.add(country)
            session.commit()
            session.refresh(country)

        bank = Bank(
            swift_code=bank_create.swiftCode,
            name=bank_create.bankName,
            address=bank_create.address,
            is_headquarter=bank_create.isHeadquarter,
            country=country,
        )

        session.add(bank)
        session.commit()


@app.get("/v1/swift-codes/{swift_code}")
def read_bank(swift_code: str):
    with Session(engine) as session:
        bank = session.exec(select(Bank).where(Bank.swift_code == swift_code)).first()

        if bank.is_headquarter:
            return BankWithBranches.from_bank(bank)
        else:
            return BankCreate.from_bank(bank)


@app.get("/v1/swift-codes/country/{country_iso2_code}")
def read_country(country_iso2_code: str):
    with Session(engine) as session:
        country = session.exec(
            select(Country).where(Country.iso2 == country_iso2_code)
        ).first()

        return CountryWithBanks.from_country(country)


@app.delete("/v1/swift-codes/{swift_code}")
def delete_bank(swift_code: str):
    with Session(engine) as session:
        bank = session.exec(select(Bank).where(Bank.swift_code == swift_code)).first()
        if not bank:
            raise HTTPException(status_code=404, detail="SWIFT code not found")
        session.delete(bank)
        session.commit()
        return {"ok": True}
