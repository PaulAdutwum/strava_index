from typing import Any, Dict, List


def aggregate_records(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Cleans and groups the raw data.
    1. Strips date suffixes so indices from different days group together.
    2. Converts string numbers from JSON into actual integers for math.
    3. Handles potential missing data/errors gracefully.
    """
    results = {}
    for record in records:
        raw_name = record.get("index", "")
        if not raw_name:
            continue

        # Strip date suffix (e.g., kubernetes.app.2025-04-10 -> kubernetes.app)
        parts = raw_name.split(".")
        if len(parts) > 1 and parts[-1].startswith("20"):
            base_name = ".".join(parts[:-1])
        else:
            base_name = raw_name

        # Convert strings to ints and handle missing keys
        try:
            size = int(record.get("pri.store.size", 0))
            shards = int(record.get("pri", 1))
        except (ValueError, TypeError):
            size, shards = 0, 1

        if base_name not in results:
            results[base_name] = {"index": base_name, "size_bytes": size, "shards": shards}
        else:
            # Aggregate: sum the size across days, keep max shards
            results[base_name]["size_bytes"] += size
            results[base_name]["shards"] = max(results[base_name]["shards"], shards)

    return list(results.values())
