import {
  BarChart3,
  Brain,
  Gauge,
  GitBranch,
  History,
  LogOut,
  Rocket,
  WandSparkles,
} from "lucide-react";

import { useLocation, useNavigate } from "react-router-dom";

function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("displayName");

    navigate("/login");
  };

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="sidebar-logo">
          <Rocket size={22} />
        </div>

        <div>
          <strong>DeployPilot AI</strong>
          <span>DevOps Intelligence</span>
        </div>
      </div>

      <p className="menu-title">WORKSPACE</p>

      <nav className="sidebar-menu">
        <button
          className={
            location.pathname === "/dashboard"
              ? "menu-item active"
              : "menu-item"
          }
          onClick={() => navigate("/dashboard")}
        >
          <Gauge size={19} />
          Dashboard
        </button>

        <button
          className={
            location.pathname === "/prediction"
              ? "menu-item active"
              : "menu-item"
          }
          onClick={() => navigate("/prediction")}
        >
          <WandSparkles size={19} />
          Prediction
        </button>

        <button
          className={
            location.pathname === "/history" ? "menu-item active" : "menu-item"
          }
          onClick={() => navigate("/history")}
        >
          <History size={19} />
          Pipeline History
        </button>

        <button
          className={
            location.pathname === "/analytics"
              ? "menu-item active"
              : "menu-item"
          }
          onClick={() => navigate("/analytics")}
        >
          <BarChart3 size={19} />
          Analytics
        </button>

        <button
          className={
            location.pathname === "/models" ? "menu-item active" : "menu-item"
          }
          onClick={() => navigate("/models")}
        >
          <Brain size={19} />
          Model Evaluation
        </button>

        <button
          className={
            location.pathname === "/github-runs"
              ? "menu-item active"
              : "menu-item"
          }
          onClick={() => navigate("/github-runs")}
        >
          <GitBranch size={19} />
          GitHub Runs
        </button>
      </nav>

      <div className="sidebar-bottom">
        <button className="menu-item logout-item" onClick={logout}>
          <LogOut size={19} />
          Logout
        </button>
      </div>
    </aside>
  );
}

export default Sidebar;
