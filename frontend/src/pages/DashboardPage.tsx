import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  Bar,
  BarChart,
} from "recharts";

import { apiRequest } from "../api/client";
import { BodyMetric, Program, WorkoutLog } from "../api/types";
import { useAuth } from "../auth/AuthContext";
import { EmptyState, ErrorState, LoadingState } from "../components/EmptyState";
import { PageHeader } from "../components/PageHeader";
import { calculateDashboardAnalytics, formatNumber } from "../lib/analytics";

export function DashboardPage() {
  const { token, user } = useAuth();
  const {
    data: program,
    isLoading: programLoading,
    isError: programError,
  } = useQuery({
    queryKey: ["active-program"],
    queryFn: () => apiRequest<Program>("/api/v1/programs/active", { token }),
    retry: false,
  });
  const {
    data: metrics = [],
    isLoading: metricsLoading,
    isError: metricsError,
  } = useQuery({
    queryKey: ["body-metrics", "latest"],
    queryFn: () => apiRequest<BodyMetric[]>("/api/v1/body-metrics", { token }),
  });
  const {
    data: workoutLogs = [],
    isLoading: logsLoading,
    isError: logsError,
  } = useQuery({
    queryKey: ["workout-logs", "latest"],
    queryFn: () => apiRequest<WorkoutLog[]>("/api/v1/workout-logs", { token }),
  });

  const analytics = calculateDashboardAnalytics(metrics, workoutLogs);
  const proteinTarget = user?.profile?.target_protein_g ? Number(user.profile.target_protein_g) : null;
  const calorieTarget = user?.profile?.target_calories ?? null;
  const proteinProgress =
    proteinTarget && analytics.todayProtein !== null ? Math.min(100, (analytics.todayProtein / proteinTarget) * 100) : null;
  const dashboardLoading = programLoading || metricsLoading || logsLoading;
  const dashboardError = metricsError || logsError;

  return (
    <main className="page">
      <PageHeader
        title="Dashboard"
        description="Overview of profile, active plan, workout logging, and body metrics."
      />
      {dashboardLoading ? <LoadingState label="Loading dashboard data..." /> : null}
      {dashboardError ? <ErrorState title="Dashboard data unavailable" description="The API is running, but one of the dashboard requests failed." /> : null}

      <section className="summary-grid">
        <article className="summary-card">
          <span>Latest weight</span>
          <strong>{analytics.latestWeight === null ? "-" : `${formatNumber(analytics.latestWeight)} kg`}</strong>
        </article>
        <article className="summary-card">
          <span>7-day avg weight</span>
          <strong>
            {analytics.sevenDayAverageWeight === null ? "Need 7 entries" : `${formatNumber(analytics.sevenDayAverageWeight)} kg`}
          </strong>
        </article>
        <article className="summary-card">
          <span>Latest waist</span>
          <strong>{analytics.latestWaist === null ? "-" : `${formatNumber(analytics.latestWaist)} cm`}</strong>
        </article>
        <article className="summary-card">
          <span>Protein today</span>
          <strong>
            {analytics.todayProtein === null
              ? "-"
              : proteinTarget
                ? `${formatNumber(analytics.todayProtein, 0)} / ${formatNumber(proteinTarget, 0)} g`
                : `${formatNumber(analytics.todayProtein, 0)} g`}
          </strong>
          {proteinProgress !== null ? (
            <div className="target-progress" aria-label="Daily protein progress">
              <span style={{ width: `${proteinProgress}%` }} />
            </div>
          ) : null}
        </article>
        <article className="summary-card">
          <span>Calories today</span>
          <strong>
            {analytics.todayCalories === null
              ? "-"
              : calorieTarget
                ? `${formatNumber(analytics.todayCalories, 0)} / ${calorieTarget}`
                : formatNumber(analytics.todayCalories, 0)}
          </strong>
        </article>
        <article className="summary-card">
          <span>Weekly workouts</span>
          <strong>{analytics.weeklyWorkoutCount}</strong>
        </article>
        <article className="summary-card">
          <span>Avg steps this week</span>
          <strong>{analytics.weeklyAverageSteps === null ? "-" : formatNumber(analytics.weeklyAverageSteps, 0)}</strong>
        </article>
        <article className="summary-card">
          <span>Avg protein this week</span>
          <strong>{analytics.weeklyAverageProtein === null ? "-" : `${formatNumber(analytics.weeklyAverageProtein, 0)} g`}</strong>
        </article>
        <article className="summary-card">
          <span>Mode</span>
          <strong>{user?.profile?.preferred_mode ?? "Not set"}</strong>
        </article>
        <article className="summary-card">
          <span>Active plan</span>
          <strong>{program?.name ?? "None"}</strong>
        </article>
      </section>

      <section className="chart-grid">
        <article className="panel chart-panel">
          <h2>Bodyweight trend</h2>
          {analytics.bodyweightTrend.length > 0 ? (
            <ResponsiveContainer width="100%" height={260}>
              <LineChart data={analytics.bodyweightTrend}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                <YAxis domain={["dataMin - 1", "dataMax + 1"]} width={44} />
                <Tooltip />
                <Line type="monotone" dataKey="weight" stroke="#185b50" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <EmptyState title="No weight data yet" description="Add seven daily metrics to unlock the weekly average and trend." actionHref="/progress" actionLabel="Add progress" />
          )}
        </article>

        <article className="panel chart-panel">
          <h2>Waist trend</h2>
          {analytics.waistTrend.length > 0 ? (
            <ResponsiveContainer width="100%" height={260}>
              <LineChart data={analytics.waistTrend}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                <YAxis domain={["dataMin - 1", "dataMax + 1"]} width={44} />
                <Tooltip />
                <Line type="monotone" dataKey="waist" stroke="#9a3d2b" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <EmptyState title="No waist data yet" description="Waist entries will appear here once logged from Progress." actionHref="/progress" actionLabel="Add progress" />
          )}
        </article>

        <article className="panel chart-panel chart-panel-wide">
          <h2>Weekly training volume</h2>
          {analytics.weeklyTrainingVolume.length > 0 ? (
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={analytics.weeklyTrainingVolume}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="week" tick={{ fontSize: 12 }} />
                <YAxis width={56} />
                <Tooltip />
                <Bar dataKey="volume" fill="#185b50" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <EmptyState title="No logged volume yet" description="Log a workout with weights to populate this chart." actionHref="/active-workout" actionLabel="Start workout" />
          )}
        </article>
      </section>

      <section className="content-grid">
        <article className="panel">
          <h2>This week</h2>
          {program ? (
            <ul className="plain-list">
              {program.workout_days.map((day) => (
                <li key={day.id}>
                  <Link to="/weekly-plan">{day.title}</Link>
                  <span>{day.focus}</span>
                </li>
              ))}
            </ul>
          ) : programError ? (
            <ErrorState title="No active plan found" description="Run the seed script to load the default home workout plan." />
          ) : (
            <EmptyState title="No active plan" description="Run the seed script to load the default home workout plan." />
          )}
        </article>

        <article className="panel">
          <h2>Recent body metrics</h2>
          {metrics.length > 0 ? (
            <ul className="plain-list">
              {metrics.slice(0, 5).map((metric) => (
                <li key={metric.id}>
                  <span>{metric.date}</span>
                  <strong>{metric.weight_kg ? `${metric.weight_kg} kg` : "No weight"}</strong>
                </li>
              ))}
            </ul>
          ) : (
            <EmptyState title="No metrics yet" description="Add weight, waist, nutrition, or activity metrics from Progress." actionHref="/progress" actionLabel="Add progress" />
          )}
        </article>
      </section>
    </main>
  );
}
