import { useEffect, useState } from "react";
import {
  Activity,
  Eye,
  GitBranch,
  Lightbulb,
  ShieldCheck,
  X,
} from "lucide-react";

import api from "../services/api";

function GitHubRuns() {
  const [runs, setRuns] = useState([]);
  const [selectedRun, setSelectedRun] = useState(null);

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

          <p>
            Live pipeline predictions, quality gate decisions and
            recommendations received from GitHub Actions.
          </p>
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

            <p>
              Open a run to review its risk, gate mode and DeployPilot advice.
            </p>
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
                  <th>Details</th>
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

                    <td>{displayFailureType(run)}</td>

                    <td>
                      <StatusBadge value={run.quality_gate_action} />
                    </td>

                    <td>
                      <button
                        className="details-button"
                        type="button"
                        onClick={() => setSelectedRun(run)}
                      >
                        <Eye size={15} />
                        View
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {selectedRun && (
        <RunDetails run={selectedRun} onClose={() => setSelectedRun(null)} />
      )}
    </div>
  );
}

function RunDetails({ run, onClose }) {
  const hasFailureLog =
    String(run.actual_result || "").toUpperCase() === "FAIL" &&
    Boolean(run.cleaned_log);

  return (
    <div
      className="run-details-overlay"
      role="presentation"
      onMouseDown={onClose}
    >
      <section
        className="run-details-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="run-details-title"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <div className="run-details-header">
          <div>
            <p className="page-label">LIVE PIPELINE DETAILS</p>

            <h2 id="run-details-title">
              {run.pipeline_id || "GitHub Actions Run"}
            </h2>

            <p>
              {run.repository || "-"} · {run.branch || "-"} · Run{" "}
              {run.run_id || "-"}
            </p>
          </div>

          <button
            className="icon-button"
            type="button"
            aria-label="Close run details"
            onClick={onClose}
          >
            <X size={20} />
          </button>
        </div>

        <div className="run-details-body">
          <div className="run-detail-grid">
            <DetailItem
              label="Actual CI Result"
              value={<StatusBadge value={run.actual_result || "-"} />}
            />

            <DetailItem
              label="ML Prediction"
              value={<StatusBadge value={run.prediction} />}
            />

            <DetailItem
              label="Risk Score"
              value={Number(run.risk_score || 0).toFixed(4)}
            />

            <DetailItem
              label="Risk Level"
              value={<StatusBadge value={run.risk_level} />}
            />

            <DetailItem label="Failure Type" value={displayFailureType(run)} />

            <DetailItem
              label="Quality Gate"
              value={<StatusBadge value={run.quality_gate_action} />}
            />

            <DetailItem label="Gate Mode" value={displayGateMode(run)} />

            <DetailItem label="Cold Start" value={displayColdStart(run)} />
          </div>

          <section className="run-detail-section">
            <div className="run-detail-section-title">
              <Activity size={18} />
              <h3>Repository & Pipeline Context</h3>
            </div>

            <div className="run-context-grid">
              <ContextItem label="Repository" value={run.repository || "-"} />
              <ContextItem label="Branch" value={run.branch || "-"} />
              <ContextItem label="Run ID" value={run.run_id || "-"} />
              <ContextItem
                label="Meaningful History Runs"
                value={
                  run.gate_mode
                    ? (run.meaningful_history_runs ?? 0)
                    : "Not recorded"
                }
              />
              <ContextItem
                label="Previous Failure Rate Used"
                value={formatRate(run.previous_failure_rate)}
              />
              <ContextItem label="Recorded" value={formatDate(run.timestamp)} />
            </div>
          </section>

          <div className="run-advice-grid">
            <AdviceCard
              icon={<Lightbulb size={19} />}
              title="Recommendation"
              text={
                run.recommendation ||
                "No recommendation was recorded for this run."
              }
            />

            <AdviceCard
              icon={<ShieldCheck size={19} />}
              title="Preventive Advice"
              text={
                run.preventive_advice ||
                "No preventive advice was recorded for this run."
              }
            />
          </div>

          <section className="run-detail-section">
            <div className="run-detail-section-title">
              <Activity size={18} />
              <h3>Real Pipeline Metrics</h3>
            </div>

            <div className="pipeline-metrics-grid">
              <Metric label="Commit Size" value={run.commit_size} />
              <Metric label="Files Changed" value={run.files_changed} />
              <Metric label="Warnings" value={run.warnings} />
              <Metric label="Tests Failed" value={run.tests_failed} />
              <Metric
                label="Build Duration"
                value={formatSeconds(run.build_duration_sec)}
              />
              <Metric
                label="Test Duration"
                value={formatSeconds(run.test_duration_sec)}
              />
              <Metric
                label="Deploy Duration"
                value={formatSeconds(run.deploy_duration_sec)}
              />
              <Metric
                label="CPU Usage"
                value={formatNumber(run.cpu_usage_pct, "%")}
              />
              <Metric
                label="Memory Usage"
                value={formatNumber(run.memory_usage_mb, " MB")}
              />
              <Metric label="Retry Count" value={run.retry_count} />
            </div>
          </section>

          <section className="run-detail-section">
            <div className="run-detail-section-title">
              <ShieldCheck size={18} />
              <h3>Quality Gate Explanation</h3>
            </div>

            <p className="run-detail-text">
              {run.threshold_explanation ||
                "No threshold explanation was recorded."}
            </p>
          </section>

          {hasFailureLog && (
            <section className="run-detail-section">
              <div className="run-detail-section-title">
                <Activity size={18} />
                <h3>Cleaned Failure Log</h3>
              </div>

              <pre className="run-log-preview">
                {String(run.cleaned_log).slice(-2500)}
              </pre>
            </section>
          )}
        </div>
      </section>
    </div>
  );
}

function DetailItem({ label, value }) {
  return (
    <div className="run-detail-item">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function ContextItem({ label, value }) {
  return (
    <div className="run-context-item">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function AdviceCard({ icon, title, text }) {
  return (
    <div className="run-advice-card">
      <div>
        {icon}
        <strong>{title}</strong>
      </div>

      <p>{text}</p>
    </div>
  );
}

function Metric({ label, value }) {
  return (
    <div className="pipeline-metric">
      <span>{label}</span>
      <strong>{value ?? 0}</strong>
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

function displayFailureType(run) {
  const actualResult = String(run.actual_result || "").toUpperCase();
  const failureType = String(run.failure_type || "").trim();

  if (actualResult === "PASS") {
    return "N/A - no CI failure";
  }

  if (!failureType || failureType.toLowerCase() === "none") {
    return "N/A";
  }

  return failureType;
}

function displayGateMode(run) {
  if (!run.gate_mode) {
    return "Not recorded";
  }

  return run.gate_mode === "ADVISORY" ? "ADVISORY - cold start" : run.gate_mode;
}

function displayColdStart(run) {
  if (!run.gate_mode) {
    return "Not recorded";
  }

  return run.cold_start ? "Yes" : "No";
}

function formatDate(value) {
  if (!value) {
    return "-";
  }

  return new Date(value).toLocaleString();
}

function formatRate(value) {
  const number = Number(value);

  if (Number.isNaN(number)) {
    return "-";
  }

  return `${(number * 100).toFixed(1)}%`;
}

function formatSeconds(value) {
  const number = Number(value || 0);

  return `${number.toFixed(1)} s`;
}

function formatNumber(value, suffix) {
  const number = Number(value || 0);

  return `${number.toFixed(2)}${suffix}`;
}

export default GitHubRuns;
