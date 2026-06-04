import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import { apiRequest } from "../api/client";
import { Exercise, ExerciseOverride, Program, WorkoutDay, WorkoutExercise } from "../api/types";
import { useAuth } from "../auth/AuthContext";
import { EmptyState, ErrorState, LoadingState } from "../components/EmptyState";
import { PageHeader } from "../components/PageHeader";
import { equipmentLabel, isExerciseCompatible } from "../lib/equipment";

const dayNames = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

function isRecoveryDay(day: WorkoutDay) {
  return day.workout_exercises.length === 0 || /recovery|rest|walk|cardio|conditioning/i.test(`${day.title} ${day.focus ?? ""}`);
}

function formatRest(seconds: number | null) {
  if (!seconds) {
    return "As needed";
  }
  if (seconds >= 60 && seconds % 60 === 0) {
    return `${seconds / 60} min`;
  }
  return `${seconds} sec`;
}

function alternativesFor(item: WorkoutExercise, exerciseMap: Map<string, Exercise>) {
  return item.exercise.alternative_exercise_ids
    .map((id) => exerciseMap.get(id)?.name)
    .filter((name): name is string => Boolean(name));
}

export function WeeklyPlanPage() {
  const { token, user } = useAuth();
  const queryClient = useQueryClient();
  const { data: program, isLoading, error } = useQuery({
    queryKey: ["active-program"],
    queryFn: () => apiRequest<Program>("/api/v1/programs/active", { token }),
    retry: false,
  });
  const { data: exercises = [], isLoading: exercisesLoading } = useQuery({
    queryKey: ["exercises"],
    queryFn: () => apiRequest<Exercise[]>("/api/v1/exercises", { token }),
  });
  const { data: overrides = [], isError: overridesError } = useQuery({
    queryKey: ["exercise-overrides"],
    queryFn: () => apiRequest<ExerciseOverride[]>("/api/v1/exercise-overrides", { token }),
  });

  const saveOverride = useMutation({
    mutationFn: async ({ workoutExerciseId, exerciseId, originalExerciseId }: { workoutExerciseId: string; exerciseId: string; originalExerciseId: string }) => {
      if (exerciseId === originalExerciseId) {
        await apiRequest<void>(`/api/v1/exercise-overrides/${workoutExerciseId}`, { method: "DELETE", token });
        return;
      }
      await apiRequest<ExerciseOverride>(`/api/v1/exercise-overrides/${workoutExerciseId}`, {
        method: "PUT",
        token,
        body: { exercise_id: exerciseId },
      });
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["exercise-overrides"] });
    },
  });

  const exerciseMap = new Map(exercises.map((exercise) => [exercise.id, exercise]));
  const overrideMap = new Map(overrides.map((override) => [override.workout_exercise_id, override]));
  const sortedDays = [...(program?.workout_days ?? [])].sort((left, right) => left.day_of_week - right.day_of_week);
  const preferredMode = user?.profile?.preferred_mode ?? "home";

  function effectiveExercise(item: WorkoutExercise) {
    return overrideMap.get(item.id)?.exercise ?? item.exercise;
  }

  function swapOptions(item: WorkoutExercise) {
    const original = item.exercise;
    const alternatives = item.exercise.alternative_exercise_ids
      .map((id) => exerciseMap.get(id))
      .filter((exercise): exercise is Exercise => Boolean(exercise));
    const current = effectiveExercise(item);
    const unique = new Map([original, current, ...alternatives].map((exercise) => [exercise.id, exercise]));
    return [...unique.values()].filter(
      (exercise) => exercise.id === original.id || exercise.id === current.id || isExerciseCompatible(exercise, preferredMode),
    );
  }

  return (
    <main className="page">
      <PageHeader title="Weekly Plan" description="Review the active weekly plan and prescribed exercise targets." />
      {isLoading || exercisesLoading ? <LoadingState label="Loading weekly plan..." /> : null}
      {error ? <ErrorState title="No active plan found" description="Run the seed script to load the default home plan." /> : null}
      {overridesError ? <ErrorState title="Saved swaps unavailable" description="The plan is still usable, but saved exercise substitutions could not be loaded." /> : null}
      {program ? (
        <section className="weekly-plan">
          {sortedDays.map((day) => {
            const recoveryDay = isRecoveryDay(day);
            const trainingDay = day.workout_exercises.length > 0;

            return (
              <article className={`day-card ${recoveryDay ? "day-card-recovery" : "day-card-strength"}`} key={day.id}>
                <div className="day-card-header">
                  <div>
                    <span className="day-label">{dayNames[day.day_of_week - 1]}</span>
                    <h2>{day.title}</h2>
                    <p>{day.focus ?? "No focus set"}</p>
                  </div>
                  <div className="day-actions">
                    <span className="day-type">{recoveryDay ? "Recovery" : "Strength"}</span>
                    {trainingDay ? (
                      <Link className="button-link" to={`/active-workout?dayId=${day.id}`}>
                        Start workout
                      </Link>
                    ) : null}
                  </div>
                </div>

                {trainingDay ? (
                  <div className="exercise-plan-list">
                    {day.workout_exercises.map((item) => {
                      const alternatives = alternativesFor(item, exerciseMap);
                      const selectedExercise = effectiveExercise(item);
                      const options = swapOptions(item);
                      return (
                        <section className="exercise-plan-row" key={item.id}>
                          <div className="exercise-plan-main">
                            <h3>
                              <Link to={`/exercises/${selectedExercise.id}`}>{selectedExercise.name}</Link>
                            </h3>
                            {selectedExercise.id !== item.exercise_id ? <span className="swap-badge">Swapped from {item.exercise.name}</span> : null}
                            <p>{item.notes ?? selectedExercise.instructions ?? "No notes yet."}</p>
                          </div>
                          <dl className="exercise-prescription">
                            <div>
                              <dt>Sets</dt>
                              <dd>{item.sets}</dd>
                            </div>
                            <div>
                              <dt>Rep range</dt>
                              <dd>
                                {item.rep_min}-{item.rep_max}
                              </dd>
                            </div>
                            <div>
                              <dt>Rest</dt>
                              <dd>{formatRest(item.rest_seconds)}</dd>
                            </div>
                          </dl>
                          <div className="exercise-options">
                            <div>
                              <strong>Alternatives</strong>
                              <span>{alternatives.length > 0 ? alternatives.join(", ") : "None listed"}</span>
                            </div>
                            <div>
                              <strong>Easier option</strong>
                              <span>{selectedExercise.easier_variation_notes ?? "Reduce load or range as needed."}</span>
                            </div>
                            <div className="swap-control">
                              <strong>Swap movement</strong>
                              <div>
                                <select
                                  value={selectedExercise.id}
                                  disabled={saveOverride.isPending}
                                  onChange={(event) =>
                                    saveOverride.mutate({
                                      workoutExerciseId: item.id,
                                      exerciseId: event.target.value,
                                      originalExerciseId: item.exercise_id,
                                    })
                                  }
                                  aria-label={`Swap ${item.exercise.name}`}
                                >
                                  {options.map((option) => (
                                    <option key={option.id} value={option.id}>
                                      {option.name} ({equipmentLabel(option)})
                                    </option>
                                  ))}
                                </select>
                                {saveOverride.isError ? <span className="field-error">Could not save swap.</span> : null}
                              </div>
                            </div>
                          </div>
                        </section>
                      );
                    })}
                  </div>
                ) : (
                  <div className="recovery-block">
                    <strong>{day.title.includes("Rest") ? "Full rest day" : "Recovery day"}</strong>
                    <p>
                      {day.workout_exercises.length === 0
                        ? "No strength work scheduled. Keep activity easy and focus on recovery."
                        : "Keep intensity low and use the session for walking, mobility, or light conditioning."}
                    </p>
                  </div>
                )}
              </article>
            );
          })}
        </section>
      ) : null}
    </main>
  );
}
