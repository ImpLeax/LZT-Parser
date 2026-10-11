import asyncio
import logging
import time

from aiogram import Bot
from LOLZTEAM.Client import Market

from config import Settings
from db.database import BotDatabase
from lzt.account import Account
from lzt.filters import is_prime_old_enough, is_trusted_seller
from lzt.formatting import format_account
from lzt.search import SEARCH_PARAMS

logger = logging.getLogger(__name__)

# Pause between Telegram messages to stay well below the per-chat rate limit.
SEND_DELAY_SECONDS = 0.5


class MarketWatcher:
    """Polls the LZT Market search and posts new matching listings to Telegram."""

    def __init__(self, market: Market, bot: Bot, db: BotDatabase, settings: Settings):
        self.market = market
        self.bot = bot
        self.db = db
        self.settings = settings

    async def run_forever(self) -> None:
        logger.info("Launching the marketplace's background parser...")
        while True:
            try:
                await self.fetch_and_notify()
            except Exception:
                logger.exception("Market polling iteration failed")
            await asyncio.sleep(self.settings.POLL_INTERVAL_SECONDS)

    async def fetch_and_notify(self) -> None:
        accounts = await self._fetch_accounts()
        candidates = [acc for acc in accounts if self._matches(acc)]
        if not candidates:
            return

        notified_ids = await self.db.get_notified_item_ids([acc.item_id for acc in candidates])
        new_accounts = [acc for acc in candidates if acc.item_id not in notified_ids]
        if not new_accounts:
            logger.info("No new accounts were found.")
            return

        logger.info("New accounts found: %d", len(new_accounts))
        await self.db.upsert_items(
            [
                {"item_id": acc.item_id, "title": acc.title, "price_usd": acc.price_usd}
                for acc in new_accounts
            ]
        )

        # Items that fail to send stay unnotified and are retried on the next poll.
        sent_ids = []
        for acc in new_accounts:
            try:
                await self.bot.send_message(
                    chat_id=self.settings.CHAT_ID,
                    message_thread_id=self.settings.THREAD_ID,
                    text=format_account(acc),
                    disable_web_page_preview=True,
                )
                sent_ids.append(acc.item_id)
            except Exception:
                logger.exception("Failed to send item %s to Telegram", acc.item_id)
            await asyncio.sleep(SEND_DELAY_SECONDS)

        await self.db.mark_items_as_notified(sent_ids)

    async def _fetch_accounts(self) -> list[Account]:
        response = await self.market.request("GET", "/steam", params=SEARCH_PARAMS)
        data = response if isinstance(response, dict) else response.json()
        return [Account.from_dict(item) for item in data.get("items", [])]

    def _matches(self, acc: Account) -> bool:
        return is_trusted_seller(
            acc,
            min_reviews=self.settings.MIN_SELLER_REVIEWS,
            min_positive_percent=self.settings.MIN_POSITIVE_PERCENT,
        ) and is_prime_old_enough(
            acc,
            min_age_years=self.settings.PRIME_MIN_AGE_YEARS,
            now=time.time(),
        )
