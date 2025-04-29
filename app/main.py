"""This module is responsible for connecting all parts of the app."""

from sqlmodel import Session

from .database import create_db_and_tables, engine
from .data_processing import extract_banks_data, extract_countries_data
from .models import Bank, Country


# TODO: insert data from excel into table models
def create_countries():
    with Session(engine) as session:
        pass


def create_banks():
    with Session(engine) as session:
        pass

def main():
    excel_file_path = ""
    banks_data = extract_banks_data(excel_file_path)
    countries_data = extract_countries_data(excel_file_path)
    create_db_and_tables()
    create_countries()
    create_banks()

    print(banks_data)
    print(countries_data)
    # TODO: add FastAPI


if __name__ == "__main__":
    main()
