import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { Link } from "react-router-dom";

import { apiRequest } from "../api/client";
import { Exercise } from "../api/types";
import { useAuth } from "../auth/AuthContext";
import { EmptyState, ErrorState, LoadingState } from "../components/EmptyState";
import { PageHeader } from "../components/PageHeader";
import { equipmentLabel } from "../lib/equipment";

export function ExerciseLibraryPage() {
  const { token } = useAuth();
  const [muscle, setMuscle] = useState("");
  const [equipment, setEquipment] = useState("");
  const { data: exercises = [], isLoading, isError } = useQuery({
    queryKey: ["exercises", muscle, equipment],
    queryFn: () => apiRequest<Exercise[]>("/api/v1/exercises", { token, query: { muscle, equipment } }),
  });

  return (
    <main className="page">
      <PageHeader title="Exercise Library" description="Search seeded exercises by target muscle or equipment." />
      <section className="filter-bar">
        <label>
          Muscle
          <input value={muscle} onChange={(event) => setMuscle(event.target.value)} placeholder="quads, chest, core" />
        </label>
        <label>
          Equipment
          <input value={equipment} onChange={(event) => setEquipment(event.target.value)} placeholder="dumbbell, bodyweight" />
        </label>
      </section>

      {isLoading ? <LoadingState label="Loading exercises..." /> : null}
      {isError ? <ErrorState title="Exercise library unavailable" description="Check that the backend is healthy and seeded." /> : null}
      {!isLoading && !isError && exercises.length === 0 ? (
        <EmptyState title="No exercises found" description="Clear the filters or run the seed script to load the default library." />
      ) : null}

      <section className="card-grid">
        {exercises.map((exercise) => (
          <article className="item-card" key={exercise.id}>
            <div className="section-title">
              <h2>
                <Link to={`/exercises/${exercise.id}`}>{exercise.name}</Link>
              </h2>
              <span>{exercise.difficulty}</span>
            </div>
            <p>{exercise.instructions}</p>
            <dl className="meta-list">
              <div>
                <dt>Primary</dt>
                <dd>{exercise.primary_muscle}</dd>
              </div>
              <div>
                <dt>Equipment</dt>
                <dd>{equipmentLabel(exercise)}</dd>
              </div>
              <div>
                <dt>Easier</dt>
                <dd>{exercise.easier_variation_notes ?? "-"}</dd>
              </div>
            </dl>
          </article>
        ))}
      </section>
    </main>
  );
}
