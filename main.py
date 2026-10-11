import asyncio
import logging
import logging.config
import os

from handlers import admin_router, chat_router
from loader import bot, db, dp, watcher
from utils.logger import LOGGER_CONFIG

logger = logging.getLogger("main")

background_tasks: set[asyncio.Task] = set()


async def on_startup() -> None:
    await db.init_models()
    task = asyncio.create_task(watcher.run_forever(), name="market-watcher")
    # Keep a strong reference so the task is not garbage-collected mid-run.
    background_tasks.add(task)
    task.add_done_callback(background_tasks.discard)


async def on_shutdown() -> None:
    for task in list(background_tasks):
        task.cancel()
    await asyncio.gather(*background_tasks, return_exceptions=True)
    await db.close()


async def main() -> None:
    dp.include_routers(admin_router, chat_router)
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    logger.info("Bot started!")
    await dp.start_polling(bot, drop_pending_updates=True)


if __name__ == "__main__":
    os.makedirs("logs", exist_ok=True)
    logging.config.dictConfig(LOGGER_CONFIG)
    try:
        asyncio.run(main())
    except Exception:
        logger.exception("Bot stopped due to an unhandled error")
        raise
