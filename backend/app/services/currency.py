from decimal import Decimal


DEFAULT_CURRENCY = "CAD"
SUPPORTED_CURRENCIES = frozenset({DEFAULT_CURRENCY})


class UnsupportedCurrencyError(ValueError):
    pass


def normalize_currency(currency: str) -> str:
    normalized_currency = currency.strip().upper()
    if normalized_currency not in SUPPORTED_CURRENCIES:
        supported = ", ".join(sorted(SUPPORTED_CURRENCIES))
        raise UnsupportedCurrencyError(
            f"Currency {currency!r} is not supported. Supported currencies: {supported}."
        )
    return normalized_currency


def require_normalized_currency(currency: str) -> str:
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
    return amount * get_exchange_rate(from_currency, to_currency)
