import type { OffenderRow } from "../api";

type Props = {
  data: OffenderRow[];
  loading: boolean;
  error?: string;
};

export default function Offenders({ data, loading, error }: Props) {
  return (
    <section className="panel panel-table">
      <header className="panel-header">
        <div>
          <p className="panel-label">Shard Violations</p>
          <h2>Ratio penalties</h2>
        </div>
      </header>

      {loading ? (
        <div className="panel-loading">Loading offenders…</div>
      ) : error ? (
        <div className="panel-error">{error}</div>
      ) : (
        <div className="panel-content">
          <table>
            <thead>
              <tr>
                <th>Index</th>
                <th>Size (GB)</th>
                <th>Shards</th>
                <th>GB / shard</th>
                <th>Recommended</th>
              </tr>
            </thead>
            <tbody>
              {data.map((item) => (
                <tr
                  key={item.index}
                  className={item.is_offender ? "row-offender" : ""}
                >
                  <td>{item.index}</td>
                  <td>{item.size_gb.toFixed(2)}</td>
                  <td>{item.shards}</td>
                  <td>{item.ratio.toFixed(2)}</td>
                  <td>{item.recommended_shards}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
