from sqlalchemy import URL, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from .models import Base, MarketItem


class BotDatabase:
    def __init__(self, url: URL):
        self.engine = create_async_engine(url=url, echo=False)
        self.session_factory = async_sessionmaker(self.engine, expire_on_commit=False)

    async def init_models(self) -> None:
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def close(self) -> None:
        await self.engine.dispose()

    async def get_notified_item_ids(self, item_ids: list[int]) -> set[int]:
        if not item_ids:
            return set()

        async with self.session_factory() as session:
            stmt = select(MarketItem.item_id).where(
                MarketItem.item_id.in_(item_ids),
                MarketItem.is_notified.is_(True),
            )
            result = await session.execute(stmt)
            return set(result.scalars().all())

    async def upsert_items(self, items_data: list[dict]) -> None:
        """Insert items that are not stored yet; existing rows are left untouched."""
        if not items_data:
            return

        async with self.session_factory() as session:
            stmt = (
                insert(MarketItem)
                .values(items_data)
                .on_conflict_do_nothing(index_elements=[MarketItem.item_id])
            )
            await session.execute(stmt)
            await session.commit()

    async def mark_items_as_notified(self, item_ids: list[int]) -> None:
        if not item_ids:
            return

        async with self.session_factory() as session:
            stmt = (
                update(MarketItem).where(MarketItem.item_id.in_(item_ids)).values(is_notified=True)
            )
            await session.execute(stmt)
            await session.commit()
