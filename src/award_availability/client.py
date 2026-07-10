"""Minimal HTTP client for providers that expose a compatible search API."""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
from typing import Any


class AwardApiClient:
    """Fetch paginated availability data using caller-supplied credentials.

    This client intentionally has no provider-specific default endpoint or
    credentials. A provider adapter can point it at an authorized endpoint and
    map the response into the format consumed by ``normalize_search_payload``.
    """

    def __init__(self, base_url: str, api_key: str, user_agent: str = "award-availability-scanner/1.0"):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.user_agent = user_agent

    def search(self, params: dict[str, str], timeout: int = 30) -> dict[str, Any]:
        query = urllib.parse.urlencode(params)
        request = urllib.request.Request(
            f"{self.base_url}/search?{query}",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "application/json",
                "User-Agent": self.user_agent,
            },
        )
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read())
