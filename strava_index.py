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
    # results take in index as key 
    # values in resutls are the stats which is also a dictionaray 
    # key: index name, value: dictionary containing stats for that index
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
            # converts if conversion fails like null value or value type,
            # set size to 0 to to avoide interfering with other indices
            # set shards to 1 to to avoide zero division later during ratio calculation
        except (ValueError, TypeError):
            size, shards = 0, 1
            
        if base_name not in results:
            results[base_name] = {"index": base_name, "size_bytes": size, "shards": shards}  
        else:
            # Aggregate: sum the size across days because size is commulative, 
            # but keep the max shards because shards are container units not commulative
            results[base_name]["size_bytes"] += size
            results[base_name]["shards"] = max(results[base_name]["shards"], shards)
        # why return list, because we can sort list by size or shards
        # later but we cannot sort a dictionary that way
    return list(results.values())

def get_data_from_file(file_path: str) -> List[Dict[str, Any]]:
    """Reads index data from a local JSON file."""
    
    #CHECK: Does the file actually exist?
    if not p.exists():
        print(f"ERROR: The file '{file_path}' was not found.")
        sys.exit(1) # Exit gracefully rather than crashing with a Traceback

    #  CHECK: Is the file empty? (0 bytes)
    if p.stat().st_size == 0:
        print(f"ERROR: The file '{file_path}' is empty.")
        return [] # Return an empty list so the rest of the app doesn't crash
    
    # 1. Create a Path object from the string (e.g., "indexes.json")
    # This object works across Windows/Mac/Linux automatically.
    p = Path(file_path)
    
    #  p.read_text() opens the file, reads the contents into a string, and closes it.
    #  json.loads() takes that string from RAM and parses it into a Python List.
    raw_data = json.loads(p.read_text())
    
    # Pass the raw list into our aggregator to clean suffixes and sum sizes.
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
    
def print_average(data: List[Dict[str, Any]]):
    """Sorts and prints the top 5 indices by GB size."""
    top = sorted(data, key=lambda x: x["size_bytes"], reverse=True)[:5]
    print("--- Top 5 Average ---")
    total_gb = 0.0
    for i, item in enumerate(top, 1):
        gb = item["size_bytes"] / BYTES_IN_GB
        total_gb += gb
    average = total_gb / 5 
    print(average)
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
    print_average(data)

if __name__ == '__main__':
    main()
    
    

#python strava_index.py --endpoint https://api.logs.strava.com --days 7

#python strava_index.py --debug