import { useEffect, useMemo, useState } from "react";
import "./App.css";
import { fetchLargestIndexes, fetchShardCounts, fetchOffenders } from "./api";
import type { LargestIndex, ShardCountRow, OffenderRow } from "./api";
import LargestIndexes from "./components/LargestIndexes";
import ShardCount from "./components/ShardCount";
import Offenders from "./components/Offenders";

type LoadingState = {
  largest: boolean;
  shards: boolean;
  offenders: boolean;
};

type ErrorState = {
  largest?: string;
  shards?: string;
  offenders?: string;
};

function App() {
  const [debug, setDebug] = useState(true);
  const [lastRefreshed, setLastRefreshed] = useState<string>("Never");
  const [apiWarning, setApiWarning] = useState<string | undefined>(undefined);
  const [largest, setLargest] = useState<LargestIndex[]>([]);
  const [shards, setShards] = useState<ShardCountRow[]>([]);
  const [offenders, setOffenders] = useState<OffenderRow[]>([]);
  const [loading, setLoading] = useState<LoadingState>({
    largest: false,
    shards: false,
    offenders: false,
  });
  const [errors, setErrors] = useState<ErrorState>({});

  const modeLabel = debug ? "Debug" : "Live";

  const refreshAll = async (currentDebug = debug) => {
    setLoading({ largest: true, shards: true, offenders: true });
    setErrors({});

    const requests = await Promise.allSettled([
      fetchLargestIndexes(currentDebug),
      fetchShardCounts(currentDebug),
      fetchOffenders(currentDebug),
    ]);

    const nextErrors: ErrorState = {};
    const warnings = new Set<string>();

    if (requests[0].status === "fulfilled") {
      setLargest(requests[0].value.data);
      if (requests[0].value.warning) warnings.add(requests[0].value.warning);
    } else {
      nextErrors.largest =
        requests[0].reason?.message ?? "Unable to load largest indexes";
      setLargest([]);
    }

    if (requests[1].status === "fulfilled") {
      setShards(requests[1].value.data);
      if (requests[1].value.warning) warnings.add(requests[1].value.warning);
    } else {
      nextErrors.shards =
        requests[1].reason?.message ?? "Unable to load shard counts";
      setShards([]);
    }

    if (requests[2].status === "fulfilled") {
      setOffenders(requests[2].value.data);
      if (requests[2].value.warning) warnings.add(requests[2].value.warning);
    } else {
      nextErrors.offenders =
        requests[2].reason?.message ?? "Unable to load offenders";
      setOffenders([]);
    }

    setErrors(nextErrors);
    setApiWarning(warnings.size ? [...warnings].join(" ") : undefined);
    setLoading({ largest: false, shards: false, offenders: false });
    setLastRefreshed(new Date().toLocaleString());
  };

  useEffect(() => {
    refreshAll(debug);
  }, [debug]);

  const summary = useMemo(() => {
    return {
      totalTopSize: largest.reduce((sum, item) => sum + item.size_gb, 0),
      totalTopShards: shards.reduce((sum, item) => sum + item.shards, 0),
      offendersCount: offenders.length,
    };
  }, [largest, shards, offenders]);

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Strava Index Metrics</p>
          <h1>Index sizing, shard usage, and offender trends</h1>
        </div>
        <div className="topbar-actions">
          <div className="mode-chip">Mode: {modeLabel}</div>
          <button
            className="ghost-button"
            onClick={() => setDebug((value) => !value)}
          >
            Toggle {debug ? "Live" : "Debug"}
          </button>
          <button className="primary-button" onClick={() => refreshAll(debug)}>
            Refresh
          </button>
        </div>
      </header>

      <section className="status-bar">
        <div>
          <p>Last refreshed</p>
          <strong>{lastRefreshed}</strong>
        </div>
        <div>
          <p>Data mode</p>
          <strong>{modeLabel}</strong>
        </div>
        <div>
          <p>Summary</p>
          <strong>
            {summary.totalTopSize.toFixed(2)} GB · {summary.totalTopShards}{" "}
            shards · {summary.offendersCount} offenders
          </strong>
        </div>
      </section>

      {apiWarning ? <div className="api-warning">{apiWarning}</div> : null}

      <main className="dashboard-grid">
        <LargestIndexes
          data={largest}
          loading={loading.largest}
          error={errors.largest}
        />
        <ShardCount
          data={shards}
          loading={loading.shards}
          error={errors.shards}
        />
        <Offenders
          data={offenders}
          loading={loading.offenders}
          error={errors.offenders}
        />
      </main>
    </div>
  );
}

export default App;
