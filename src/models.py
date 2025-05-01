"""This module is responsible for creating Country and Bank models."""

from sqlmodel import Field, Relationship, SQLModel

# TODO: check correctness of all provided data
class Bank(SQLModel, table=True):
    """Table model for the bank."""

    id: int | None = Field(default=None, primary_key=True)
    swift_code: str = Field(min_length=11, max_length=11, index=True, unique=True)
    name: str
    address: str # TODO: change to only
    is_headquarter: bool
    country_id: int = Field(foreign_key="country.id")
    headquarter_id: int | None = Field(
        default=None, foreign_key="bank.id", ondelete="SET NULL"
    )

    country: "Country" = Relationship(back_populates="banks")
    headquarter: "Bank" = Relationship(
        sa_relationship_kwargs=dict(remote_side="Bank.id"),
        back_populates="branches",
        passive_deletes="all",
    )
    branches: list["Bank"] = Relationship(
        back_populates="headquarter", passive_deletes="all"
    )


class BankBase(SQLModel):
    address: str
    bankName: str
    countryISO2: str = Field(min_length=2, max_length=2)
    isHeadquarter: bool
    swiftCode: str = Field(min_length=11, max_length=11)

    @classmethod
    def from_bank(cls, bank: Bank):
        return cls(
            address=bank.address,
            bankName=bank.name,
            countryISO2=bank.country.iso2,
            isHeadquarter=bank.is_headquarter,
            swiftCode=bank.swift_code,
        )


class BankCreate(BankBase):
    countryName: str  # TODO: change order of fields returned by SQLModel

    @classmethod
    def from_bank(cls, bank: Bank):
        base = BankBase.from_bank(bank)
        return cls(**base.model_dump(), countryName=bank.country.name)


class BankWithBranches(BankCreate):
    branches: list[BankBase]

    @classmethod
    def from_bank(cls, bank: Bank):
        base = BankCreate.from_bank(bank)
        branches = [BankBase.from_bank(b) for b in bank.branches]
        return cls(**base.model_dump(), branches=branches)


class Country(SQLModel, table=True):
    """Table model for the country."""

    id: int | None = Field(default=None, primary_key=True)
    iso2: str = Field(min_length=2, max_length=2, index=True, unique=True)
    name: str
    banks: list["Bank"] = Relationship(
        back_populates="country"
    )  # TODO: explicitly define action on delete


class CountryWithBanks(SQLModel):
    countryISO2: str
    countryName: str
    swiftCodes: list[BankBase]

    @classmethod
    def from_country(cls, country: Country):
        swiftCodes = [BankBase.from_bank(b) for b in country.banks]
        return cls(
            countryISO2=country.iso2, countryName=country.name, swiftCodes=swiftCodes
        )
