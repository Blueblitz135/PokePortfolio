"""Centralize currency validation and the MVP's CAD-only conversion contract."""

from decimal import Decimal


DEFAULT_CURRENCY = "CAD"
SUPPORTED_CURRENCIES = frozenset({DEFAULT_CURRENCY})


class UnsupportedCurrencyError(ValueError):
    """Raised when data is not in a supported normalized currency."""

    pass


def normalize_currency(currency: str) -> str:
    """Normalize casing/whitespace and reject currencies outside MVP support."""

    normalized_currency = currency.strip().upper()
    if normalized_currency not in SUPPORTED_CURRENCIES:
        supported = ", ".join(sorted(SUPPORTED_CURRENCIES))
        raise UnsupportedCurrencyError(
            f"Currency {currency!r} is not supported. Supported currencies: {supported}."
        )
    return normalized_currency


def require_normalized_currency(currency: str) -> str:
    """Require the internal portfolio currency used by financial calculations."""

    normalized_currency = normalize_currency(currency)
    if normalized_currency != DEFAULT_CURRENCY:
        raise UnsupportedCurrencyError(
            "Portfolio calculations require values normalized to "
            f"{DEFAULT_CURRENCY}; received {normalized_currency}."
        )
    return normalized_currency


def get_exchange_rate(
    from_currency: str, to_currency: str = DEFAULT_CURRENCY
) -> Decimal:
    """Return an exact supported rate; currently only same-currency CAD is valid."""

    source_currency = normalize_currency(from_currency)
    target_currency = normalize_currency(to_currency)

    if source_currency == target_currency:
        return Decimal("1")

    raise UnsupportedCurrencyError(
        f"Conversion from {source_currency} to {target_currency} is not supported."
    )


def convert(
    amount: Decimal, from_currency: str, to_currency: str = DEFAULT_CURRENCY
) -> Decimal:
    """Convert an amount with the supported exchange-rate lookup."""

    return amount * get_exchange_rate(from_currency, to_currency)
