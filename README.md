# Strava Take Home: Index Analysis Tool

Hi, I'm Paul. This is my solution for the Strava take-home project.
This script parses index data, analyzes it, and prints out clear stats and recommendations to help teams know when and where to act before things break.

---

## My Decisions

**Size Standard**
Initially, I wasn't sure whether to use 1024³ or 10⁹. After researching the standard for this type of work, I learned that 10⁹ is the accepted convention in these contexts. I used it for the byte-to-GB conversion to ensure the 1:30 shard-to-GB ratio recommendations are consistent with the instructions.

**Data Cleaning**
Logging environments typically generate daily indices with date suffixes — for example, `kubernetes.app.2026-03-14`. I strip those suffixes automatically so that data from multiple days gets grouped under a single base name. This gives a more accurate, aggregated picture of each service rather than treating every day as a separate index.

**Library Choice**
I used `requests` for all API communication instead of Python's built-in `urllib`. It handles timeouts, connection resets, and error responses more reliably — which matters when querying a live cluster that may be under load.

---

## Handling Edge Cases & Assumptions

**Zero & Negative Values**
If an index reports 0 shards (which can happen with a misconfigured or glitchy API response), dividing by zero would crash the program. I handle this with a guard clause: if `shards == 0`, I treat the ratio as the full index size. I also wrap sizes with `max(0, size)` to ignore any negative values a faulty API might return.

**Data Types**
The `_cat` API sometimes returns numeric fields as strings (e.g., `"5"` instead of `5`). I cast these to integers during aggregation so the math works correctly regardless of how the API formats its response.

**Missing Keys**
If a JSON record is missing a `size` or `shard` field entirely, the tool defaults to `0` and `1` respectively. This keeps the program running without crashing and makes the missing data visible in the output rather than silently dropped.

---

## How to Run

### 1. Install Dependencies

The `requests` library is required to run this application. Please install it before running the program.

```bash
pip install requests
```

Or, using the included requirements file:

```bash
pip install -r requirements.txt
```

### 2. Debug Mode (Local File)

To run the analysis against the included `indexes.json` file:

```bash
python strava_index.py --debug
```

### 3. API Mode (Live Data)

To fetch live data from your Elasticsearch cluster:

```bash
python strava_index.py --endpoint <YOUR_API_URL> --days 7
```

The `--days` flag controls how many days of historical data to pull and aggregate. It defaults to 7 if not specified.

---

## What the Script Outputs

The script prints three reports:

1. **Top 5 Largest Indices by Size** — sorted by total GB across all aggregated days
2. **Top 5 Indices by Shard Count** — useful for spotting over-sharded small indices
3. **Top 5 Shard Count Offenders** — indices that violate the 1 shard per 30 GB rule, with a concrete recommendation for how many shards they should have

---

## What I Learned

Working on this gave me a clearer picture of a few things I hadn't thought much about before:

- **The `_cat` API's `&bytes=b` flag** — I didn't realize how important it is to request raw byte counts. Without it, the API returns human-readable strings like `"11.1gb"` that are much harder to parse reliably in a script.
- **GB conversion standards** — I initially debated using 1024³ for the byte-to-GB conversion, but after researching industry standards for logging metrics, I learned that 10⁹ is the preferred decimal standard for this type of reporting.
- **The 30–50 GB shard "sweet spot"** — I gained a better understanding of why this range matters in practice. It was interesting to see how a tool like this can surface both over-sharded indices and under-sharded ones — which mirrors the real world contexts when managing a clusters at scale.

- **`timedelta` for date iteration** — I used Python's `timedelta` to step backwards through the last N days when querying the API, which was also new to me. One cool thing about timedelta is that is that it handles all the edge cases automatically — leap years, month boundaries, and year rollovers — so I didn't have to write any custom date math or worry about days-per-month logic.

---

## File Structure

```
.
├── strava_index.py   # Main script
├── indexes.json      # Sample data for debug mode
├── requirements.txt  # Python dependencies
└── README.md         # This file
```
