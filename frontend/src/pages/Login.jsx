import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Lock, Mail, Rocket } from "lucide-react";

import api from "../services/api";

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

      navigate("/dashboard");
    } catch {
      setError("Invalid email or password.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-logo">
          <Rocket size={28} />
        </div>

        <h1>DeployPilot AI</h1>

        <p className="login-description">
          CI/CD Failure Prediction and Risk Control System
        </p>

        <form onSubmit={handleLogin}>
          <label>Email address</label>

          <div className="input-box">
            <Mail size={18} />

            <input
              type="email"
              placeholder="admin@deploypilot.ai"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
            />
          </div>

          <label>Password</label>

          <div className="input-box">
            <Lock size={18} />

            <input
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
            />
          </div>

          {error && <div className="login-error">{error}</div>}

          <button className="login-button" disabled={loading}>
            {loading ? "Signing in..." : "Sign in"}
          </button>
        </form>
      </div>
    </div>
  );
}

export default Login;
