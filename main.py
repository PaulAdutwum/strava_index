import os
from typing import List, Optional, Tuple

import requests
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from aggregator import aggregate_records
from analyzer import get_largest_indexes, get_most_shards, get_shard_offenders
from fetcher import get_data_from_file, get_data_from_server

app = FastAPI(title="Strava Index Analyzer", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
DEFAULT_ENDPOINT = os.getenv("STRAVA_ENDPOINT", "https://api.logs.strava.com")
DEFAULT_DAYS = int(os.getenv("STRAVA_DAYS", "7"))


def get_data(debug: bool = False) -> Tuple[List[dict], Optional[str]]:
    """Fetch and aggregate data based on debug mode, with a fallback to local JSON."""
    if debug:
        raw_data = get_data_from_file("indexes.json")
        return aggregate_records(raw_data), "Loaded local indexes.json in debug mode."

    try:
        raw_data = get_data_from_server(DEFAULT_ENDPOINT, DEFAULT_DAYS)
        return aggregate_records(raw_data), None
    except requests.RequestException as err:
        raw_data = get_data_from_file("indexes.json")
        warning = (
            "Live API request failed; falling back to local indexes.json. "
            f"Error: {err}"
        )
        return aggregate_records(raw_data), warning


def build_response(result: list, warning: Optional[str] = None) -> dict:
    response = {"data": result}
    if warning:
        response["warning"] = warning
    return response


@app.get("/api/largest")
async def get_largest(debug: bool = Query(False, description="Use debug mode with local indexes.json")):
    """Get top 5 largest indexes by size."""
    try:
        data, warning = get_data(debug)
        return build_response(get_largest_indexes(data), warning)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/shards")
async def get_shards(debug: bool = Query(False, description="Use debug mode with local indexes.json")):
    """Get top 5 indexes by shard count."""
    try:
        data, warning = get_data(debug)
        return build_response(get_most_shards(data), warning)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/offenders")
async def get_offenders(debug: bool = Query(False, description="Use debug mode with local indexes.json")):
    """Get top 5 shard count offenders."""
    try:
        data, warning = get_data(debug)
        return build_response(get_shard_offenders(data), warning)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """Simple root message describing available API endpoints."""
    return {
        "message": "Strava Index Analyzer API",
        "endpoints": ["/api/largest", "/api/shards", "/api/offenders", "/health"]
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
