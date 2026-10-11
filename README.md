# LZT Market Watcher Bot

An async Telegram bot that monitors the [LZT Market](https://lzt.market) for CS2 Steam accounts matching a set of filters and posts each new listing to a Telegram chat (optionally a forum topic) as a formatted card.

## Features

- Polls the LZT Market `/steam` search on a fixed interval with a predefined set of server-side filters (price, region, Prime, bans, activity, etc.).
- Applies extra client-side filters the API cannot express:
  - seller reputation (minimum number of reviews and positive-review percentage);
  - Prime upgrade age (accounts whose Prime was bought recently are skipped).
- Parses the purchase history to show the Prime upgrade date and the payment methods used.
- Deduplicates listings in PostgreSQL, so each account is posted once; listings that fail to send are retried on the next poll.
- `/debug` command for the admin to discover chat / topic IDs during setup.

## Tech stack

Python 3.12 · aiogram 3 · SQLAlchemy 2 (async) + asyncpg · PostgreSQL · pydantic-settings · [LOLZTEAM](https://pypi.org/project/lolzteam/) API client · uv · Docker Compose

## How it works

```
 every POLL_INTERVAL_SECONDS
            │
            ▼
 LZT Market /steam search ──► Account.from_dict ──► seller / Prime filters
                                                           │
                                                           ▼
                         Telegram ◄── format_account ◄── skip already notified (PostgreSQL)
                             │
                             └──► mark as notified
```

| Path | Responsibility |
| --- | --- |
| `lzt/` | Pure domain logic: listing model and parsing, search params, filters, HTML formatting. No I/O, no config. |
| `services/market_watcher.py` | Polling loop: fetch → parse → filter → dedup → send → mark notified. |
| `db/` | SQLAlchemy model (`market_items`) and data-access methods. |
| `handlers.py` | Telegram commands (`/start` in the target chat, admin-only `/debug`). |
| `loader.py` | Builds the shared clients (LZT Market, Bot, Dispatcher, DB) from settings. |
| `config.py` | Settings loaded from environment variables / `.env`. |
| `main.py` | Entry point: logging, router registration, startup/shutdown hooks. |

## Configuration

All credentials are read from environment variables (or a local `.env` file, which is git-ignored). Copy the template and fill it in:

```bash
cp .env.example .env
```

| Variable | Required | Description |
| --- | --- | --- |
| `TG_API_KEY` | yes | Telegram bot token from @BotFather |
| `LZT_API_KEY` | yes | LZT Market API token |
| `CHAT_ID` | yes | Chat where listings are posted |
| `THREAD_ID` | no | Forum topic ID inside `CHAT_ID` |
| `ADMIN_ID` | yes | Telegram user ID allowed to use `/debug` |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` | yes | Database credentials |
| `POSTGRES_HOST`, `POSTGRES_PORT` | yes / no | Database address (`db` inside Docker Compose, default port `5432`) |
| `POLL_INTERVAL_SECONDS` | no | Polling interval, default `60` |
| `MIN_SELLER_REVIEWS` | no | Minimum seller reviews, default `100` |
| `MIN_POSITIVE_PERCENT` | no | Minimum positive-review percentage, default `90.0` |
| `PRIME_MIN_AGE_YEARS` | no | Minimum age of the Prime upgrade, default `10` |

The search itself (price cap, excluded countries, etc.) is defined in `lzt/search.py`.

To find `CHAT_ID` / `THREAD_ID`, add the bot to the chat and send `/debug` from the `ADMIN_ID` account.

## Running

### Docker Compose (recommended)

```bash
docker compose up -d --build
docker compose logs -f bot
```

PostgreSQL is not exposed to the host by default. The table is created automatically on first start.

### Locally

Requires [uv](https://docs.astral.sh/uv/) and a reachable PostgreSQL instance (set `POSTGRES_HOST` accordingly).

```bash
uv sync
uv run main.py
```

Logs are written to stdout and `logs/log.log` (rotated).

## Development

```bash
uv sync                    # installs dev dependencies (pytest, ruff) too
uv run pytest              # tests (no network or database required)
uv run ruff check .        # lint
uv run ruff format .       # format
```

## Disclaimer

Personal project built for my own use. Use it in accordance with the LZT Market and Telegram terms of service.
