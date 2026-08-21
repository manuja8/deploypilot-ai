import { useEffect, useState } from "react";
import { Activity, CircleCheck, Database } from "lucide-react";

import api from "../services/api";
import StatCard from "../components/StatCard";

function Dashboard() {
  const [history, setHistory] = useState([]);
  const [apiOnline, setApiOnline] = useState(false);
  const [models, setModels] = useState({});

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const historyResponse = await api.get("/history");
      setHistory(historyResponse.data);

      const healthResponse = await api.get("/health");

      if (healthResponse.data.status === "healthy") {
        setApiOnline(true);
      }

      const modelResponse = await api.get("/model-status");
      setModels(modelResponse.data);
    } catch (error) {
      console.error("Dashboard loading failed:", error);
    }
  };

  const totalRuns = history.length;

  const failedRuns = history.filter(
    (item) => item.prediction === "FAIL",
  ).length;

  const blockedRuns = history.filter(
    (item) => item.quality_gate_action === "BLOCK",
  ).length;

  const failRate = totalRuns === 0 ? 0 : (failedRuns / totalRuns) * 100;

  const averageRisk =
    totalRuns === 0
      ? 0
      : history.reduce(
          (total, item) => total + Number(item.risk_score || 0),
          0,
        ) / totalRuns;

  return (
    <div>
      <div className="page-heading">
        <div>
          <p className="page-label">OVERVIEW</p>

          <h1>Dashboard</h1>

          <p>Monitor pipeline risk, predictions and quality gate decisions.</p>
        </div>

        <div className="live-status">
          <span className={apiOnline ? "online-dot" : "offline-dot"} />

          {apiOnline ? "System Online" : "System Offline"}
        </div>
      </div>

      <div className="stats-grid">
        <StatCard
          title="Total Runs"
          value={totalRuns}
          note="Pipeline predictions"
          type="green"
        />

        <StatCard
          title="Fail Rate"
          value={`${failRate.toFixed(1)}%`}
          note="Predicted failures"
          type="red"
        />

        <StatCard
          title="Average Risk"
          value={averageRisk.toFixed(2)}
          note="Mean failure score"
          type="orange"
        />

        <StatCard
          title="Blocked Runs"
          value={blockedRuns}
          note="Quality gate blocks"
          type="purple"
        />
      </div>

      <div className="dashboard-grid">
        <section className="content-card">
          <div className="card-heading">
            <div>
              <h2>Recent Pipeline Runs</h2>

              <p>Latest predictions stored in the database.</p>
            </div>
          </div>

          {history.length === 0 ? (
            <div className="empty-state">
              <Database size={34} />

              <h3>No pipeline runs yet</h3>

              <p>Prediction history will appear here.</p>
            </div>
          ) : (
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>Pipeline</th>
                    <th>Branch</th>
                    <th>Prediction</th>
                    <th>Risk</th>
                    <th>Action</th>
                  </tr>
                </thead>

                <tbody>
                  {history.slice(0, 6).map((item) => (
                    <tr key={item.id}>
                      <td>{item.pipeline_id || "-"}</td>

                      <td>{item.branch || "-"}</td>

                      <td>
                        <span
                          className={
                            item.prediction === "FAIL"
                              ? "status fail"
                              : "status pass"
                          }
                        >
                          {item.prediction}
                        </span>
                      </td>

                      <td>{Number(item.risk_score || 0).toFixed(2)}</td>

                      <td>
                        <span
                          className={`status ${
                            item.quality_gate_action?.toLowerCase() || "allow"
                          }`}
                        >
                          {item.quality_gate_action}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>

        <section className="content-card">
          <div className="card-heading">
            <div>
              <h2>System Health</h2>

              <p>Current DeployPilot AI components.</p>
            </div>

            <Activity size={21} />
          </div>

          <div className="health-list">
            <div className="health-row">
              <div>
                <CircleCheck size={19} />
                FastAPI Backend
              </div>

              <span className={apiOnline ? "health-ok" : "health-bad"}>
                {apiOnline ? "Online" : "Offline"}
              </span>
            </div>

            <div className="health-row">
              <div>
                <Database size={19} />
                Database
              </div>

              <span className="health-ok">Connected</span>
            </div>

            <div className="health-row">
              <div>
                <CircleCheck size={19} />
                Failure Risk Model
              </div>

              <span className="health-wait">
                {models.failure_risk_model_loaded ? "Loaded" : "Fallback"}
              </span>
            </div>

            <div className="health-row">
              <div>
                <CircleCheck size={19} />
                Failure Type Model
              </div>

              <span className="health-wait">
                {models.failure_type_classifier_loaded ? "Loaded" : "Fallback"}
              </span>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}

export default Dashboard;
