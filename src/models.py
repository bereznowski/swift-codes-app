"""This module is responsible for creating Country and Bank models."""

from sqlmodel import Field, Relationship, SQLModel

ISO2_CODE_LEN = 2
SWIFT_CODE_LEN = 11


class Bank(SQLModel, table=True):
    """Table model for the bank."""

    id: int | None = Field(default=None, primary_key=True)
    swift_code: str = Field(
        min_length=SWIFT_CODE_LEN, max_length=SWIFT_CODE_LEN, index=True, unique=True
    )
    name: str
    address: str
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


class BankWithoutCountryName(SQLModel):
    """Object model for the bank used in a list of headquarter's branches or country's banks."""

    address: str
    bankName: str
    countryISO2: str = Field(min_length=ISO2_CODE_LEN, max_length=ISO2_CODE_LEN)
    isHeadquarter: bool
    swiftCode: str = Field(min_length=SWIFT_CODE_LEN, max_length=SWIFT_CODE_LEN)

    @classmethod
    def from_bank(cls, bank: Bank):
        """Creates object of BankWithoutCountryName based on the Bank object.

        Parameters
        ----------
        bank : Bank
            Bank object to be converted.

        Returns
        -------
        BankWithoutCountryName
            New object of the BankWithoutCountryName class.
        """
        return cls(
            address=bank.address,
            bankName=bank.name,
            countryISO2=bank.country.iso2,
            isHeadquarter=bank.is_headquarter,
            swiftCode=bank.swift_code,
        )


# This model could simply inherit from BankWithoutCountryName.
# It is defined in this way to excatly match JSON properties' order described in requirements.
class BankCreate(SQLModel):
    """Object model for the bank used when creating new banks."""

    address: str
    bankName: str
    countryISO2: str = Field(min_length=ISO2_CODE_LEN, max_length=ISO2_CODE_LEN)
    countryName: str
    isHeadquarter: bool
    swiftCode: str = Field(min_length=SWIFT_CODE_LEN, max_length=SWIFT_CODE_LEN)

    @classmethod
    def from_bank(cls, bank: Bank):
        """Creates object of BankCreate based on the Bank object.

        Parameters
        ----------
        bank : Bank
            Bank object to be converted.

        Returns
        -------
        BankCreate
            New object of the BankCreate class.
        """
        return cls(
            address=bank.address,
            bankName=bank.name,
            countryISO2=bank.country.iso2,
            countryName=bank.country.name,
            isHeadquarter=bank.is_headquarter,
            swiftCode=bank.swift_code,
        )


class BankBranch(BankCreate):
    """Object model for the bank used when describing a branch directly."""


class BankHeadquarter(BankCreate):
    """Object model for the bank used when describing a headquarter."""

    branches: list[BankWithoutCountryName]

    @classmethod
    def from_bank(cls, bank: Bank):
        """Creates object of BankHeadquarter based on the Bank object.

        Parameters
        ----------
        bank : Bank
            Bank object to be converted.

        Returns
        -------
        BankHeadquarter
            New object of the BankHeadquarter class.
        """
        base = BankCreate.from_bank(bank)
        branches = [BankWithoutCountryName.from_bank(b) for b in bank.branches]
        return cls(**base.model_dump(), branches=branches)


class Country(SQLModel, table=True):
    """Table model for the country."""

    id: int | None = Field(default=None, primary_key=True)
    iso2: str = Field(min_length=ISO2_CODE_LEN, max_length=ISO2_CODE_LEN, index=True, unique=True)
    name: str
    banks: list["Bank"] = Relationship(back_populates="country")


class CountryWithBanks(SQLModel):
    """Object model for the country used when describing country with associated banks."""

    countryISO2: str
    countryName: str
    swiftCodes: list[BankWithoutCountryName]

    @classmethod
    def from_country(cls, country: Country):
        """Creates object of CountryWithBanks based on the Country object.

        Parameters
        ----------
        country : Country
            Country object to be converted.

        Returns
        -------
        CountryWithBanks
            New object of the CountryWithBanks class.
        """
        swift_codes = [BankWithoutCountryName.from_bank(b) for b in country.banks]
        return cls(
            countryISO2=country.iso2, countryName=country.name, swiftCodes=swift_codes
        )
