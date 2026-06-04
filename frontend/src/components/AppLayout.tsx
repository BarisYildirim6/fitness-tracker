import { NavLink, Navigate, Outlet } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";

const navItems = [
  { to: "/", label: "Dashboard" },
  { to: "/weekly-plan", label: "Weekly Plan" },
  { to: "/active-workout", label: "Active Workout" },
  { to: "/exercises", label: "Exercise Library" },
  { to: "/progress", label: "Progress" },
  { to: "/settings", label: "Settings" },
];

export function AppLayout() {
  const { user, logout } = useAuth();

  if (user && !user.profile) {
    return <Navigate to="/onboarding" replace />;
  }

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="sidebar-header">
          <p className="eyebrow">Fitness Tracker</p>
          <strong>Home/Gym MVP</strong>
        </div>
        <nav className="sidebar-nav" aria-label="Primary navigation">
          {navItems.map((item) => (
            <NavLink key={item.to} to={item.to} end={item.to === "/"}>
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>

      <div className="app-main">
        <header className="top-nav">
          <div>
            <span className="muted">Signed in as</span>
            <strong>{user?.email}</strong>
          </div>
          <button type="button" className="secondary-button" onClick={logout}>
            Log out
          </button>
        </header>
        <Outlet />
      </div>
    </div>
  );
}
