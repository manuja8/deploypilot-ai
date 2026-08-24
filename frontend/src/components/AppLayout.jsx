import { Outlet } from "react-router-dom";

import Header from "./Header";
import Sidebar from "./Sidebar";

function AppLayout() {
  return (
    <div className="app-layout">
      <Sidebar />

      <div className="main-area">
        <Header />

        <main className="page-content">
          <Outlet />
        </main>

        <footer className="app-footer">
          © 2026 DeployPilot AI. CI/CD Pipeline Failure Prediction and Risk
          Control System.
        </footer>
      </div>
    </div>
  );
}

export default AppLayout;
