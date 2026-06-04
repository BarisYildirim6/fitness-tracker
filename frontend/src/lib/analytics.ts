import { BodyMetric, WorkoutLog } from "../api/types";

export type DashboardAnalytics = {
  latestWeight: number | null;
  sevenDayAverageWeight: number | null;
  latestWaist: number | null;
  todayProtein: number | null;
  todayCalories: number | null;
  weeklyWorkoutCount: number;
  weeklyAverageSteps: number | null;
  weeklyAverageProtein: number | null;
  bodyweightTrend: Array<{ date: string; weight: number }>;
  waistTrend: Array<{ date: string; waist: number }>;
  weeklyTrainingVolume: Array<{ week: string; volume: number }>;
};

function numberOrNull(value: string | number | null | undefined): number | null {
  if (value === null || value === undefined || value === "") {
    return null;
  }
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

function dateFromMetric(value: string) {
  return new Date(`${value}T00:00:00`);
}

function startOfWeek(value: Date) {
  const date = new Date(value);
  date.setHours(0, 0, 0, 0);
  const day = date.getDay();
  const diff = day === 0 ? -6 : 1 - day;
  date.setDate(date.getDate() + diff);
  return date;
}

function formatDate(value: Date) {
  return value.toISOString().slice(0, 10);
}

function formatLocalDate(value: Date) {
  const year = value.getFullYear();
  const month = String(value.getMonth() + 1).padStart(2, "0");
  const day = String(value.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function average(values: number[]) {
  if (values.length === 0) {
    return null;
  }
  return values.reduce((total, value) => total + value, 0) / values.length;
}

function sameOrAfter(left: Date, right: Date) {
  return left.getTime() >= right.getTime();
}

function sameOrBefore(left: Date, right: Date) {
  return left.getTime() <= right.getTime();
}

export function calculateDashboardAnalytics(metrics: BodyMetric[], workoutLogs: WorkoutLog[]): DashboardAnalytics {
  const metricsByDateAscending = [...metrics].sort((left, right) => left.date.localeCompare(right.date));
  const metricsByDateDescending = [...metricsByDateAscending].reverse();
  const latestMetricWithWeight = metricsByDateDescending.find((metric) => metric.weight_kg !== null);
  const latestMetricWithWaist = metricsByDateDescending.find((metric) => metric.waist_cm !== null);
  const todayMetric = metricsByDateDescending.find((metric) => metric.date === formatLocalDate(new Date()));

  const latestMetricDate = metricsByDateDescending[0]?.date;
  const currentWeekStart = startOfWeek(latestMetricDate ? dateFromMetric(latestMetricDate) : new Date());
  const currentWeekEnd = new Date(currentWeekStart);
  currentWeekEnd.setDate(currentWeekEnd.getDate() + 6);
  currentWeekEnd.setHours(23, 59, 59, 999);

  const sevenDayWeightWindowEnd = latestMetricWithWeight ? dateFromMetric(latestMetricWithWeight.date) : null;
  const sevenDayWeightWindowStart = sevenDayWeightWindowEnd ? new Date(sevenDayWeightWindowEnd) : null;
  sevenDayWeightWindowStart?.setDate(sevenDayWeightWindowStart.getDate() - 6);
  const sevenDayWeights =
    sevenDayWeightWindowStart && sevenDayWeightWindowEnd
      ? metricsByDateAscending
          .filter((metric) => metric.weight_kg !== null)
          .filter((metric) => {
            const metricDate = dateFromMetric(metric.date);
            return sameOrAfter(metricDate, sevenDayWeightWindowStart) && sameOrBefore(metricDate, sevenDayWeightWindowEnd);
          })
          .map((metric) => numberOrNull(metric.weight_kg))
          .filter((value): value is number => value !== null)
      : [];

  const currentWeekMetrics = metricsByDateAscending.filter((metric) => {
    const metricDate = dateFromMetric(metric.date);
    return sameOrAfter(metricDate, currentWeekStart) && sameOrBefore(metricDate, currentWeekEnd);
  });

  const currentWeekLogs = workoutLogs.filter((log) => {
    const startedAt = new Date(log.started_at);
    return sameOrAfter(startedAt, currentWeekStart) && sameOrBefore(startedAt, currentWeekEnd);
  });

  const volumeByWeek = new Map<string, number>();
  workoutLogs.forEach((log) => {
    const week = formatDate(startOfWeek(new Date(log.started_at)));
    const volume = log.set_logs.reduce((total, setLog) => {
      const weight = numberOrNull(setLog.weight_kg) ?? 0;
      return total + weight * setLog.reps;
    }, 0);
    volumeByWeek.set(week, (volumeByWeek.get(week) ?? 0) + volume);
  });

  return {
    latestWeight: numberOrNull(latestMetricWithWeight?.weight_kg),
    sevenDayAverageWeight: sevenDayWeights.length >= 7 ? average(sevenDayWeights) : null,
    latestWaist: numberOrNull(latestMetricWithWaist?.waist_cm),
    todayProtein: numberOrNull(todayMetric?.protein_g),
    todayCalories: numberOrNull(todayMetric?.calories),
    weeklyWorkoutCount: currentWeekLogs.length,
    weeklyAverageSteps: average(
      currentWeekMetrics.map((metric) => metric.steps).filter((value): value is number => value !== null),
    ),
    weeklyAverageProtein: average(
      currentWeekMetrics.map((metric) => numberOrNull(metric.protein_g)).filter((value): value is number => value !== null),
    ),
    bodyweightTrend: metricsByDateAscending
      .map((metric) => ({ date: metric.date, weight: numberOrNull(metric.weight_kg) }))
      .filter((point): point is { date: string; weight: number } => point.weight !== null)
      .slice(-30),
    waistTrend: metricsByDateAscending
      .map((metric) => ({ date: metric.date, waist: numberOrNull(metric.waist_cm) }))
      .filter((point): point is { date: string; waist: number } => point.waist !== null)
      .slice(-30),
    weeklyTrainingVolume: [...volumeByWeek.entries()]
      .sort(([left], [right]) => left.localeCompare(right))
      .map(([week, volume]) => ({ week, volume }))
      .slice(-12),
  };
}

export function formatNumber(value: number | null, digits = 1) {
  return value === null ? "-" : value.toFixed(digits);
}
