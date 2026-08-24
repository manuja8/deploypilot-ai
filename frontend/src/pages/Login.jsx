import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Lock, Mail, Rocket, ShieldCheck } from "lucide-react";

import api from "../services/api";
import loginBackground from "../assets/login-bg.JPG";

function Login() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async (event) => {
    event.preventDefault();

    if (!email || !password) {
      setError("Enter your email and password.");
      return;
    }

    try {
      setLoading(true);
      setError("");

      const response = await api.post("/auth/login", {
        email,
        password,
      });

      localStorage.setItem("token", response.data.access_token);
      localStorage.setItem("displayName", response.data.display_name);
      localStorage.setItem("role", response.data.role);

      navigate("/dashboard");
    } catch (error) {
      setError(error.response?.data?.detail || "Invalid email or password.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <section className="login-panel">
        <div className="login-panel-content">
          <div className="login-brand">
            <div className="login-logo">
              <Rocket size={25} />
            </div>

            <div>
              <strong>DeployPilot AI</strong>
              <span>DevOps Intelligence</span>
            </div>
          </div>

          <div className="login-heading">
            <p className="login-eyebrow">WELCOME BACK</p>
            <h1>Sign in to DeployPilot</h1>
            <p>
              Access pipeline predictions, risk analysis and quality gate
              decisions.
            </p>
          </div>

          <form className="login-form" onSubmit={handleLogin}>
            <label htmlFor="email">Email address</label>

            <div className="input-box">
              <Mail size={18} />
              <input
                id="email"
                type="email"
                placeholder="admin@deploypilot.ai"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                autoComplete="email"
              />
            </div>

            <label htmlFor="password">Password</label>

            <div className="input-box">
              <Lock size={18} />
              <input
                id="password"
                type="password"
                placeholder="Enter your password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                autoComplete="current-password"
              />
            </div>

            {error && <div className="login-error">{error}</div>}

            <button className="login-button" type="submit" disabled={loading}>
              {loading ? "Signing in..." : "Sign in"}
            </button>
          </form>

          <div className="login-security-note">
            <ShieldCheck size={16} />
            <span>Secure access to the DeployPilot AI dashboard</span>
          </div>
        </div>
      </section>

      <section className="login-hero" aria-label="DeployPilot AI">
        <img
          className="login-hero-image"
          src={loginBackground}
          alt="DeployPilot AI CI/CD pipeline failure prediction and risk control system"
        />
      </section>
    </div>
  );
}

export default Login;
