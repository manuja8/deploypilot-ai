import { useEffect, useState } from "react";
import { GitBranch } from "lucide-react";

import api from "../services/api";

function GitHubRuns() {
  const [runs, setRuns] = useState([]);

  useEffect(() => {
    loadRuns();
  }, []);

  const loadRuns = async () => {
    try {
      const response = await api.get("/history");

      const githubRuns = response.data.filter(
        (run) => run.source === "GITHUB_ACTIONS",
      );

      setRuns(githubRuns);
    } catch (error) {
      console.error("GitHub runs loading failed:", error);
    }
  };

  return (
    <div>
      <div className="page-heading">
        <div>
          <p className="page-label">CI/CD INTEGRATION</p>

          <h1>GitHub Runs</h1>

          <p>Pipeline predictions received from GitHub Actions.</p>
        </div>
      </div>

      <div className="github-summary">
        <SummaryBox label="GitHub Runs" value={runs.length} />

        <SummaryBox label="Blocked" value={countAction(runs, "BLOCK")} />

        <SummaryBox label="Allowed" value={countAction(runs, "ALLOW")} />

        <SummaryBox label="Warnings" value={countAction(runs, "WARN")} />
      </div>

      <section className="content-card">
        <div className="card-heading">
          <div>
            <h2>GitHub Action Predictions</h2>

            <p>Runs saved through the GitHub prediction endpoint.</p>
          </div>

          <GitBranch size={22} />
        </div>

        {runs.length === 0 ? (
          <div className="empty-state">
            <GitBranch size={34} />

            <h3>No GitHub runs yet</h3>

            <p>GitHub Actions predictions will appear here.</p>
          </div>
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Pipeline</th>
                  <th>Repository</th>
                  <th>Branch</th>
                  <th>Prediction</th>
                  <th>Risk</th>
                  <th>Failure Type</th>
                  <th>Action</th>
                </tr>
              </thead>

              <tbody>
                {runs.map((run) => (
                  <tr key={run.id}>
                    <td>{formatDate(run.timestamp)}</td>

                    <td>{run.pipeline_id || "-"}</td>

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

function countAction(runs, action) {
  return runs.filter((run) => run.quality_gate_action === action).length;
}

function SummaryBox({ label, value }) {
  return (
    <div className="github-summary-box">
      <span>{label}</span>
      <strong>{value}</strong>
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

export default GitHubRuns;
