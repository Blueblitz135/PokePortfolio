# 07 - Currency Strategy

## Default currency

CAD is the default currency across the whole application.

## Internal normalized currency

Market prices should be normalized to CAD before storing or displaying in the main portfolio calculations.

## User display currency

Later, the user can select display currency from a dropdown.

Suggested supported display currencies:

```txt
CAD
USD
EUR
GBP
JPY
```

## Purchase lots

MVP can store purchase lots in CAD by default.

If future support allows users to enter purchases in USD or other currencies:

1. Store original amount and original currency.
2. Convert to CAD using FX rate at time of entry or current rate.
3. Store normalized CAD amount for calculations.

For now, keep it simple:

```txt
purchase_price_per_unit
currency = CAD
```

## External market data

If external listing data returns USD/EUR/etc.:

1. Read original price and currency.
2. Convert to CAD using a live currency conversion API.
3. Store both original and normalized CAD values if useful.
4. Use CAD for market calculations.

## FX caching

Do not call a currency API for every single row.

Cache exchange rates:

- daily for historical/slow-changing use
- hourly if using live listing ingestion

## Suggested service

Create a `currency_service` with functions like:

```python
convert(amount: Decimal, from_currency: str, to_currency: str = "CAD") -> Decimal
get_exchange_rate(from_currency: str, to_currency: str = "CAD") -> Decimal
```

## MVP implementation

Ticket 012 should implement the structure, but it does not need to support every currency from day one.
