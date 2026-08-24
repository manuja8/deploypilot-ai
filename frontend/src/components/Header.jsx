import { Bell } from "lucide-react";

function Header() {
  const displayName = localStorage.getItem("displayName") || "DeployPilot User";
  const role = localStorage.getItem("role") || "USER";

  return (
    <header className="app-header">
      <div>
        <h3>DeployPilot AI</h3>
        <span>CI/CD Failure Prediction and Risk Control</span>
      </div>

      <div className="header-user">
        <button className="icon-button" type="button" aria-label="Notifications">
          <Bell size={18} />
        </button>

        <div className="user-avatar">{displayName.charAt(0).toUpperCase()}</div>

        <div>
          <strong>{displayName}</strong>
          <small>{role === "ADMIN" ? "Administrator" : "User"}</small>
        </div>
      </div>
    </header>
  );
}

export default Header;
