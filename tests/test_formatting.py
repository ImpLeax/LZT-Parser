from lzt.account import Account
from lzt.formatting import format_account


def test_api_strings_are_html_escaped(listing):
    listing["title"] = "<b>Cheap</b> & fast"
    listing["seller"]["username"] = "a<b"

    text = format_account(Account.from_dict(listing))

    assert "&lt;b&gt;Cheap&lt;/b&gt; &amp; fast" in text
    assert "Seller a&lt;b Feedback" in text
    assert "<b>" not in text


def test_contains_market_link_and_sorted_payment_methods(listing):
    text = format_account(Account.from_dict(listing))

    assert "https://lzt.market/123456/" in text
    assert "Used Payment Methods: PayPal, Visa" in text


def test_unknown_dates_for_minimal_listing():
    text = format_account(Account.from_dict({"item_id": 1}))

    assert "Last Activity (CS2): Unknown" in text
    assert "Registration Date: Unknown" in text
    assert "Used Payment Methods: None" in text
