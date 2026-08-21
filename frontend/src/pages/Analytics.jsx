import { useEffect, useState } from "react";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import api from "../services/api";

function Analytics() {
  const [runs, setRuns] = useState([]);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      const response = await api.get("/history");
      setRuns(response.data);
    } catch (error) {
      console.error("Analytics loading failed:", error);
    }
  };

  const passCount = runs.filter((run) => run.prediction === "PASS").length;

  const failCount = runs.filter((run) => run.prediction === "FAIL").length;

  const predictionData = [
    {
      name: "PASS",
      value: passCount,
      color: "#22c55e",
    },
    {
      name: "FAIL",
      value: failCount,
      color: "#ef4444",
    },
  ];

  const riskData = [
    {
      name: "LOW",
      value: countValue(runs, "risk_level", "LOW"),
    },
    {
      name: "MEDIUM",
      value: countValue(runs, "risk_level", "MEDIUM"),
    },
    {
      name: "HIGH",
      value: countValue(runs, "risk_level", "HIGH"),
    },
  ];

  const actionData = [
    {
      name: "ALLOW",
      value: countValue(runs, "quality_gate_action", "ALLOW"),
    },
    {
      name: "WARN",
      value: countValue(runs, "quality_gate_action", "WARN"),
    },
    {
      name: "BLOCK",
      value: countValue(runs, "quality_gate_action", "BLOCK"),
    },
  ];

  const riskTrend = [...runs].reverse().map((run, index) => ({
    run: index + 1,
    risk: Number(run.risk_score || 0),
    pipeline: run.pipeline_id,
  }));

  const failureData = getFailureTypes(runs);

  return (
    <div>
      <div className="page-heading">
        <div>
          <p className="page-label">PIPELINE ANALYTICS</p>

          <h1>Analytics</h1>

          <p>Review prediction trends and CI/CD risk patterns.</p>
        </div>
      </div>

      <div className="analytics-grid">
        <ChartCard
          title="PASS vs FAIL"
          description="Pipeline prediction results"
        >
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie
                data={predictionData}
                dataKey="value"
                nameKey="name"
                innerRadius={55}
                outerRadius={85}
                paddingAngle={3}
              >
                {predictionData.map((item) => (
                  <Cell key={item.name} fill={item.color} />
                ))}
              </Pie>

              <Tooltip />
            </PieChart>
          </ResponsiveContainer>

          <ChartLegend data={predictionData} />
        </ChartCard>

        <ChartCard title="Risk Levels" description="LOW, MEDIUM and HIGH runs">
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={riskData}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />

              <XAxis dataKey="name" />
              <YAxis allowDecimals={false} />
              <Tooltip />

              <Bar dataKey="value" fill="#2563eb" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard
          title="Quality Gate Decisions"
          description="ALLOW, WARN and BLOCK actions"
        >
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={actionData}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />

              <XAxis dataKey="name" />
              <YAxis allowDecimals={false} />
              <Tooltip />

              <Bar dataKey="value" fill="#8b5cf6" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard
          title="Risk Score Trend"
          description="Risk score across stored runs"
        >
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={riskTrend}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />

              <XAxis dataKey="run" />
              <YAxis domain={[0, 1]} />
              <Tooltip />

              <Line
                type="monotone"
                dataKey="risk"
                stroke="#2563eb"
                strokeWidth={3}
              />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      <section className="content-card analytics-wide">
        <div className="card-heading">
          <div>
            <h2>Failure Type Distribution</h2>

            <p>Failure categories detected in pipeline runs.</p>
          </div>
        </div>

        {failureData.length === 0 ? (
          <div className="empty-state">
            <h3>No failure data yet</h3>

            <p>Failure categories will appear after failed runs.</p>
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={failureData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" horizontal={false} />

              <XAxis type="number" allowDecimals={false} />

              <YAxis dataKey="name" type="category" width={120} />

              <Tooltip />

              <Bar dataKey="value" fill="#f59e0b" radius={[0, 6, 6, 0]} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </section>
    </div>
  );
}

function countValue(runs, field, value) {
  return runs.filter((run) => run[field] === value).length;
}

function getFailureTypes(runs) {
  const counts = {};

  runs.forEach((run) => {
    if (run.failure_type && run.failure_type !== "None") {
      counts[run.failure_type] = (counts[run.failure_type] || 0) + 1;
    }
  });

  return Object.entries(counts).map(([name, value]) => ({
    name,
    value,
  }));
}

function ChartCard({ title, description, children }) {
  return (
    <section className="content-card">
      <div className="card-heading">
        <div>
          <h2>{title}</h2>
          <p>{description}</p>
        </div>
      </div>

      {children}
    </section>
  );
}

function ChartLegend({ data }) {
  return (
    <div className="chart-legend">
      {data.map((item) => (
        <div key={item.name}>
          <span
            className="legend-dot"
            style={{
              background: item.color,
            }}
          />
          {item.name}: {item.value}
        </div>
      ))}
    </div>
  );
}

export default Analytics;
