import pytest

from lzt.account import Account
from lzt.filters import SECONDS_PER_YEAR, is_prime_old_enough, is_trusted_seller

NOW = 2_000_000_000.0


@pytest.fixture
def acc(listing) -> Account:
    return Account.from_dict(listing)


def test_trusted_seller_thresholds(acc):
    assert is_trusted_seller(acc, min_reviews=100, min_positive_percent=90.0)
    assert not is_trusted_seller(acc, min_reviews=106, min_positive_percent=90.0)
    assert not is_trusted_seller(acc, min_reviews=100, min_positive_percent=95.3)


def test_missing_prime_upgrade_is_accepted(acc):
    acc.prime_upgrade_timestamp = 0
    assert is_prime_old_enough(acc, min_age_years=10, now=NOW)


def test_prime_upgrade_age_boundary(acc):
    cutoff = NOW - 10 * SECONDS_PER_YEAR

    acc.prime_upgrade_timestamp = int(cutoff) - 1
    assert is_prime_old_enough(acc, min_age_years=10, now=NOW)

    acc.prime_upgrade_timestamp = int(cutoff) + 1
    assert not is_prime_old_enough(acc, min_age_years=10, now=NOW)
