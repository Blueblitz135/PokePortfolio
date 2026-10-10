import asyncio

from app.adapters.justtcg import JustTCGAdapter, RawCardPriceLookup
from app.config import settings


async def main() -> None:
    adapter = JustTCGAdapter(
        api_key=settings.justtcg_api_key,
        usd_to_cad_rate=settings.justtcg_usd_to_cad_rate,
        base_url=settings.justtcg_base_url,
        timeout_seconds=settings.justtcg_timeout_seconds,
    )

    lookup = RawCardPriceLookup(
        name="Umbreon VMAX",
        set_name="Evolving Skies",
        card_number="215",
        set_total="203",
        condition=None,
        grading_company="PSA",
        grade="10",
    )

    result = await adapter.fetch_raw_card_price_history(
        lookup,
        duration="90d",
    )

    if result is None:
        print("JustTCG could not uniquely match the card and grade.")
        return

    print(f"Provider card ID: {result.provider_card_id}")
    print(f"Provider variant ID: {result.provider_variant_id}")
    print(f"Printing: {result.printing}")
    print(f"Currency: {result.currency}")
    print(f"Current price: {result.current_price_cad}")
    print(f"Observed at: {result.current_observed_at}")
    print(f"History points: {len(result.points)}")

    for point in result.points:
        print(f"{point.observed_at}: {point.market_price_per_unit} CAD")


if __name__ == "__main__":
    asyncio.run(main())