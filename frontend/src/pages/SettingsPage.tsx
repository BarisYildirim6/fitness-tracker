import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { useAuth } from "../auth/AuthContext";
import { PageHeader } from "../components/PageHeader";

const optionalDecimal = z
  .string()
  .optional()
  .refine((value) => value === undefined || value === "" || (!Number.isNaN(Number(value)) && Number(value) >= 0), {
    message: "Must be a positive number.",
  });

const optionalInteger = z
  .string()
  .optional()
  .refine((value) => value === undefined || value === "" || (/^\d+$/.test(value) && Number(value) >= 0), {
    message: "Must be a whole number.",
  });

const settingsSchema = z.object({
  preferred_mode: z.enum(["home", "gym"]),
  goal: z.string().max(120).optional(),
  target_protein_g: optionalDecimal,
  target_calories: optionalInteger,
});

type SettingsFormValues = z.infer<typeof settingsSchema>;

function cleanSettings(values: SettingsFormValues) {
  return {
    preferred_mode: values.preferred_mode,
    goal: values.goal || undefined,
    target_protein_g: values.target_protein_g || undefined,
    target_calories: values.target_calories ? Number(values.target_calories) : undefined,
  };
}

export function SettingsPage() {
  const { user, updateProfile, logout } = useAuth();
  const [saveError, setSaveError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);
  const {
    register,
    reset,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<SettingsFormValues>({
    resolver: zodResolver(settingsSchema),
    defaultValues: {
      preferred_mode: user?.profile?.preferred_mode ?? "home",
      goal: user?.profile?.goal ?? "",
      target_protein_g: user?.profile?.target_protein_g ?? "",
      target_calories: user?.profile?.target_calories ? String(user.profile.target_calories) : "",
    },
  });

  useEffect(() => {
    reset({
      preferred_mode: user?.profile?.preferred_mode ?? "home",
      goal: user?.profile?.goal ?? "",
      target_protein_g: user?.profile?.target_protein_g ?? "",
      target_calories: user?.profile?.target_calories ? String(user.profile.target_calories) : "",
    });
  }, [reset, user]);

  async function onSubmit(values: SettingsFormValues) {
    setSaveError(null);
    setSaved(false);
    try {
      await updateProfile(cleanSettings(values));
      setSaved(true);
    } catch {
      setSaveError("Could not save profile targets. Check the values and try again.");
    }
  }

  return (
    <main className="page">
      <PageHeader title="Settings" description="Account and profile targets." />
      <section className="content-grid">
        <form className="panel form-panel settings-panel" onSubmit={handleSubmit(onSubmit)}>
          <h2>Profile targets</h2>
          <label>
            Preferred mode
            <select {...register("preferred_mode")}>
              <option value="home">Home</option>
              <option value="gym">Gym</option>
            </select>
          </label>
          <label>
            Goal
            <input {...register("goal")} />
            {errors.goal ? <span className="field-error">{errors.goal.message}</span> : null}
          </label>
          <div className="form-grid">
            <label>
              Protein target g
              <input inputMode="decimal" {...register("target_protein_g")} />
              {errors.target_protein_g ? <span className="field-error">{errors.target_protein_g.message}</span> : null}
            </label>
            <label>
              Calorie target
              <input inputMode="numeric" {...register("target_calories")} />
              {errors.target_calories ? <span className="field-error">{errors.target_calories.message}</span> : null}
            </label>
          </div>
          <button type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Saving..." : "Save targets"}
          </button>
          {saveError ? <p className="form-error">{saveError}</p> : null}
          {saved ? <p className="form-note">Targets saved.</p> : null}
        </form>

        <section className="panel settings-panel">
          <h2>Account</h2>
          <dl className="meta-list">
            <div>
              <dt>Email</dt>
              <dd>{user?.email}</dd>
            </div>
            <div>
              <dt>Protein target</dt>
              <dd>{user?.profile?.target_protein_g ? `${user.profile.target_protein_g} g` : "-"}</dd>
            </div>
            <div>
              <dt>Calorie target</dt>
              <dd>{user?.profile?.target_calories ?? "-"}</dd>
            </div>
          </dl>
          <button type="button" className="secondary-button" onClick={logout}>
            Log out
          </button>
        </section>
      </section>
    </main>
  );
}
