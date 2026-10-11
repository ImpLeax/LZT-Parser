import datetime
from typing import Annotated

from sqlalchemy import BigInteger, Boolean, DateTime, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

intpk = Annotated[int, mapped_column(primary_key=True)]
created_at = Annotated[
    datetime.datetime, mapped_column(DateTime(timezone=True), server_default=func.now())
]
updated_at = Annotated[
    datetime.datetime,
    mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now()),
]


class Base(DeclarativeBase):
    pass


class MarketItem(Base):
    __tablename__ = "market_items"

    id: Mapped[intpk]

    item_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)

    price_usd: Mapped[float]

    title: Mapped[str] = mapped_column(String(255))

    is_notified: Mapped[bool] = mapped_column(Boolean, default=False)

    discovered_at: Mapped[created_at]

    def __repr__(self):
        return f"<MarketItem(item_id={self.item_id}, price=${self.price_usd})>"
