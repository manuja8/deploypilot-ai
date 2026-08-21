import { Bell } from "lucide-react";

function Header() {
  const displayName = localStorage.getItem("displayName") || "DeployPilot User";

  return (
    <header className="app-header">
      <div>
        <h3>DeployPilot AI</h3>

        <span>CI/CD Failure Prediction and Risk Control</span>
      </div>

      <div className="header-user">
        <button className="icon-button">
          <Bell size={18} />
        </button>

        <div className="user-avatar">{displayName.charAt(0)}</div>

        <div>
          <strong>{displayName}</strong>
          <small>Administrator</small>
        </div>
      </div>
    </header>
  );
}

export default Header;
