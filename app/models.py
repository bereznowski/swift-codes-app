from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from typing import List
from typing import Optional


class Base(DeclarativeBase):
    pass


class Country(Base):
    __tablename__ = "country"

    country_iso2: Mapped[str] = mapped_column(String(2), primary_key=True)
    country_name: Mapped[str]

    banks: Mapped[Optional[List["Bank"]]] = relationship(back_populates="country")

    def __repr__(self) -> str:
        return f"Country(country_iso2={self.country_iso2!r}, country_name={self.country_name!r}, banks={[self.banks[i].swift_code for i in range(len(self.banks))]!r})"


class Bank(Base):
    __tablename__ = "bank"

    swift_code: Mapped[str] = mapped_column(String(11), primary_key=True)
    bank_name: Mapped[str]
    address: Mapped[Optional[str]]
    is_headquarter: Mapped[bool]
    country_iso2 = mapped_column(String, ForeignKey("country.country_iso2"))
    hq_swift_code: Mapped[Optional[str]] = mapped_column(
        String, ForeignKey("bank.swift_code")
    )

    country: Mapped["Country"] = relationship(back_populates="banks")
    headquarter: Mapped[Optional["Bank"]] = relationship("Bank")

    def __repr__(self) -> str:
        return (
            f"Bank(swift_code={self.swift_code!r}, "
            f"bank_name={self.bank_name!r}, address={self.address!r}, "
            f"country_iso2={self.country_iso2!r}, is_headquarter={self.is_headquarter!r}, "
            f"hq_swift_code={self.hq_swift_code!r})"
        )
