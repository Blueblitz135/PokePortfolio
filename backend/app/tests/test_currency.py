from decimal import Decimal

import pytest

from app.services.currency import (
    DEFAULT_CURRENCY,
    SUPPORTED_CURRENCIES,
    UnsupportedCurrencyError,
    convert,
    get_exchange_rate,
    normalize_currency,
    require_normalized_currency,
)


def test_currency_service_supports_cad_without_rounding() -> None:
    amount = Decimal("12.3456")

    assert DEFAULT_CURRENCY == "CAD"
    assert SUPPORTED_CURRENCIES == frozenset({"CAD"})
    assert normalize_currency(" cad ") == "CAD"
    assert require_normalized_currency("cad") == "CAD"
    assert get_exchange_rate("cad") == Decimal("1")
    assert convert(amount, "CAD") == amount


@pytest.mark.parametrize("currency", ["USD", "EUR", ""])
def test_currency_service_rejects_unsupported_currencies(currency: str) -> None:
    with pytest.raises(UnsupportedCurrencyError, match="not supported"):
        convert(Decimal("10.00"), currency)


def test_portfolio_currency_stays_cad_when_conversion_support_expands(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "app.services.currency.SUPPORTED_CURRENCIES",
        frozenset({"CAD", "USD"}),
    )

    with pytest.raises(UnsupportedCurrencyError, match="normalized to CAD"):
        require_normalized_currency("USD")
