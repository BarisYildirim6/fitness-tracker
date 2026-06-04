import { Link, Outlet } from "react-router-dom";

export function AuthLayout() {
  return (
    <main className="auth-page">
      <section className="auth-panel">
        <div className="auth-brand">
          <p className="eyebrow">Fitness Tracker</p>
          <h1>Training log for home and gym work.</h1>
        </div>
        <Outlet />
        <p className="auth-footer">
          <Link to="/">Back to app</Link>
        </p>
      </section>
    </main>
  );
}
