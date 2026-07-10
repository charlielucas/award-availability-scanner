"""Normalize provider-style availability records into reviewable options."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable


@dataclass(frozen=True)
class AvailabilityOption:
    record_id: str
    route_id: str
    origin: str
    destination: str
    date: str
    program: str
    cabin: str
    miles: int
    direct: bool
    seats: int | None
    taxes: float | None
    currency: str

    def to_row(self) -> dict[str, Any]:
        return asdict(self)


def normalize_search_payload(
    payload: dict[str, Any], origin: str, destination: str
) -> list[AvailabilityOption]:
    """Turn a small provider-style payload into one row per available cabin.

    The expected input is intentionally simple and documented in
    ``data/sample_search_response.json``. Adapters for a specific provider can
    translate their response into this shape without changing the ranking code.
    """

    options: list[AvailabilityOption] = []
    for record in payload.get("data", []):
        for cabin, details in (record.get("cabins") or {}).items():
            if details.get("available") is not True:
                continue
            miles = _as_positive_int(details.get("miles"))
            if miles is None:
                continue
            options.append(
                AvailabilityOption(
                    record_id=str(record.get("id") or "unknown"),
                    route_id=str(record.get("route_id") or "unknown"),
                    origin=origin.upper(),
                    destination=destination.upper(),
                    date=str(record.get("date") or ""),
                    program=str(record.get("program") or "unknown"),
                    cabin=cabin,
                    miles=miles,
                    direct=bool(details.get("direct")),
                    seats=_as_nonnegative_int(details.get("seats")),
                    taxes=_as_nonnegative_float(details.get("taxes")),
                    currency=str(record.get("currency") or "USD"),
                )
            )
    return options


def rank_options(
    options: Iterable[AvailabilityOption],
    *,
    max_miles: int | None = None,
    direct_only: bool = False,
) -> list[AvailabilityOption]:
    """Filter options and rank by miles, directness, date, then program."""

    ranked = list(options)
    if max_miles is not None:
        ranked = [option for option in ranked if option.miles <= max_miles]
    if direct_only:
        ranked = [option for option in ranked if option.direct]
    return sorted(
        ranked,
        key=lambda option: (
            option.miles,
            not option.direct,
            option.date,
            option.program.lower(),
        ),
    )


def _as_positive_int(value: Any) -> int | None:
    try:
        converted = int(value)
    except (TypeError, ValueError):
        return None
    return converted if converted > 0 else None


def _as_nonnegative_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        converted = int(value)
    except (TypeError, ValueError):
        return None
    return converted if converted >= 0 else None


def _as_nonnegative_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        converted = float(value)
    except (TypeError, ValueError):
        return None
    return converted if converted >= 0 else None
