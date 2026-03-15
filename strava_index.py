import argparse
import json
import math
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List

# 'requests' is a third-party library. 
# It must be installed via 'pip install requests' to work.
import requests

# Constants for standardizing calculations
BYTES_IN_GB = 1_000_000_000
GB_PER_SHARD_THRESHOLD = 30.0

# --- HELPER LOGIC ---

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
            
        # converts 'strings' to 'ints' and handle missing keys
        try:
            size = int(record.get("pri.store.size", 0))
            shards = int(record.get("pri", 1))    
        except (ValueError, TypeError):
            size, shards = 0, 1
            
        if base_name not in results:
            results[base_name] = {"index": base_name, "size_bytes": size, "shards": shards}  
        else:
            # Aggregate: sum the size across days, but keep the max shards
            results[base_name]["size_bytes"] += size
            results[base_name]["shards"] = max(results[base_name]["shards"], shards)
        
    return list(results.values())

def get_data_from_file(file_path: str) -> List[Dict[str, Any]]:
    """Reads index data from a local JSON file."""
    p = Path(file_path)
    raw_data = json.loads(p.read_text())
    return aggregate_records(raw_data)

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
          
    return aggregate_records(server_records)

# Print Methods

def print_largest_indexes(data: List[Dict[str, Any]]):
    """Sorts and prints the top 5 indices by GB size."""
    top = sorted(data, key=lambda x: x["size_bytes"], reverse=True)[:5]
    print("--- Top 5 Largest Indexes by Size ---")
    for i, item in enumerate(top, 1):
        gb = item["size_bytes"] / BYTES_IN_GB
        print(f"{i}. {item['index']}: {gb:.2f} GB")
    print()

def print_most_shards(data: List[Dict[str, Any]]):
    """Sorts and prints the top 5 indices by shard count."""
    top = sorted(data, key=lambda x: x["shards"], reverse=True)[:5]
    print("--- Top 5 Largest Indexes by Shard Count ---")
    for i, item in enumerate(top, 1):
        print(f"{i}. {item['index']}: {item['shards']} shards")
    print()
    
def print_least_balanced(data: List[Dict[str, Any]]):
    """Identifies top 5 indices that violate the 1 shard per 30GB rule."""
    stats = []
    for item in data:
        gb = item["size_bytes"] / BYTES_IN_GB
        shards = item["shards"]
        # Ratio Calculation - Handles Zero Division Error
        ratio = gb / shards if shards > 0 else gb
        # Recommended shards: 1 per 30GB, rounded up
        recommended = max(1, math.ceil(gb / GB_PER_SHARD_THRESHOLD))
        
        stats.append({
            "name": item["index"], 
            "gb": gb, 
            "shards": shards, 
            "ratio": ratio, 
            "rec": recommended
        })
        
    # Sort by the ratio (highest offenders first)
    top = sorted(stats, key=lambda x: x["ratio"], reverse=True)[:5]
    print("--- Top 5 Shard Count Offenders ---")
    for i, item in enumerate(top, 1):
        print(f"{i}. {item['name']}")
        print(f"   Size: {item['gb']:.2f} GB | Shards: {item['shards']} | Ratio: {item['ratio']:.2f}")
        print(f"   Recommendation: Change to {item['rec']} shards")
    print()


def main():
    parser = argparse.ArgumentParser(description="Process index data.")
    parser.add_argument("--endpoint", type=str, default="",
                        help="Logging endpoint")
    parser.add_argument("--debug", action="store_true",
                        help="Debug flag used to run locally")
    parser.add_argument("--days", type=int, default=7,
                        help="Number of days of data to parse")
    args = parser.parse_args()

    data = None

    if args.debug:
        try:
            data = get_data_from_file("indexes.json")
        except Exception as err:
            sys.exit("Error reading data from file. Error: " + str(err))
    else:
        try:
            data = get_data_from_server(args.endpoint, args.days)
        except Exception as err:
            sys.exit("Error reading data from API endpoint. Error: " + str(err))

    print_largest_indexes(data)
    print_most_shards(data)
    print_least_balanced(data)

if __name__ == '__main__':
    main()