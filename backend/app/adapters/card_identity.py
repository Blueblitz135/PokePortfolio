"""Normalize known catalog formatting without using fuzzy price matches."""

import re


def normalized(value: object) -> str:
    return " ".join(str(value or "").casefold().replace("_", " ").split())


def card_name_matches(provider: object, local: str) -> bool:
    # Catalog art labels are redundant only when set and collector number match.
    def base(value: object) -> str:
        return re.sub(
            r"\s*\((?:alternate art secret|alternate full art|full art|secret|rainbow)\)$",
            "", normalized(value),
        )
    return base(provider) == base(local)


def set_name_matches(provider: object, local: str) -> bool:
    def base(value: object) -> str:
        return re.sub(r"^(?:swsh|sv|sm|xy)\d+\s*:\s*", "", normalized(value))
    return base(provider) == base(local)


def card_number_matches(provider: object, number: str, total: str | None) -> bool:
    def part(value: str) -> str:
        value = normalized(value)
        return str(int(value)) if value.isdigit() else value
    parts = str(provider or "").split("/")
    if len(parts) > 2 or part(parts[0]) != part(number):
        return False
    return not total or len(parts) == 1 or part(parts[1]) == part(total)
