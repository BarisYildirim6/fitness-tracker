import { Navigate, Outlet, useLocation } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";

export function ProtectedRoute() {
  const { isLoading, user } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return <div className="page-loader">Loading...</div>;
  }

  if (!user) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return <Outlet />;
}
