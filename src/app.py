"""This module is responsible for connecting all parts of the app."""

from sqlmodel import Session, select

from .database import create_db_and_tables, engine
from .data_processing import extract_banks_data, extract_countries_data
from .models import Bank, Country


def create_banks(banks_data: list[dict]):
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
    with Session(engine) as session:
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


def create_countries(countries_data: list[dict]):
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
    with Session(engine) as session:
        for country in countries_data:
            session.add(Country(iso2=country["iso2"], name=country["name"]))
        session.commit()


def main():
    """Connects all parts of the application."""
    excel_file_path = "./data/swift_codes.xlsx"
    banks_data = extract_banks_data(excel_file_path)
    countries_data = extract_countries_data(excel_file_path)
    create_db_and_tables()
    create_countries(countries_data=countries_data)
    create_banks(banks_data=banks_data)

    # TODO: add FastAPI


if __name__ == "__main__":
    main()
