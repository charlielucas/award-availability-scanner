"""Command line interface for ranking availability data from a JSON file."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from .ranking import AvailabilityOption, normalize_search_payload, rank_options


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Normalize and rank award availability records from a JSON payload."
    )
    parser.add_argument("--input", required=True, help="Path to a provider-style JSON payload.")
    parser.add_argument("--origin", required=True, help="Origin airport code used for the scan.")
    parser.add_argument("--destination", required=True, help="Destination airport code used for the scan.")
    parser.add_argument("--outdir", default="output", help="Directory for generated CSV and summary files.")
    parser.add_argument("--max-miles", type=int, default=None, help="Exclude options above this mileage cost.")
    parser.add_argument("--direct-only", action="store_true", help="Keep only nonstop options.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    with open(args.input, encoding="utf-8") as handle:
        payload = json.load(handle)

    options = normalize_search_payload(payload, args.origin, args.destination)
    ranked = rank_options(options, max_miles=args.max_miles, direct_only=args.direct_only)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    write_csv(outdir / "ranked_options.csv", ranked)
    write_summary(outdir / "scan_summary.md", args.origin, args.destination, options, ranked)
    print(f"Wrote {outdir / 'ranked_options.csv'} and {outdir / 'scan_summary.md'}")
    return 0


def write_csv(path: Path, options: list[AvailabilityOption]) -> None:
    fields = list(AvailabilityOption.__dataclass_fields__)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(option.to_row() for option in options)


def write_summary(
    path: Path,
    origin: str,
    destination: str,
    options: list[AvailabilityOption],
    ranked: list[AvailabilityOption],
) -> None:
    lines = [
        "# Availability Scan Summary",
        "",
        f"- Route: `{origin.upper()} -> {destination.upper()}`",
        f"- Available cabin options: {len(options)}",
        f"- Ranked options: {len(ranked)}",
        "",
        "## Top Results",
        "",
    ]
    if not ranked:
        lines.append("No options matched the selected filters.")
    else:
        lines.extend(
            f"- {option.miles:,} miles | {option.cabin} | {option.program} | "
            f"{option.date} | {'nonstop' if option.direct else 'connection'}"
            for option in ranked[:5]
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
