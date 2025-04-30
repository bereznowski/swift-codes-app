"""This module is responsible for connecting all parts of the app."""

from sqlmodel import Session

from .database import create_db_and_tables, engine
from .data_processing import extract_banks_data, extract_countries_data
from .models import Bank, Country


# TODO: insert data from excel into table models
def create_banks(banks_data: list[dict]):
    with Session(engine) as session:
        pass


def create_countries(countries_data: list[dict]):
    with Session(engine) as session:
        pass


def main():
    excel_file_path = "./data/swift_codes.xlsx"
    banks_data = extract_banks_data(excel_file_path)
    countries_data = extract_countries_data(excel_file_path)
    create_db_and_tables()
    create_countries(countries_data=countries_data)
    create_banks(banks_data=banks_data)

    # TODO: add FastAPI


if __name__ == "__main__":
    main()
