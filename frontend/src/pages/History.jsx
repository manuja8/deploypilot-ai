import { useEffect, useState } from "react";

import api from "../services/api";

function History() {
  const [runs, setRuns] = useState([]);
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("ALL");

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const response = await api.get("/history");
      setRuns(response.data);
    } catch (error) {
      console.error("History loading failed:", error);
    }
  };

  const filteredRuns = runs.filter((run) => {
    const text = search.toLowerCase();

    const matchesSearch =
      run.pipeline_id?.toLowerCase().includes(text) ||
      run.repository?.toLowerCase().includes(text) ||
      run.branch?.toLowerCase().includes(text) ||
      run.failure_type?.toLowerCase().includes(text);

    const matchesStatus = status === "ALL" || run.prediction === status;

    return matchesSearch && matchesStatus;
  });

  return (
    <div>
      <div className="page-heading">
        <div>
          <p className="page-label">PIPELINE RECORDS</p>

          <h1>Pipeline History</h1>

          <p>Review previous predictions and quality gate decisions.</p>
        </div>
      </div>

      <section className="content-card">
        <div className="history-toolbar">
          <input
            className="history-search"
            placeholder="Search pipeline, repository, branch..."
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />

          <select
            className="history-filter"
            value={status}
            onChange={(event) => setStatus(event.target.value)}
          >
            <option value="ALL">All Predictions</option>

            <option value="PASS">PASS</option>

            <option value="FAIL">FAIL</option>
          </select>
        </div>

        {filteredRuns.length === 0 ? (
          <div className="empty-state">
            <h3>No matching pipeline runs</h3>

            <p>Try changing the search or filter.</p>
          </div>
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Pipeline</th>
                  <th>Source</th>
                  <th>Repository</th>
                  <th>Branch</th>
                  <th>Prediction</th>
                  <th>Risk</th>
                  <th>Failure Type</th>
                  <th>Action</th>
                </tr>
              </thead>

              <tbody>
                {filteredRuns.map((run) => (
                  <tr key={run.id}>
                    <td>{formatDate(run.timestamp)}</td>

                    <td>{run.pipeline_id || "-"}</td>

                    <td>{run.source || "MANUAL"}</td>

                    <td>{run.repository || "-"}</td>

                    <td>{run.branch || "-"}</td>

                    <td>
                      <StatusBadge value={run.prediction} />
                    </td>

                    <td>{Number(run.risk_score || 0).toFixed(2)}</td>

                    <td>{run.failure_type || "None"}</td>

                    <td>
                      <StatusBadge value={run.quality_gate_action} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}

function StatusBadge({ value }) {
  const type = value?.toLowerCase() || "allow";

  return <span className={`status ${type}`}>{value || "-"}</span>;
}

function formatDate(value) {
  if (!value) {
    return "-";
  }

  return new Date(value).toLocaleString();
}

export default History;
