import { useState } from "react";
import { ShieldCheck } from "lucide-react";

import api from "../services/api";

function Prediction() {
  const [formData, setFormData] = useState({
    pipeline_id: "model_2_validation",
    run_id: "validation_001",
    source: "MANUAL",
    ci_tool: "GitHub Actions",
    repository: "deploypilot-demo",
    branch: "main",

    commit_size: 68,
    files_changed: 22,
    warnings: 15,
    tests_failed: 0,

    build_duration_sec: 1713,
    test_duration_sec: 922,
    deploy_duration_sec: 0,

    cpu_usage_pct: 47.3,
    memory_usage_mb: 23788,
    retry_count: 3,
    previous_failure_rate: 0.861,

    language: "Python",
    os: "ubuntu-latest",
    cloud_provider: "GitHub Hosted",

    error_log: "",

    quality_gate_enabled: true,
    actual_result: "FAIL",
  });
  // const [formData, setFormData] = useState({
  //   pipeline_id: "manual_001",
  //   run_id: "run_001",
  //   source: "MANUAL",
  //   ci_tool: "GitHub Actions",
  //   repository: "deploypilot-demo",
  //   branch: "main",

  //   commit_size: 40,
  //   files_changed: 12,
  //   warnings: 5,
  //   tests_failed: 3,

  //   build_duration_sec: 400,
  //   test_duration_sec: 240,
  //   deploy_duration_sec: 0,

  //   cpu_usage_pct: 75,
  //   memory_usage_mb: 3200,
  //   retry_count: 1,
  //   previous_failure_rate: 0.4,

  //   language: "Python",
  //   os: "ubuntu-latest",
  //   cloud_provider: "GitHub Hosted",

  //   error_log: "AssertionError expected 200 got 500",

  //   quality_gate_enabled: true,
  //   actual_result: "",
  // });

  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const updateField = (event) => {
    const { name, value, type, checked } = event.target;

    setFormData({
      ...formData,
      [name]: type === "checkbox" ? checked : value,
    });
  };

  const runPrediction = async (event) => {
    event.preventDefault();

    try {
      setLoading(true);
      setError("");

      const response = await api.post("/predict", formData);

      setResult(response.data);
    } catch (error) {
      console.error(error);

      setError("Prediction failed. Check the FastAPI backend.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="page-heading">
        <div>
          <p className="page-label">AI PREDICTION</p>

          <h1>Manual Prediction</h1>

          <p>
            Enter pipeline details to check the failure risk before deployment.
          </p>
        </div>
      </div>

      <div className="prediction-layout">
        <section className="content-card">
          <div className="card-heading">
            <div>
              <h2>Pipeline Details</h2>

              <p>Enter the current CI/CD run information.</p>
            </div>
          </div>

          <form className="prediction-form" onSubmit={runPrediction}>
            <div className="form-grid">
              <Input
                label="Pipeline ID"
                name="pipeline_id"
                value={formData.pipeline_id}
                onChange={updateField}
              />

              <Input
                label="Run ID"
                name="run_id"
                value={formData.run_id}
                onChange={updateField}
              />

              <Input
                label="Repository"
                name="repository"
                value={formData.repository}
                onChange={updateField}
              />

              <Input
                label="Branch"
                name="branch"
                value={formData.branch}
                onChange={updateField}
              />

              <NumberInput
                label="Commit Size"
                name="commit_size"
                value={formData.commit_size}
                onChange={updateField}
              />

              <NumberInput
                label="Files Changed"
                name="files_changed"
                value={formData.files_changed}
                onChange={updateField}
              />

              <NumberInput
                label="Warnings"
                name="warnings"
                value={formData.warnings}
                onChange={updateField}
              />

              <NumberInput
                label="Tests Failed"
                name="tests_failed"
                value={formData.tests_failed}
                onChange={updateField}
              />

              <NumberInput
                label="Build Duration (sec)"
                name="build_duration_sec"
                value={formData.build_duration_sec}
                onChange={updateField}
              />

              <NumberInput
                label="Test Duration (sec)"
                name="test_duration_sec"
                value={formData.test_duration_sec}
                onChange={updateField}
              />

              <NumberInput
                label="CPU Usage %"
                name="cpu_usage_pct"
                value={formData.cpu_usage_pct}
                onChange={updateField}
              />

              <NumberInput
                label="Memory Usage MB"
                name="memory_usage_mb"
                value={formData.memory_usage_mb}
                onChange={updateField}
              />

              <NumberInput
                label="Retry Count"
                name="retry_count"
                value={formData.retry_count}
                onChange={updateField}
              />

              <NumberInput
                label="Previous Failure Rate"
                name="previous_failure_rate"
                value={formData.previous_failure_rate}
                step="0.01"
                onChange={updateField}
              />
            </div>

            <label className="form-label">Error Log</label>

            <textarea
              className="form-textarea"
              name="error_log"
              value={formData.error_log}
              onChange={updateField}
              rows="5"
            />

            <label className="check-row">
              <input
                type="checkbox"
                name="quality_gate_enabled"
                checked={formData.quality_gate_enabled}
                onChange={updateField}
              />
              Enable Quality Gate
            </label>

            {error && <div className="form-error">{error}</div>}

            <button className="primary-button" disabled={loading}>
              {loading ? "Checking pipeline..." : "Run Prediction"}
            </button>
          </form>
        </section>

        <section className="content-card">
          <div className="card-heading">
            <div>
              <h2>Prediction Result</h2>

              <p>Risk decision and recommended action.</p>
            </div>

            <ShieldCheck size={22} />
          </div>

          {!result ? (
            <div className="empty-state">
              <ShieldCheck size={36} />

              <h3>No prediction yet</h3>

              <p>Complete the form and run a prediction.</p>
            </div>
          ) : (
            <PredictionResult result={result} />
          )}
        </section>
      </div>
    </div>
  );
}

function Input({ label, name, value, onChange }) {
  return (
    <div className="form-field">
      <label>{label}</label>

      <input name={name} value={value} onChange={onChange} />
    </div>
  );
}

function NumberInput({ label, name, value, onChange, step = "1" }) {
  return (
    <div className="form-field">
      <label>{label}</label>

      <input
        type="number"
        name={name}
        value={value}
        step={step}
        onChange={onChange}
      />
    </div>
  );
}

function PredictionResult({ result }) {
  return (
    <div className="prediction-result">
      <div className="result-grid">
        <ResultItem label="Prediction" value={result.prediction} />

        <ResultItem
          label="Risk Score"
          value={Number(result.risk_score).toFixed(2)}
        />

        <ResultItem label="Risk Level" value={result.risk_level} />

        <ResultItem label="Gate Action" value={result.quality_gate_action} />
      </div>

      <div className="result-section">
        <span>Failure Type</span>

        <strong>{result.failure_type}</strong>
      </div>

      <div className="result-section">
        <span>Recommendation</span>

        <p>{result.recommendation}</p>
      </div>

      <div className="result-section">
        <span>Preventive Advice</span>

        <p>{result.preventive_advice}</p>
      </div>

      <div className="result-section">
        <span>Quality Gate Explanation</span>

        <p>{result.threshold_explanation}</p>
      </div>

      <div className="result-section">
        <span>Cleaned Log</span>

        <code>{result.cleaned_log_preview || "No error log"}</code>
      </div>
    </div>
  );
}

function ResultItem({ label, value }) {
  return (
    <div className="result-item">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

export default Prediction;
