"""Post-search filters that the LZT Market API cannot apply server-side."""

from .account import Account

SECONDS_PER_YEAR = 365.25 * 24 * 60 * 60


def is_trusted_seller(acc: Account, min_reviews: int, min_positive_percent: float) -> bool:
    return (
        acc.seller.total_reviews >= min_reviews
        and acc.seller.positive_percent >= min_positive_percent
    )


def is_prime_old_enough(acc: Account, min_age_years: float, now: float) -> bool:
    """Accept accounts whose Prime upgrade is older than `min_age_years`.

    A timestamp of 0 means no upgrade was found in the purchase history, which is accepted too.
    """
    if acc.prime_upgrade_timestamp == 0:
        return True
    return acc.prime_upgrade_timestamp < now - min_age_years * SECONDS_PER_YEAR
