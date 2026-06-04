import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { apiRequest } from "../api/client";
import { BodyMetric } from "../api/types";
import { useAuth } from "../auth/AuthContext";
import { EmptyState, ErrorState, LoadingState } from "../components/EmptyState";
import { PageHeader } from "../components/PageHeader";

const optionalDecimal = z
  .string()
  .optional()
  .refine((value) => value === undefined || value === "" || (!Number.isNaN(Number(value)) && Number(value) >= 0), {
    message: "Must be a positive number.",
  });

const optionalPositiveDecimal = z
  .string()
  .optional()
  .refine((value) => value === undefined || value === "" || (!Number.isNaN(Number(value)) && Number(value) > 0), {
    message: "Must be greater than 0.",
  });

const optionalInteger = z
  .string()
  .optional()
  .refine((value) => value === undefined || value === "" || (/^\d+$/.test(value) && Number(value) >= 0), {
    message: "Must be a whole number.",
  });

const metricSchema = z.object({
  date: z.string().min(1),
  weight_kg: optionalPositiveDecimal,
  waist_cm: optionalPositiveDecimal,
  steps: optionalInteger,
  protein_g: optionalDecimal,
  calories: optionalInteger,
  nutrition_note: z.string().max(500).optional(),
  sleep_hours: optionalDecimal,
  mood: z.string().max(80).optional(),
});

const nutritionSchema = z.object({
  date: z.string().min(1),
  protein_g: optionalDecimal.refine((value) => value !== undefined && value !== "", {
    message: "Protein is required.",
  }),
  calories: optionalInteger.refine((value) => value !== undefined && value !== "", {
    message: "Calories are required.",
  }),
  nutrition_note: z.string().max(500).optional(),
});

type MetricFormValues = z.infer<typeof metricSchema>;
type NutritionFormValues = z.infer<typeof nutritionSchema>;

function cleanMetric(values: MetricFormValues) {
  return {
    date: values.date,
    weight_kg: values.weight_kg || null,
    waist_cm: values.waist_cm || null,
    steps: values.steps ? Number(values.steps) : null,
    protein_g: values.protein_g || null,
    calories: values.calories ? Number(values.calories) : null,
    nutrition_note: values.nutrition_note || null,
    sleep_hours: values.sleep_hours || null,
    mood: values.mood || null,
  };
}

function cleanNutrition(values: NutritionFormValues) {
  return {
    date: values.date,
    protein_g: values.protein_g,
    calories: Number(values.calories),
    nutrition_note: values.nutrition_note || null,
  };
}

export function ProgressPage() {
  const { token } = useAuth();
  const queryClient = useQueryClient();
  const { data: metrics = [], isLoading, isError } = useQuery({
    queryKey: ["body-metrics"],
    queryFn: () => apiRequest<BodyMetric[]>("/api/v1/body-metrics", { token }),
  });
  const {
    register: registerMetric,
    reset: resetMetric,
    handleSubmit: handleMetricSubmit,
    formState: { errors },
  } = useForm<MetricFormValues>({
    resolver: zodResolver(metricSchema),
    defaultValues: { date: new Date().toISOString().slice(0, 10) },
  });
  const {
    register: registerNutrition,
    reset: resetNutrition,
    handleSubmit: handleNutritionSubmit,
    formState: { errors: nutritionErrors },
  } = useForm<NutritionFormValues>({
    resolver: zodResolver(nutritionSchema),
    defaultValues: { date: new Date().toISOString().slice(0, 10) },
  });
  const createMetric = useMutation({
    mutationFn: (values: MetricFormValues) =>
      apiRequest<BodyMetric>("/api/v1/body-metrics", {
        method: "POST",
        token,
        body: cleanMetric(values),
      }),
    onSuccess: () => {
      resetMetric({ date: new Date().toISOString().slice(0, 10) });
      void queryClient.invalidateQueries({ queryKey: ["body-metrics"] });
      void queryClient.invalidateQueries({ queryKey: ["workout-logs"] });
    },
  });
  const logNutrition = useMutation({
    mutationFn: (values: NutritionFormValues) =>
      apiRequest<BodyMetric>("/api/v1/nutrition/daily", {
        method: "POST",
        token,
        body: cleanNutrition(values),
      }),
    onSuccess: () => {
      resetNutrition({ date: new Date().toISOString().slice(0, 10) });
      void queryClient.invalidateQueries({ queryKey: ["body-metrics"] });
    },
  });

  return (
    <main className="page">
      <PageHeader title="Progress" description="Track body weight, waist, activity, nutrition, sleep, and mood." />
      {isLoading ? <LoadingState label="Loading progress entries..." /> : null}
      {isError ? <ErrorState title="Progress entries unavailable" description="You can still submit a new entry; refresh to retry the table." /> : null}
      <section className="content-grid">
        <form className="panel form-panel" onSubmit={handleNutritionSubmit((values) => logNutrition.mutate(values))}>
          <h2>Quick nutrition</h2>
          <div className="form-grid">
            <label>
              Date
              <input type="date" {...registerNutrition("date")} />
              {nutritionErrors.date ? <span className="field-error">{nutritionErrors.date.message}</span> : null}
            </label>
            <label>
              Protein g
              <input inputMode="decimal" {...registerNutrition("protein_g")} />
              {nutritionErrors.protein_g ? <span className="field-error">{nutritionErrors.protein_g.message}</span> : null}
            </label>
            <label>
              Calories
              <input inputMode="numeric" {...registerNutrition("calories")} />
              {nutritionErrors.calories ? <span className="field-error">{nutritionErrors.calories.message}</span> : null}
            </label>
            <label className="full-field">
              Note
              <input {...registerNutrition("nutrition_note")} />
              {nutritionErrors.nutrition_note ? <span className="field-error">{nutritionErrors.nutrition_note.message}</span> : null}
            </label>
          </div>
          {logNutrition.isError ? <p className="form-error">Could not save nutrition log.</p> : null}
          <button type="submit" disabled={logNutrition.isPending}>
            {logNutrition.isPending ? "Saving..." : "Save nutrition"}
          </button>
        </form>

        <form className="panel form-panel" onSubmit={handleMetricSubmit((values) => createMetric.mutate(values))}>
          <h2>Add metric</h2>
          <div className="form-grid">
            <label>
              Date
              <input type="date" {...registerMetric("date")} />
              {errors.date ? <span className="field-error">{errors.date.message}</span> : null}
            </label>
            <label>
              Weight kg
              <input inputMode="decimal" {...registerMetric("weight_kg")} />
              {errors.weight_kg ? <span className="field-error">{errors.weight_kg.message}</span> : null}
            </label>
            <label>
              Waist cm
              <input inputMode="decimal" {...registerMetric("waist_cm")} />
              {errors.waist_cm ? <span className="field-error">{errors.waist_cm.message}</span> : null}
            </label>
            <label>
              Steps
              <input inputMode="numeric" {...registerMetric("steps")} />
              {errors.steps ? <span className="field-error">{errors.steps.message}</span> : null}
            </label>
            <label>
              Protein g
              <input inputMode="decimal" {...registerMetric("protein_g")} />
              {errors.protein_g ? <span className="field-error">{errors.protein_g.message}</span> : null}
            </label>
            <label>
              Calories
              <input inputMode="numeric" {...registerMetric("calories")} />
              {errors.calories ? <span className="field-error">{errors.calories.message}</span> : null}
            </label>
            <label className="full-field">
              Nutrition note
              <input {...registerMetric("nutrition_note")} />
              {errors.nutrition_note ? <span className="field-error">{errors.nutrition_note.message}</span> : null}
            </label>
            <label>
              Sleep hours
              <input inputMode="decimal" {...registerMetric("sleep_hours")} />
              {errors.sleep_hours ? <span className="field-error">{errors.sleep_hours.message}</span> : null}
            </label>
            <label>
              Mood
              <input {...registerMetric("mood")} />
              {errors.mood ? <span className="field-error">{errors.mood.message}</span> : null}
            </label>
          </div>
          {createMetric.isError ? <p className="form-error">Could not save metric. Check the entered values.</p> : null}
          <button type="submit" disabled={createMetric.isPending}>
            {createMetric.isPending ? "Saving..." : "Save metric"}
          </button>
        </form>

      </section>

      <article className="panel">
        <h2>Recent metrics</h2>
        {metrics.length > 0 ? (
          <table className="data-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Weight kg</th>
                <th>Waist cm</th>
                <th>Steps</th>
                <th>Protein g</th>
                <th>Calories</th>
                <th>Nutrition note</th>
                <th>Sleep h</th>
                <th>Mood</th>
              </tr>
            </thead>
            <tbody>
              {metrics.slice(0, 14).map((metric) => (
                <tr key={metric.id}>
                  <td>{metric.date}</td>
                  <td>{metric.weight_kg ?? "-"}</td>
                  <td>{metric.waist_cm ?? "-"}</td>
                  <td>{metric.steps ?? "-"}</td>
                  <td>{metric.protein_g ?? "-"}</td>
                  <td>{metric.calories ?? "-"}</td>
                  <td>{metric.nutrition_note ?? "-"}</td>
                  <td>{metric.sleep_hours ?? "-"}</td>
                  <td>{metric.mood ?? "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : isLoading ? (
          <LoadingState label="Loading recent metrics..." />
        ) : (
          <EmptyState title="No metrics yet" description="Use quick nutrition or add a full metric entry to start the trend charts." />
        )}
      </article>
    </main>
  );
}
