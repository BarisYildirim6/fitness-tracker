import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { FormEvent, useEffect, useMemo, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";

import { apiRequest } from "../api/client";
import {
  ExerciseOverride,
  Program,
  ProgressionSuggestion,
  WorkoutDay,
  WorkoutDayWithProgression,
  WorkoutExercise,
  WorkoutExerciseWithProgression,
  WorkoutLog,
} from "../api/types";
import { useAuth } from "../auth/AuthContext";
import { EmptyState, ErrorState, LoadingState } from "../components/EmptyState";
import { PageHeader } from "../components/PageHeader";

type SetEntry = {
  id: string;
  weight_kg: string;
  reps: string;
  rpe: string;
};

type SetEntryField = keyof Omit<SetEntry, "id">;
type SetEntriesByWorkoutExercise = Record<string, SetEntry[]>;
type ValidationErrors = Record<string, string>;

function createSetEntry(reps = "", weightKg = ""): SetEntry {
  return {
    id: `${Date.now()}-${Math.random().toString(16).slice(2)}`,
    weight_kg: weightKg,
    reps,
    rpe: "",
  };
}

function progressionFor(item: WorkoutExercise | WorkoutExerciseWithProgression): ProgressionSuggestion | null {
  return "progression_suggestion" in item ? item.progression_suggestion : null;
}

function buildInitialSets(day: WorkoutDay | WorkoutDayWithProgression): SetEntriesByWorkoutExercise {
  return Object.fromEntries(
    day.workout_exercises.map((item) => {
      const suggestion = progressionFor(item);
      return [
        item.id,
        Array.from({ length: item.sets }, () =>
          createSetEntry(String(suggestion?.suggested_reps ?? item.rep_min), suggestion?.suggested_weight_kg ?? ""),
        ),
      ];
    }),
  );
}

function validateSets(selectedDay: WorkoutDay | WorkoutDayWithProgression, setsByExercise: SetEntriesByWorkoutExercise): ValidationErrors {
  const errors: ValidationErrors = {};
  let totalSets = 0;

  selectedDay.workout_exercises.forEach((item) => {
    const sets = setsByExercise[item.id] ?? [];
    totalSets += sets.length;

    sets.forEach((set) => {
      const reps = Number(set.reps);
      const weight = set.weight_kg === "" ? null : Number(set.weight_kg);
      const rpe = set.rpe === "" ? null : Number(set.rpe);

      if (!set.reps || Number.isNaN(reps) || reps <= 0) {
        errors[`${item.id}:${set.id}:reps`] = "Reps must be greater than 0.";
      }
      if (weight !== null && (Number.isNaN(weight) || weight < 0)) {
        errors[`${item.id}:${set.id}:weight_kg`] = "Weight cannot be negative.";
      }
      if (rpe !== null && (Number.isNaN(rpe) || rpe < 0 || rpe > 10)) {
        errors[`${item.id}:${set.id}:rpe`] = "RPE must be between 0 and 10.";
      }
    });
  });

  if (totalSets === 0) {
    errors.form = "Log at least one set before submitting.";
  }

  return errors;
}

function prescribedText(item: WorkoutExercise) {
  return `${item.sets} x ${item.rep_min}-${item.rep_max}${item.rest_seconds ? `, ${item.rest_seconds}s rest` : ""}`;
}

function formatLastPerformance(suggestion: ProgressionSuggestion) {
  if (suggestion.last_reps.length === 0) {
    return "No previous log";
  }
  const weight = suggestion.last_weight_kg ? `${suggestion.last_weight_kg} kg` : "bodyweight";
  const reps = suggestion.last_reps.join("/");
  const rpe = suggestion.last_average_rpe ? `, avg RPE ${suggestion.last_average_rpe}` : "";
  return `${weight} x ${reps}${rpe}`;
}

export function ActiveWorkoutPage() {
  const { token } = useAuth();
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [selectedDayId, setSelectedDayId] = useState("");
  const [notes, setNotes] = useState("");
  const [startedAt, setStartedAt] = useState(() => new Date().toISOString());
  const [setsByExercise, setSetsByExercise] = useState<SetEntriesByWorkoutExercise>({});
  const [errors, setErrors] = useState<ValidationErrors>({});

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
    data: logs = [],
    isLoading: logsLoading,
    isError: logsError,
  } = useQuery({
    queryKey: ["workout-logs"],
    queryFn: () => apiRequest<WorkoutLog[]>("/api/v1/workout-logs", { token }),
  });
  const { data: overrides = [] } = useQuery({
    queryKey: ["exercise-overrides"],
    queryFn: () => apiRequest<ExerciseOverride[]>("/api/v1/exercise-overrides", { token }),
  });

  const workoutDays = useMemo(() => program?.workout_days.filter((day) => day.workout_exercises.length > 0) ?? [], [program]);
  const requestedDayId = searchParams.get("dayId");
  const overrideMap = useMemo(
    () => new Map(overrides.map((override) => [override.workout_exercise_id, override])),
    [overrides],
  );

  useEffect(() => {
    if (requestedDayId && workoutDays.some((day) => day.id === requestedDayId)) {
      setSelectedDayId(requestedDayId);
    }
  }, [requestedDayId, workoutDays]);

  const selectedDay = workoutDays.find((day) => day.id === selectedDayId) ?? workoutDays[0];
  const selectedDayIdForQuery = selectedDay?.id;
  const {
    data: progressionDay,
    isLoading: progressionLoading,
    isError: progressionError,
  } = useQuery({
    queryKey: ["workout-day-progression", selectedDayIdForQuery],
    queryFn: () => apiRequest<WorkoutDayWithProgression>(`/api/v1/workout-days/${selectedDayIdForQuery}/progression`, { token }),
    enabled: Boolean(selectedDayIdForQuery),
  });
  const suggestionsPending = Boolean(selectedDayIdForQuery) && progressionLoading && !progressionDay;
  const selectedDayForLogging = progressionDay?.id === selectedDayIdForQuery ? progressionDay : selectedDay;

  useEffect(() => {
    if (selectedDayForLogging && !suggestionsPending) {
      setSetsByExercise(buildInitialSets(selectedDayForLogging));
      setErrors({});
      setStartedAt(new Date().toISOString());
    }
  }, [selectedDayForLogging, suggestionsPending]);

  function updateSet(workoutExerciseId: string, setId: string, field: SetEntryField, value: string) {
    setSetsByExercise((current) => ({
      ...current,
      [workoutExerciseId]: (current[workoutExerciseId] ?? []).map((set) =>
        set.id === setId ? { ...set, [field]: value } : set,
      ),
    }));
  }

  function addSet(item: WorkoutExercise) {
    setSetsByExercise((current) => ({
      ...current,
      [item.id]: [...(current[item.id] ?? []), createSetEntry(String(item.rep_min))],
    }));
  }

  function removeSet(workoutExerciseId: string, setId: string) {
    setSetsByExercise((current) => ({
      ...current,
      [workoutExerciseId]: (current[workoutExerciseId] ?? []).filter((set) => set.id !== setId),
    }));
  }

  function effectiveExercise(item: WorkoutExercise) {
    return overrideMap.get(item.id)?.exercise ?? item.exercise;
  }

  const createLog = useMutation({
    mutationFn: () => {
      if (!selectedDayForLogging) {
        throw new Error("No workout day selected.");
      }

      const nextErrors = validateSets(selectedDayForLogging, setsByExercise);
      setErrors(nextErrors);
      if (Object.keys(nextErrors).length > 0) {
        throw new Error("Validation failed.");
      }

      return apiRequest<WorkoutLog>("/api/v1/workout-logs", {
        method: "POST",
        token,
        body: {
          workout_day_id: selectedDayForLogging.id,
          started_at: startedAt,
          completed_at: new Date().toISOString(),
          notes: notes || null,
          set_logs: selectedDayForLogging.workout_exercises.flatMap((item) =>
            (setsByExercise[item.id] ?? []).map((set, index) => ({
              exercise_id: effectiveExercise(item).id,
              set_index: index + 1,
              reps: Number(set.reps),
              weight_kg: set.weight_kg || null,
              rpe: set.rpe || null,
            })),
          ),
        },
      });
    },
    onSuccess: () => {
      setNotes("");
      void queryClient.invalidateQueries({ queryKey: ["workout-logs"] });
      navigate("/", { replace: true });
    },
  });

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    createLog.mutate();
  }

  return (
    <main className="page">
      <PageHeader title="Active Workout" description="Log sets quickly from the selected workout day." />
      {programLoading ? <LoadingState label="Loading workout..." /> : null}
      {programError ? <ErrorState title="Workout plan unavailable" description="Run the seed script or check backend health." /> : null}
      {suggestionsPending ? <LoadingState label="Loading progression suggestions..." /> : null}
      {progressionError ? <ErrorState title="Progression suggestions unavailable" description="You can still log the workout with the programmed defaults." /> : null}
      {!programLoading && !suggestionsPending && !selectedDayForLogging ? (
        <EmptyState title="No workout day available" description="Seed the default plan, then return here to log a session." actionHref="/weekly-plan" actionLabel="View weekly plan" />
      ) : !suggestionsPending && selectedDayForLogging ? (
        <form className="active-workout" onSubmit={handleSubmit}>
          <section className="workout-toolbar panel">
            <label>
              Workout day
              <select value={selectedDayForLogging.id} onChange={(event) => setSelectedDayId(event.target.value)}>
                {workoutDays.map((day) => (
                  <option key={day.id} value={day.id}>
                    {day.title}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Notes
              <textarea value={notes} onChange={(event) => setNotes(event.target.value)} rows={3} />
            </label>
            <div className="workout-submit">
              {errors.form ? <p className="form-error">{errors.form}</p> : null}
              {createLog.isError && !errors.form ? <p className="form-error">Check set values before submitting.</p> : null}
              <button type="submit" disabled={createLog.isPending}>
                {createLog.isPending ? "Submitting..." : "Submit workout"}
              </button>
            </div>
          </section>

          <section className="set-log-list">
            {selectedDayForLogging.workout_exercises.map((item) => {
              const sets = setsByExercise[item.id] ?? [];
              const selectedExercise = effectiveExercise(item);
              const suggestion = progressionFor(item);
              return (
                <article className="set-log-card" key={item.id}>
                  <div className="set-log-header">
                    <div>
                      <h2>{selectedExercise.name}</h2>
                      {selectedExercise.id !== item.exercise_id ? <span className="swap-badge">Swapped from {item.exercise.name}</span> : null}
                      <p>{prescribedText(item)}</p>
                      {suggestion ? (
                        <div className="progression-panel">
                          <span>Last: {formatLastPerformance(suggestion)}</span>
                          <span>
                            Suggested: {suggestion.suggested_weight_kg ? `${suggestion.suggested_weight_kg} kg, ` : ""}
                            {suggestion.suggested_reps_text}
                          </span>
                          <p>{suggestion.reason}</p>
                        </div>
                      ) : null}
                    </div>
                    <button type="button" className="secondary-button" onClick={() => addSet(item)}>
                      Add set
                    </button>
                  </div>

                  <div className="set-log-grid set-log-grid-head" aria-hidden="true">
                    <span>Set</span>
                    <span>Weight kg</span>
                    <span>Reps</span>
                    <span>RPE</span>
                    <span />
                  </div>

                  {sets.map((set, index) => (
                    <div className="set-log-grid" key={set.id}>
                      <strong>Set {index + 1}</strong>
                      <label>
                        <span className="mobile-field-label">Weight kg</span>
                        <input
                          aria-label={`${selectedExercise.name} set ${index + 1} weight kg`}
                          inputMode="decimal"
                          value={set.weight_kg}
                          onChange={(event) => updateSet(item.id, set.id, "weight_kg", event.target.value)}
                        />
                        {errors[`${item.id}:${set.id}:weight_kg`] ? (
                          <span className="field-error">{errors[`${item.id}:${set.id}:weight_kg`]}</span>
                        ) : null}
                      </label>
                      <label>
                        <span className="mobile-field-label">Reps</span>
                        <input
                          aria-label={`${selectedExercise.name} set ${index + 1} reps`}
                          inputMode="numeric"
                          value={set.reps}
                          onChange={(event) => updateSet(item.id, set.id, "reps", event.target.value)}
                        />
                        {errors[`${item.id}:${set.id}:reps`] ? (
                          <span className="field-error">{errors[`${item.id}:${set.id}:reps`]}</span>
                        ) : null}
                      </label>
                      <label>
                        <span className="mobile-field-label">RPE</span>
                        <input
                          aria-label={`${selectedExercise.name} set ${index + 1} RPE`}
                          inputMode="decimal"
                          value={set.rpe}
                          onChange={(event) => updateSet(item.id, set.id, "rpe", event.target.value)}
                        />
                        {errors[`${item.id}:${set.id}:rpe`] ? (
                          <span className="field-error">{errors[`${item.id}:${set.id}:rpe`]}</span>
                        ) : null}
                      </label>
                      <button type="button" className="secondary-button compact-button" onClick={() => removeSet(item.id, set.id)}>
                        Remove
                      </button>
                    </div>
                  ))}
                </article>
              );
            })}
          </section>
        </form>
      ) : null}

      <section className="panel">
        <h2>Recent logs</h2>
        {logs.length > 0 ? (
          <ul className="plain-list">
            {logs.slice(0, 6).map((log) => (
              <li key={log.id}>
                <span>{new Date(log.started_at).toLocaleString()}</span>
                <strong>{log.notes ?? "Workout log"}</strong>
              </li>
            ))}
          </ul>
        ) : logsLoading ? (
          <LoadingState label="Loading recent logs..." />
        ) : logsError ? (
          <ErrorState title="Recent logs unavailable" description="Workout logging still works, but recent history could not be loaded." />
        ) : (
          <EmptyState title="No workout logs yet" description="Completed sessions will appear here after submission." />
        )}
      </section>
    </main>
  );
}
