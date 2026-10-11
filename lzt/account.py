"""Typed model of a single LZT Market Steam listing."""

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

PRIME_UPGRADE_PRODUCT = "Prime Status Upgrade"

# Amounts such as "12.50€" or "300" inside a transaction source string.
_AMOUNT_RE = re.compile(r"[0-9]+[.,]?[0-9]*[€$£₽]?")


@dataclass
class SellerInfo:
    user_id: int
    username: str
    sold_items_count: int
    active_items_count: int
    is_banned: bool
    restore_percents: int
    total_reviews: int = 0
    positive_reviews: int = 0
    negative_reviews: int = 0
    positive_percent: float = 0.0


@dataclass
class SteamInventory:
    cs2_value: float = 0.0
    dota2_value: float = 0.0
    tf2_value: float = 0.0
    rust_value: float = 0.0
    steam_value: float = 0.0
    pubg_value: float = 0.0


@dataclass
class SteamFinance:
    balance: str = ""
    converted_balance: float = 0.0
    total_purchased_rub: float = 0.0
    total_spend_rub: float = 0.0


@dataclass
class CS2Stats:
    rank_id: int = 0
    wingman_rank_id: int = 0
    profile_rank: int = 0
    premier_elo: int = 0
    win_count: int = 0
    medal_count: int = 0
    last_activity: int = 0
    last_launched: int = 0


@dataclass
class SteamStats:
    steam_id: int
    country: str
    register_date: int
    last_activity: int
    level: int
    game_count: int
    friend_count: int
    hours_played_recently: float
    is_limited: bool
    has_faceit: bool
    community_ban: bool
    vac_bans: str
    trade_ban: bool


@dataclass
class Account:
    item_id: int
    title: str
    price_usd: float
    price_rub: float
    item_origin: str
    published_date: int
    view_count: int

    seller: SellerInfo
    steam_stats: SteamStats
    cs2_stats: CS2Stats
    inventory: SteamInventory
    finance: SteamFinance

    email_provider: str
    is_prime: bool = False

    last_transaction_date: str = "Unknown"
    prime_upgrade_info: str = "Not found in history"
    prime_upgrade_timestamp: int = 0
    unique_payment_methods: set[str] = field(default_factory=set)
    raw_data: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Account":
        total_pos, total_neg = _count_feedback(data.get("feedback_data", "{}"))
        total_reviews = total_pos + total_neg
        pos_percent = round(total_pos / total_reviews * 100, 1) if total_reviews > 0 else 0.0

        seller_data = data.get("seller", {})
        seller = SellerInfo(
            user_id=seller_data.get("user_id", 0),
            username=seller_data.get("username", "Unknown"),
            sold_items_count=seller_data.get("sold_items_count", 0),
            active_items_count=seller_data.get("active_items_count", 0),
            is_banned=bool(seller_data.get("is_banned", 0)),
            restore_percents=seller_data.get("restore_percents", 0),
            total_reviews=total_reviews,
            positive_reviews=total_pos,
            negative_reviews=total_neg,
            positive_percent=pos_percent,
        )

        finance = SteamFinance(
            balance=data.get("steam_balance", ""),
            converted_balance=data.get("steam_converted_balance", 0.0),
            total_purchased_rub=data.get("steam_total_purchased_rub", 0.0),
            total_spend_rub=data.get("steam_total_spend_rub", 0.0),
        )

        inventory = SteamInventory(
            cs2_value=data.get("steam_cs2_inv_value", 0.0),
            steam_value=data.get("steam_steam_inv_value", 0.0),
        )

        cs2_stats = CS2Stats(
            rank_id=data.get("steam_cs2_rank_id", 0),
            wingman_rank_id=data.get("steam_cs2_wingman_rank_id", 0),
            profile_rank=data.get("steam_cs2_profile_rank", 0),
            premier_elo=data.get("steam_cs2_premier_elo", 0),
            win_count=data.get("steam_cs2_win_count", 0),
            last_activity=data.get("steam_cs2_last_activity", 0),
        )

        steam_stats = SteamStats(
            steam_id=data.get("steam_item_id", 0),
            country=data.get("steam_country", ""),
            register_date=data.get("steam_register_date", 0),
            last_activity=data.get("steam_last_activity", 0),
            level=data.get("steam_level", 0),
            game_count=data.get("steam_game_count", 0),
            friend_count=data.get("steam_friend_count", 0),
            hours_played_recently=float(data.get("steam_hours_played_recently", 0)),
            is_limited=bool(data.get("steam_is_limited", 0)),
            has_faceit=bool(data.get("steam_has_faceit", 0)),
            community_ban=bool(data.get("steam_community_ban", 0)),
            vac_bans=data.get("steam_bans", ""),
            trade_ban=bool(data.get("steam_trade_ban", 0)),
        )

        # PHP-backed APIs encode empty objects as [], so guard every level.
        full_games = data.get("steam_full_games") or {}
        games_list = (full_games.get("list") or {}) if isinstance(full_games, dict) else {}
        cs2_game = games_list.get("730") if isinstance(games_list, dict) else None
        is_prime = bool(cs2_game.get("is_paid", 0)) if isinstance(cs2_game, dict) else False

        transactions = data.get("steamTransactions", [])
        unique_payment_methods: set[str] = set()
        prime_upgrade_info = "Not found in history"
        prime_upgrade_timestamp = 0
        last_transaction_date = "Unknown"

        if transactions:
            # The API returns transactions newest first.
            latest_ts = _to_timestamp(transactions[0].get("date"))
            if latest_ts > 0:
                last_transaction_date = _format_date(latest_ts)

            for transaction in transactions:
                source_words = _extract_payment_words(transaction.get("source", ""))
                unique_payment_methods.update(source_words)

                if transaction.get("product") == PRIME_UPGRADE_PRODUCT:
                    prime_ts = _to_timestamp(transaction.get("date"))
                    if prime_ts > 0:
                        source = " ".join(source_words) or "Unknown"
                        prime_upgrade_info = f"{_format_date(prime_ts)} (via {source})"
                        prime_upgrade_timestamp = prime_ts

        return cls(
            item_id=data.get("item_id", 0),
            title=data.get("title", ""),
            price_usd=data.get("price", 0.0),
            price_rub=data.get("rub_price", 0.0),
            item_origin=data.get("item_origin", ""),
            published_date=data.get("published_date", 0),
            view_count=data.get("view_count", 0),
            email_provider=data.get("email_provider", ""),
            is_prime=is_prime,
            seller=seller,
            steam_stats=steam_stats,
            cs2_stats=cs2_stats,
            inventory=inventory,
            finance=finance,
            last_transaction_date=last_transaction_date,
            prime_upgrade_info=prime_upgrade_info,
            prime_upgrade_timestamp=prime_upgrade_timestamp,
            unique_payment_methods=unique_payment_methods,
            raw_data=data,
        )


def _count_feedback(feedback: Any) -> tuple[int, int]:
    """Sum positive/negative reviews across all categories of `feedback_data`.

    The API sends it as a JSON string; a decoded dict is accepted as well.
    """
    if isinstance(feedback, str):
        try:
            feedback = json.loads(feedback)
        except json.JSONDecodeError:
            return 0, 0
    if not isinstance(feedback, dict):
        return 0, 0

    positive = negative = 0
    for stats in feedback.values():
        if isinstance(stats, dict):
            positive += stats.get("positive", 0)
            negative += stats.get("negative", 0)
    return positive, negative


def _extract_payment_words(source: str) -> list[str]:
    """Extract payment method names from a transaction source, dropping amounts and masks."""
    if not source:
        return []
    cleaned = source.replace("\t", " ").replace("\n", " ").replace("*", "")
    cleaned = _AMOUNT_RE.sub("", cleaned)
    return [word for word in cleaned.split() if word.isalpha() and len(word) >= 3]


def _to_timestamp(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _format_date(timestamp: int) -> str:
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
