import { useEffect, useState } from "react";
import { Brain, CheckCircle2, Clock } from "lucide-react";

import api from "../services/api";

function ModelEvaluation() {
  const [modelStatus, setModelStatus] = useState({});
  const [modelMetrics, setModelMetrics] = useState({});

  useEffect(() => {
    loadModelStatus();
    loadModelMetrics();
  }, []);

  const loadModelStatus = async () => {
    try {
      const response = await api.get("/model-status");

      setModelStatus(response.data);
    } catch (error) {
      console.error("Model status loading failed:", error);
    }
  };

  const loadModelMetrics = async () => {
    try {
      const response = await api.get("/model-metrics");

      setModelMetrics(response.data);
    } catch (error) {
      console.error("Model metrics loading failed:", error);
    }
  };

  const riskMetrics = modelMetrics.failure_risk_metrics;

  const failureMetrics = modelMetrics.failure_type_metrics;

  return (
    <div>
      <div className="page-heading">
        <div>
          <p className="page-label">MODEL PERFORMANCE</p>

          <h1>Model Evaluation</h1>

          <p>
            Review the performance of the two DeployPilot AI machine learning
            models.
          </p>
        </div>
      </div>

      <div className="model-grid">
        <ModelCard
          title="Failure Risk Model"
          algorithm="Random Forest"
          purpose="Predicts PASS or FAIL risk"
          loaded={modelStatus.failure_risk_model_loaded}
        />

        <ModelCard
          title="Failure Type Classifier"
          algorithm="TF-IDF + Logistic Regression"
          purpose="Classifies CI/CD failure type"
          loaded={modelStatus.failure_type_classifier_loaded}
        />
      </div>

      <section className="content-card">
        <div className="card-heading">
          <div>
            <h2>Model 1 Evaluation Metrics</h2>

            <p>Failure Risk Prediction Model</p>
          </div>
        </div>

        <div className="metrics-row">
          <MetricBox
            title="Accuracy"
            value={formatMetric(riskMetrics?.accuracy)}
          />

          <MetricBox
            title="Precision"
            value={formatMetric(riskMetrics?.precision)}
          />

          <MetricBox title="Recall" value={formatMetric(riskMetrics?.recall)} />

          <MetricBox
            title="F1 Score"
            value={formatMetric(riskMetrics?.f1_score)}
          />

          <MetricBox
            title="ROC-AUC"
            value={formatMetric(riskMetrics?.roc_auc)}
          />
        </div>

        <div className="model-note">
          <CheckCircle2 size={18} />

          <div>
            <strong>Model training completed</strong>

            <p>
              Final selected model: {riskMetrics?.model_name || "Random Forest"}
              . These are the real evaluation results from the trained model.
            </p>
          </div>
        </div>
      </section>

      <section className="content-card model-section">
        <div className="card-heading">
          <div>
            <h2>Model 2 Evaluation Metrics</h2>

            <p>Log Failure Type Classification Model</p>
          </div>
        </div>

        <div className="metrics-row">
          <MetricBox
            title="Accuracy"
            value={formatMetric(failureMetrics?.accuracy)}
          />

          <MetricBox
            title="Precision"
            value={formatMetric(failureMetrics?.precision_macro)}
          />

          <MetricBox
            title="Recall"
            value={formatMetric(failureMetrics?.recall_macro)}
          />

          <MetricBox
            title="Macro F1"
            value={formatMetric(failureMetrics?.macro_f1)}
          />

          <MetricBox
            title="Weighted F1"
            value={formatMetric(failureMetrics?.weighted_f1)}
          />
        </div>

        <div className="model-note">
          <Brain size={18} />

          <div>
            <strong>Regex preprocessing is applied before TF-IDF</strong>

            <p>
              Final selected model:{" "}
              {failureMetrics?.model_name || "Logistic Regression"}. The
              classifier predicts 10 CI/CD failure categories.
            </p>
          </div>
        </div>
      </section>

      <section className="content-card model-section">
        <div className="card-heading">
          <div>
            <h2>Why These Metrics Matter</h2>
          </div>
        </div>

        <div className="metric-explanations">
          <MetricExplanation
            name="Accuracy"
            text="Shows how many predictions are correct overall."
          />

          <MetricExplanation
            name="Precision"
            text="Shows how many predicted failures were actually failures."
          />

          <MetricExplanation
            name="Recall"
            text="Shows how many real failures the model successfully detects."
          />

          <MetricExplanation
            name="F1 Score"
            text="Balances precision and recall. It helps evaluate whether risky runs can be detected without unnecessarily blocking safe runs."
          />

          <MetricExplanation
            name="ROC-AUC"
            text="Shows how well the failure risk model separates PASS and FAIL pipeline runs."
          />

          <MetricExplanation
            name="Macro F1"
            text="Gives equal importance to each failure category when evaluating the failure type classifier."
          />
        </div>
      </section>
    </div>
  );
}

function formatMetric(value) {
  if (value === undefined || value === null) {
    return "Pending";
  }

  return `${(value * 100).toFixed(2)}%`;
}

function ModelCard({ title, algorithm, purpose, loaded }) {
  return (
    <section className="content-card model-card">
      <div className="model-icon">
        <Brain size={24} />
      </div>

      <div>
        <h2>{title}</h2>

        <p>{purpose}</p>

        <span className="model-algorithm">{algorithm}</span>
      </div>

      <div className={loaded ? "model-state loaded" : "model-state pending"}>
        {loaded ? (
          <>
            <CheckCircle2 size={15} />
            Loaded
          </>
        ) : (
          <>
            <Clock size={15} />
            Fallback
          </>
        )}
      </div>
    </section>
  );
}

function MetricBox({ title, value }) {
  return (
    <div className="metric-box">
      <span>{title}</span>

      <strong>{value}</strong>
    </div>
  );
}

function MetricExplanation({ name, text }) {
  return (
    <div className="metric-explanation">
      <strong>{name}</strong>

      <p>{text}</p>
    </div>
  );
}

export default ModelEvaluation;
