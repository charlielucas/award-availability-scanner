# Award Availability Scanner

A small Python project for normalizing and ranking award availability records from provider-style API payloads.

The repository uses synthetic fixture data. It includes no personal itineraries, account information, API keys, or records from a live provider.

## What It Does

- reads a provider-style JSON payload
- expands available cabin classes into individual options
- ranks results by mileage cost, directness, date, and program
- writes a CSV and a short Markdown summary for review
- keeps the provider adapter separate from normalization and ranking logic

## Quick Start

Use Python 3.9 or newer.

```bash
make test
make demo
```

The demo reads [`data/sample_search_response.json`](data/sample_search_response.json) and writes the illustrative outputs in `examples/`.

## API Adapter

`AwardApiClient` is a minimal example of how an authorized API client can fetch a compatible `/search` response. It has no built-in endpoint or credentials. Use it only with a provider you are authorized to access, and follow that provider's terms and rate limits.

## Design Notes

The important boundary in this project is between provider-specific retrieval and the work a person needs to review: normalized options, transparent filters, and ranked outputs. A production version could add provider adapters, retry policies, caching, structured logging, and a richer comparison UI.

