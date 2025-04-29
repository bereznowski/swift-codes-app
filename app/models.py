"""This module is responsible for creating Country and Bank models."""

from sqlmodel import Field, Relationship, SQLModel


class Bank(SQLModel, table=True):
    """Table model for the bank."""

    id: int | None = Field(default=None, primary_key=True)
    swift_code: str = Field(min_length=11, max_length=11, index=True, unique=True)
    name: str
    address: str | None = Field(default=None)
    is_headquarter: bool
    country_id: int = Field(default=None, foreign_key="country.id")
    headquarter_id: int | None = Field(default=None, foreign_key="bank.id")

    country: "Country" = Relationship(back_populates="banks")
    headquarter: "Bank" = Relationship(
        sa_relationship_kwargs=dict(remote_side="Bank.id"), back_populates="branches"
    )
    branches: list["Bank"] = Relationship(back_populates="headquarter")


class Country(SQLModel, table=True):
    """Table model for the country."""

    id: int | None = Field(default=None, primary_key=True)
    iso2: str = Field(min_length=2, max_length=2, index=True, unique=True)
    name: str

    banks: list["Bank"] = Relationship(back_populates="country")
