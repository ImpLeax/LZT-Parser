"""Rendering of listings as Telegram HTML messages."""

from datetime import datetime
from html import escape

from .account import Account

MARKET_URL = "https://lzt.market/{item_id}/"


def _flag(value: bool) -> str:
    return "🔴 Yes" if value else "🟢 No"


def _date_or_unknown(timestamp: int) -> str:
    if timestamp > 0:
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
    return "Unknown"


def format_account(acc: Account) -> str:
    """Build the notification text. Every API-sourced string is HTML-escaped."""
    vac_bans = f"🔴 {escape(acc.steam_stats.vac_bans)}" if acc.steam_stats.vac_bans else "🟢 None"
    prime_status = "✅ Yes" if acc.is_prime else "❌ No"

    reviews_text = "No reviews"
    if acc.seller.total_reviews > 0:
        reviews_text = (
            f"{acc.seller.total_reviews} reviews ({acc.seller.positive_percent}% Positive)"
        )

    payments = ", ".join(sorted(acc.unique_payment_methods)) or "None"

    # The API exposes these totals only as *_rub fields; they are intentionally labelled USD.
    total_games_value = acc.raw_data.get("steam_total_games_rub", 0.0) or 0.0
    total_spend = acc.finance.total_purchased_rub or 0.0

    return (
        f"📌 {escape(acc.title)}\n"
        f"💰 Price: ${acc.price_usd} ({acc.price_rub} RUB)\n"
        f"⏱️ Last Activity (CS2): {_date_or_unknown(acc.cs2_stats.last_activity)}\n"
        f"💳 Last Transaction: {escape(acc.last_transaction_date)}\n"
        f"🏷️ Origin: {escape(acc.item_origin.capitalize())}\n"
        f"⏳ Hours (Past 2 Weeks): {acc.steam_stats.hours_played_recently}h\n"
        f"🛡️ Restrictions: Limit: {_flag(acc.steam_stats.is_limited)}"
        f" | Comm Ban: {_flag(acc.steam_stats.community_ban)}"
        f" | Trade Ban: {_flag(acc.steam_stats.trade_ban)}"
        f" | VAC: {vac_bans}\n"
        f"🌟 Seller {escape(acc.seller.username)} Feedback: {reviews_text}\n"
        f"\n"
        f"🎮 CS2 Data:\n"
        f" ├ Prime Status: {prime_status}\n"
        f" ├ Profile Rank: {acc.cs2_stats.profile_rank} level\n"
        f" ├ Premier ELO: {acc.cs2_stats.premier_elo}\n"
        f" ├ Wingman Rank ID: {acc.cs2_stats.wingman_rank_id}\n"
        f" └ Win Count: {acc.cs2_stats.win_count}\n"
        f"\n"
        f"⚙️ Steam Account:\n"
        f" ├ Steam Level: {acc.steam_stats.level}\n"
        f" ├ Registration Date: {_date_or_unknown(acc.steam_stats.register_date)}\n"
        f" ├ Region: {escape(acc.steam_stats.country)}\n"
        f" ├ Total Games: {acc.steam_stats.game_count}\n"
        f" ├ Total Games Value: ${total_games_value:.2f} USD\n"
        f" └ Total Spend: ${total_spend:.2f} USD\n"
        f"\n"
        f"🧾 Purchase History Insights:\n"
        f" ├ Prime Upgrade: {escape(acc.prime_upgrade_info)}\n"
        f" └ Used Payment Methods: {escape(payments)}\n"
        f"\n"
        f"🔗 Link: {MARKET_URL.format(item_id=acc.item_id)}\n"
        f"{'=' * 40}"
    )
