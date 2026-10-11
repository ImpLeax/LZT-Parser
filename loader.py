"""Composition root: creates the shared API clients from settings at import time."""

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from LOLZTEAM.Client import Market

from config import settings
from db.database import BotDatabase
from services.market_watcher import MarketWatcher

market = Market(settings.LZT_API_KEY.get_secret_value())
market.settings.delay.enable()
market.settings.delay.min = 3
market.settings.logger.disable()

bot = Bot(
    token=settings.TG_API_KEY.get_secret_value(),
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)

dp = Dispatcher()
db = BotDatabase(settings.database_url)
watcher = MarketWatcher(market=market, bot=bot, db=db, settings=settings)
