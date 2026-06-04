import { createBrowserRouter, Navigate } from "react-router-dom";

import { AppLayout } from "./components/AppLayout";
import { AuthLayout } from "./components/AuthLayout";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { ActiveWorkoutPage } from "./pages/ActiveWorkoutPage";
import { DashboardPage } from "./pages/DashboardPage";
import { ExerciseLibraryPage } from "./pages/ExerciseLibraryPage";
import { ExerciseDetailPage } from "./pages/ExerciseDetailPage";
import { LoginPage } from "./pages/LoginPage";
import { OnboardingProfilePage } from "./pages/OnboardingProfilePage";
import { ProgressPage } from "./pages/ProgressPage";
import { RegisterPage } from "./pages/RegisterPage";
import { SettingsPage } from "./pages/SettingsPage";
import { WeeklyPlanPage } from "./pages/WeeklyPlanPage";

export const router = createBrowserRouter([
  {
    element: <AuthLayout />,
    children: [
      { path: "/login", element: <LoginPage /> },
      { path: "/register", element: <RegisterPage /> },
    ],
  },
  {
    element: <ProtectedRoute />,
    children: [
      { path: "/onboarding", element: <OnboardingProfilePage /> },
      {
        element: <AppLayout />,
        children: [
          { path: "/", element: <DashboardPage /> },
          { path: "/weekly-plan", element: <WeeklyPlanPage /> },
          { path: "/active-workout", element: <ActiveWorkoutPage /> },
          { path: "/exercises", element: <ExerciseLibraryPage /> },
          { path: "/exercises/:exerciseId", element: <ExerciseDetailPage /> },
          { path: "/progress", element: <ProgressPage /> },
          { path: "/settings", element: <SettingsPage /> },
        ],
      },
    ],
  },
  { path: "*", element: <Navigate to="/" replace /> },
]);
