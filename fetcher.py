import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List

import requests


def get_data_from_file(file_path: str) -> List[Dict[str, Any]]:
    """Reads index data from a local JSON file."""

    p = Path(file_path)

    # CHECK: Does the file actually exist?
    if not p.exists():
        raise FileNotFoundError(f"The file '{file_path}' was not found.")

    # CHECK: Is the file empty? (0 bytes)
    if p.stat().st_size == 0:
        return []  # Return an empty list so the rest of the app doesn't crash

    # Read and parse JSON
    raw_data = json.loads(p.read_text())

    return raw_data


def get_data_from_server(endpoint: str, days: int) -> List[Dict[str, Any]]:
    """Queries the live API for the last N days and aggregates results."""
    server_records = []
    today = datetime.now(timezone.utc).date()

    for i in range(days):
        date = today - timedelta(days=i)
        # Format date for the API query
        date_query = f"*{date.year:04d}*{date.month:02d}*{date.day:02d}"
        url = f"{endpoint.rstrip('/')}/_cat/indices/{date_query}?v&h=index,pri.store.size,pri&format=json&bytes=b"

        response = requests.get(url, timeout=20)
        response.raise_for_status()
        server_records.extend(response.json())

    return server_records
