"""This module is responsible for testing models from app/models.py"""

import pytest

from sqlmodel import Session, SQLModel, create_engine, select

from src.models import Bank, Country


@pytest.fixture(name="banks_data")
def fixture_banks_data():
    """Exemplary banks data inserted into database.

    The data includes following cases:
    - headquarter with branches (1 or 2 branches),
    - headquarter without branches,
    - branch without headquarter,
    - many banks from different countries,
    - many banks from the same country,
    - empty address field.

    Returns
    -------
    list[dict]
        List of dicts representing banks.
    """
    return [
        {
            "swift_code": "A1234567XXX",
            "name": "Alior Bank",
            "address": "Alior Bank Address",
            "is_headquarter": True,
            "country_iso2": "PL",
            "headquarter": None,
        },
        {
            "swift_code": "D1234567XXX",
            "name": "Deutsche Bank",
            "address": "Deutsche Bank Address",
            "is_headquarter": True,
            "country_iso2": "DE",
            "headquarter": None,
        },
        {
            "swift_code": "P1234567XXX",
            "name": "PKO Bank",
            "address": "PKO Bank Address",
            "is_headquarter": True,
            "country_iso2": "PL",
            "headquarter": None,
        },
        {
            "swift_code": "A0987654321",
            "name": "Alior Bank",
            "address": " ",
            "is_headquarter": False,
            "country_iso2": "PL",
            "headquarter": None,
        },
        {
            "swift_code": "A1234567890",
            "name": "Alior Bank",
            "address": "Alior Bank Address",
            "is_headquarter": False,
            "country_iso2": "PL",
            "headquarter": "A1234567XXX",
        },
        {
            "swift_code": "A1234567891",
            "name": "Alior Bank",
            "address": "Alior Bank Address",
            "is_headquarter": False,
            "country_iso2": "PL",
            "headquarter": "A1234567XXX",
        },
        {
            "swift_code": "C1234567890",
            "name": "Commerzbank",
            "address": None,
            "is_headquarter": False,
            "country_iso2": "DE",
            "headquarter": "C1234567XXX",
        },
        {
            "swift_code": "D1234567890",
            "name": "Deutsche Bank",
            "address": "Deutsche Bank Address",
            "is_headquarter": False,
            "country_iso2": "DE",
            "headquarter": "D1234567XXX",
        },
    ]


@pytest.fixture(name="countries_data")
def fixture_countries_data():
    """Exemplary countries data inserted into database.

    Returns
    -------
    list[dict]
        List of dicts representing countries.
    """
    return [{"iso2": "DE", "name": "Germany"}, {"iso2": "PL", "name": "Poland"}]


@pytest.fixture(name="session")
def fixture_session():
    """Creates new session for in-memory database.

    Yields
    -------
    sqlmodel.Session
        SQLModel Session connected with in-memory database.
    """
    engine = create_engine("sqlite://")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


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

    deutsche_bank1 = session.exec(
        select(Bank).where(Bank.swift_code == "D1234567890")
    ).one()
    deutsche_bank2 = session.exec(
        select(Bank).where(Bank.swift_code == "D1234567XXX")
    ).one()
    commerzbank = session.exec(
        select(Bank).where(Bank.swift_code == "C1234567890")
    ).one()
    alior_bank1 = session.exec(
        select(Bank).where(Bank.swift_code == "A1234567890")
    ).one()
    alior_bank2 = session.exec(
        select(Bank).where(Bank.swift_code == "A1234567XXX")
    ).one()
    alior_bank3 = session.exec(
        select(Bank).where(Bank.swift_code == "A0987654321")
    ).one()
    alior_bank4 = session.exec(
        select(Bank).where(Bank.swift_code == "A1234567891")
    ).one()
    pko_bank = session.exec(select(Bank).where(Bank.swift_code == "P1234567XXX")).one()

    banks_branches_and_headquarter = [
        {"bank": deutsche_bank1, "branches": [], "headquarter": deutsche_bank2},
        {"bank": deutsche_bank2, "branches": [deutsche_bank1], "headquarter": None},
        {"bank": commerzbank, "branches": [], "headquarter": None},
        {"bank": alior_bank1, "branches": [], "headquarter": alior_bank2},
        {
            "bank": alior_bank2,
            "branches": [alior_bank1, alior_bank4],
            "headquarter": None,
        },
        {"bank": alior_bank3, "branches": [], "headquarter": None},
        {"bank": alior_bank4, "branches": [], "headquarter": alior_bank2},
        {"bank": pko_bank, "branches": [], "headquarter": None},
    ]

    for bank_bh in banks_branches_and_headquarter:
        assert len(bank_bh["bank"].branches) == len(
            bank_bh["branches"]
        ), f"{bank_bh['bank'].swift_code} should have {len(bank_bh['branches'])} branches."
        assert bank_bh["bank"].headquarter == bank_bh["headquarter"], (
            f"{bank_bh['headquarter'].swift_code} should be "
            f"a headquarter of {len(bank_bh['bank'].swift_code)}"
        )
        for branch in bank_bh["branches"]:
            assert (
                branch in bank_bh["bank"].branches
            ), f"{branch.swift_code} should be a branch of {bank_bh['bank'].swift_code}"


def test_relationship_banks_country(session, banks_data, countries_data):
    """Tests relationship between banks and country.

    Parameters
    ----------
    session : sqlmodel.Session
        SQLModel Session used to interact with in-memory database.
    banks_data : list[dict]
        List of dicts used for creating table models of banks.
    countries_data : list[dict]
        List of dicts used for creating table models of countries.
    """
    for country_data in countries_data:
        country = Country(iso2=country_data["iso2"], name=country_data["name"])
        session.add(country)
        session.commit()

    for bank_data in banks_data:
        country = session.exec(
            select(Country).where(Country.iso2 == bank_data["country_iso2"])
        ).first()
        headquarter = session.exec(
            select(Bank).where(Bank.swift_code == bank_data["headquarter"])
        ).first()

        bank = Bank(
            swift_code=bank_data["swift_code"],
            name=bank_data["name"],
            address=bank_data["address"],
            is_headquarter=bank_data["is_headquarter"],
            country_id=country.id if country is not None else None,
            headquarter_id=headquarter.id if headquarter is not None else None,
        )

        session.add(bank)
        session.commit()

    germany = session.exec(select(Country).where(Country.iso2 == "DE")).one()
    poland = session.exec(select(Country).where(Country.iso2 == "PL")).one()

    deutsche_bank1 = session.exec(
        select(Bank).where(Bank.swift_code == "D1234567890")
    ).one()
    deutsche_bank2 = session.exec(
        select(Bank).where(Bank.swift_code == "D1234567XXX")
    ).one()
    commerzbank = session.exec(
        select(Bank).where(Bank.swift_code == "C1234567890")
    ).one()
    alior_bank1 = session.exec(
        select(Bank).where(Bank.swift_code == "A1234567890")
    ).one()
    alior_bank2 = session.exec(
        select(Bank).where(Bank.swift_code == "A1234567XXX")
    ).one()
    alior_bank3 = session.exec(
        select(Bank).where(Bank.swift_code == "A0987654321")
    ).one()
    alior_bank4 = session.exec(
        select(Bank).where(Bank.swift_code == "A1234567891")
    ).one()
    pko_bank = session.exec(select(Bank).where(Bank.swift_code == "P1234567XXX")).one()

    bank_country_pairs = [
        {"bank": deutsche_bank1, "country": germany},
        {"bank": deutsche_bank1, "country": germany},
        {"bank": deutsche_bank2, "country": germany},
        {"bank": commerzbank, "country": germany},
        {"bank": alior_bank1, "country": poland},
        {"bank": alior_bank2, "country": poland},
        {"bank": alior_bank3, "country": poland},
        {"bank": alior_bank4, "country": poland},
        {"bank": pko_bank, "country": poland},
    ]

    for bc_pair in bank_country_pairs:
        assert (
            bc_pair["bank"] in bc_pair["country"].banks
        ), f"{bc_pair['bank'].swift_code} not in {bc_pair['country'].name} banks."
        assert (
            bc_pair["bank"].country == bc_pair["country"]
        ), f"{bc_pair['bank'].swift_code} country is not {bc_pair['country'].name}."
        assert (
            bc_pair["bank"].country_id == bc_pair["country"].id
        ), f"{bc_pair['bank'].swift_code} does not refer to {bc_pair['country'].name} ID."
