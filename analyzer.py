import math
from typing import Any, Dict, List

BYTES_IN_GB = 1_000_000_000
GB_PER_SHARD_THRESHOLD = 30.0


def get_largest_indexes(data: List[Dict[str, Any]], top_n: int = 5) -> List[Dict[str, Any]]:
    """Returns top N indices by GB size."""
    top = sorted(data, key=lambda x: x["size_bytes"], reverse=True)[:top_n]
    result = []
    for item in top:
        gb = item["size_bytes"] / BYTES_IN_GB
        result.append({
            "index": item["index"],
            "size_gb": round(gb, 2),
            "shards": item["shards"]
        })
    return result


def get_most_shards(data: List[Dict[str, Any]], top_n: int = 5) -> List[Dict[str, Any]]:
    """Returns top N indices by shard count."""
    top = sorted(data, key=lambda x: x["shards"], reverse=True)[:top_n]
    result = []
    for item in top:
        result.append({
            "index": item["index"],
            "shards": item["shards"],
            "size_gb": round(item["size_bytes"] / BYTES_IN_GB, 2)
        })
    return result


def get_shard_offenders(data: List[Dict[str, Any]], top_n: int = 5) -> List[Dict[str, Any]]:
    """Identifies top N indices that violate the 1 shard per 30GB rule."""
    stats = []
    for item in data:
        gb = item["size_bytes"] / BYTES_IN_GB
        shards = item["shards"]
        ratio = gb / shards if shards > 0 else gb
        recommended = max(1, math.ceil(gb / GB_PER_SHARD_THRESHOLD))

        stats.append({
            "index": item["index"],
            "size_gb": round(gb, 2),
            "shards": shards,
            "ratio": round(ratio, 2),
            "recommended_shards": recommended,
            "is_offender": ratio > GB_PER_SHARD_THRESHOLD
        })

    # Sort by ratio (highest offenders first)
    top = sorted(stats, key=lambda x: x["ratio"], reverse=True)[:top_n]
    return top
