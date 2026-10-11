import json
from typing import Any

import pytest


@pytest.fixture
def listing() -> dict[str, Any]:
    """A trimmed LZT Market `/steam` item with the fields the bot reads."""
    return {
        "item_id": 123456,
        "title": "Prime account",
        "price": 12.5,
        "rub_price": 1100,
        "item_origin": "brute",
        "published_date": 1_700_000_000,
        "view_count": 10,
        "email_provider": "other",
        "feedback_data": json.dumps(
            {
                "1": {"positive": 90, "negative": 5},
                "2": {"positive": 10, "negative": 0},
            }
        ),
        "seller": {"user_id": 1, "username": "seller", "sold_items_count": 50},
        "steam_country": "Germany",
        "steam_register_date": 1_400_000_000,
        "steam_full_games": {"list": {"730": {"is_paid": 1}}},
        "steamTransactions": [
            {"date": 1_690_000_000, "product": "Some Game", "source": "Visa ****1234 9.99€"},
            {
                "date": 1_450_000_000,
                "product": "Prime Status Upgrade",
                "source": "PayPal\t14.99$",
            },
        ],
    }
