import { useEffect, useState } from "react";
import { Brain, CheckCircle2, Clock } from "lucide-react";

import api from "../services/api";

function ModelEvaluation() {
  const [modelStatus, setModelStatus] = useState({});

  useEffect(() => {
    loadModelStatus();
  }, []);

  const loadModelStatus = async () => {
    try {
      const response = await api.get("/model-status");

      setModelStatus(response.data);
    } catch (error) {
      console.error("Model status loading failed:", error);
    }
  };

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
          <MetricBox title="Accuracy" value="Pending" />

          <MetricBox title="Precision" value="Pending" />

          <MetricBox title="Recall" value="Pending" />

          <MetricBox title="F1 Score" value="Pending" />

          <MetricBox title="ROC-AUC" value="Pending" />
        </div>

        <div className="model-note">
          <Clock size={18} />

          <div>
            <strong>Model training is still pending</strong>

            <p>
              These values will be replaced with real evaluation results after
              the Failure Risk Model is trained.
            </p>
          </div>
        </div>
      </section>

      <section className="content-card model-section">
        <div className="card-heading">
          <div>
            <h2>Model 2 Evaluation</h2>

            <p>Log Failure Type Classification Model</p>
          </div>
        </div>

        <div className="metrics-row">
          <MetricBox title="Macro F1" value="Pending" />

          <MetricBox title="Weighted F1" value="Pending" />

          <MetricBox title="Classes" value="10" />
        </div>

        <div className="model-note">
          <Brain size={18} />

          <div>
            <strong>Regex preprocessing will be applied before TF-IDF</strong>

            <p>
              This directly addresses the lecturer's recommendation about noisy
              CI/CD logs.
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
            text="Balances precision and recall. It helps evaluate whether the quality gate detects risky builds without unnecessarily blocking safe builds."
          />

          <MetricExplanation
            name="ROC-AUC"
            text="Shows how well Model 1 separates high-risk and low-risk pipeline runs."
          />
        </div>
      </section>
    </div>
  );
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
