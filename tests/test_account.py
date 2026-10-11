from datetime import datetime

from lzt.account import Account, _extract_payment_words


def test_feedback_is_aggregated_across_categories(listing):
    acc = Account.from_dict(listing)

    assert acc.seller.positive_reviews == 100
    assert acc.seller.negative_reviews == 5
    assert acc.seller.total_reviews == 105
    assert acc.seller.positive_percent == 95.2


def test_feedback_accepts_decoded_dict_and_ignores_garbage(listing):
    listing["feedback_data"] = {"1": {"positive": 3, "negative": 1}}
    assert Account.from_dict(listing).seller.total_reviews == 4

    listing["feedback_data"] = "not json"
    assert Account.from_dict(listing).seller.total_reviews == 0


def test_prime_upgrade_is_parsed_from_transactions(listing):
    acc = Account.from_dict(listing)

    expected_date = datetime.fromtimestamp(1_450_000_000).strftime("%Y-%m-%d")
    assert acc.prime_upgrade_timestamp == 1_450_000_000
    assert acc.prime_upgrade_info == f"{expected_date} (via PayPal)"
    assert acc.is_prime is True


def test_payment_methods_are_collected_from_all_transactions(listing):
    acc = Account.from_dict(listing)

    assert acc.unique_payment_methods == {"Visa", "PayPal"}


def test_last_transaction_date_uses_first_entry(listing):
    acc = Account.from_dict(listing)

    assert acc.last_transaction_date == datetime.fromtimestamp(1_690_000_000).strftime("%Y-%m-%d")


def test_minimal_listing_uses_defaults():
    acc = Account.from_dict({"item_id": 1, "steam_full_games": []})

    assert acc.is_prime is False
    assert acc.seller.username == "Unknown"
    assert acc.prime_upgrade_timestamp == 0
    assert acc.prime_upgrade_info == "Not found in history"
    assert acc.last_transaction_date == "Unknown"
    assert acc.unique_payment_methods == set()


def test_extract_payment_words_drops_amounts_masks_and_short_tokens():
    assert _extract_payment_words("Visa ****1234\t9.99€ on 12") == ["Visa"]
    assert _extract_payment_words("") == []
