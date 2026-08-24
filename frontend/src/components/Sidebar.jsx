import {
  BarChart3,
  Brain,
  Gauge,
  GitBranch,
  History,
  LogOut,
  Rocket,
  Users,
  WandSparkles,
} from "lucide-react";

import { useLocation, useNavigate } from "react-router-dom";

function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();
  const role = localStorage.getItem("role") || "USER";
  const isAdmin = role === "ADMIN";

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("displayName");
    localStorage.removeItem("role");

    navigate("/login");
  };

  const menuClass = (path) =>
    location.pathname === path ? "menu-item active" : "menu-item";

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
        <button className={menuClass("/dashboard")} onClick={() => navigate("/dashboard")}>
          <Gauge size={19} />
          Dashboard
        </button>

        <button className={menuClass("/prediction")} onClick={() => navigate("/prediction")}>
          <WandSparkles size={19} />
          Prediction
        </button>

        <button className={menuClass("/history")} onClick={() => navigate("/history")}>
          <History size={19} />
          Pipeline History
        </button>

        <button className={menuClass("/analytics")} onClick={() => navigate("/analytics")}>
          <BarChart3 size={19} />
          Analytics
        </button>

        <button className={menuClass("/models")} onClick={() => navigate("/models")}>
          <Brain size={19} />
          Model Evaluation
        </button>

        <button className={menuClass("/github-runs")} onClick={() => navigate("/github-runs")}>
          <GitBranch size={19} />
          GitHub Runs
        </button>
      </nav>

      {isAdmin && (
        <>
          <p className="menu-title admin-menu-title">ADMINISTRATION</p>

          <nav className="sidebar-menu">
            <button className={menuClass("/users")} onClick={() => navigate("/users")}>
              <Users size={19} />
              User Management
            </button>
          </nav>
        </>
      )}

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
