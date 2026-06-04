import { useQuery } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";

import { apiRequest } from "../api/client";
import { ExerciseDetail } from "../api/types";
import { useAuth } from "../auth/AuthContext";
import { EmptyState, LoadingState } from "../components/EmptyState";
import { PageHeader } from "../components/PageHeader";
import { equipmentLabel } from "../lib/equipment";

export function ExerciseDetailPage() {
  const { exerciseId } = useParams();
  const { token, user } = useAuth();
  const { data: exercise, isLoading, error } = useQuery({
    queryKey: ["exercise", exerciseId],
    queryFn: () => apiRequest<ExerciseDetail>(`/api/v1/exercises/${exerciseId}`, { token }),
    enabled: Boolean(exerciseId),
  });

  if (isLoading) {
    return (
      <main className="page">
        <LoadingState label="Loading exercise..." />
      </main>
    );
  }

  if (error || !exercise) {
    return (
      <main className="page">
        <EmptyState title="Exercise not found" description="Return to the library and choose another exercise." actionHref="/exercises" actionLabel="Back to library" />
      </main>
    );
  }

  return (
    <main className="page">
      <PageHeader title={exercise.name} description={exercise.instructions ?? "No instructions listed."} />
      <section className="content-grid">
        <article className="panel">
          <h2>Details</h2>
          <dl className="meta-list">
            <div>
              <dt>Primary muscle</dt>
              <dd>{exercise.primary_muscle}</dd>
            </div>
            <div>
              <dt>Secondary muscles</dt>
              <dd>{exercise.secondary_muscles.join(", ") || "-"}</dd>
            </div>
            <div>
              <dt>Equipment</dt>
              <dd>{equipmentLabel(exercise)}</dd>
            </div>
            <div>
              <dt>Mode fit</dt>
              <dd>
                {exercise.equipment_compatible
                  ? `Compatible with ${user?.profile?.preferred_mode ?? "home"} mode`
                  : "Better suited to gym mode"}
              </dd>
            </div>
            <div>
              <dt>Easier option</dt>
              <dd>{exercise.easier_variation_notes ?? "Reduce load or range as needed."}</dd>
            </div>
          </dl>
        </article>

        <article className="panel">
          <h2>Alternatives</h2>
          {exercise.alternatives.length > 0 ? (
            <ul className="plain-list">
              {exercise.alternatives.map((alternative) => (
                <li key={alternative.id}>
                  <Link to={`/exercises/${alternative.id}`}>{alternative.name}</Link>
                  <span>{equipmentLabel(alternative)}</span>
                </li>
              ))}
            </ul>
          ) : (
            <EmptyState title="No alternatives listed" description="This movement can still be used as prescribed." />
          )}
        </article>
      </section>
    </main>
  );
}
