import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { Navigate, useNavigate } from "react-router-dom";
import { z } from "zod";

import { ApiError } from "../api/client";
import { useAuth } from "../auth/AuthContext";

const profileSchema = z.object({
  height_cm: z.string().optional(),
  current_weight_kg: z.string().optional(),
  goal: z.string().max(120).optional(),
  training_level: z.string().max(50).optional(),
  preferred_mode: z.enum(["home", "gym"]),
  target_weekly_weight_loss_kg: z.string().optional(),
  target_protein_g: z.string().optional(),
  target_calories: z.string().optional(),
});

type ProfileFormValues = z.infer<typeof profileSchema>;

function cleanProfile(values: ProfileFormValues) {
  return {
    height_cm: values.height_cm || undefined,
    current_weight_kg: values.current_weight_kg || undefined,
    goal: values.goal || undefined,
    training_level: values.training_level || undefined,
    preferred_mode: values.preferred_mode,
    target_weekly_weight_loss_kg: values.target_weekly_weight_loss_kg || undefined,
    target_protein_g: values.target_protein_g || undefined,
    target_calories: values.target_calories ? Number(values.target_calories) : undefined,
  };
}

export function OnboardingProfilePage() {
  const { user, createProfile } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ProfileFormValues>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      height_cm: "184",
      current_weight_kg: "115",
      preferred_mode: "home",
      target_weekly_weight_loss_kg: "0.5",
      target_protein_g: "180",
      target_calories: "2300",
      training_level: "beginner",
      goal: "Fat loss, muscle volume, and strength",
    },
  });

  if (user?.profile) {
    return <Navigate to="/" replace />;
  }

  async function onSubmit(values: ProfileFormValues) {
    setError(null);
    try {
      await createProfile(cleanProfile(values));
      navigate("/", { replace: true });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not save profile");
    }
  }

  return (
    <main className="auth-page">
      <form className="form-card wide-form" onSubmit={handleSubmit(onSubmit)}>
        <h2>Set up profile</h2>
        <div className="form-grid">
          <label>
            Height cm
            <input inputMode="decimal" {...register("height_cm")} />
          </label>
          <label>
            Current weight kg
            <input inputMode="decimal" {...register("current_weight_kg")} />
          </label>
          <label>
            Training level
            <input {...register("training_level")} />
          </label>
          <label>
            Preferred mode
            <select {...register("preferred_mode")}>
              <option value="home">Home</option>
              <option value="gym">Gym</option>
            </select>
          </label>
          <label>
            Weekly loss target kg
            <input inputMode="decimal" {...register("target_weekly_weight_loss_kg")} />
          </label>
          <label>
            Protein target g
            <input inputMode="decimal" {...register("target_protein_g")} />
          </label>
          <label>
            Calorie target
            <input inputMode="numeric" {...register("target_calories")} />
          </label>
          <label className="full-field">
            Goal
            <input {...register("goal")} />
            {errors.goal ? <span className="field-error">{errors.goal.message}</span> : null}
          </label>
        </div>
        {error ? <p className="form-error">{error}</p> : null}
        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Saving..." : "Save profile"}
        </button>
      </form>
    </main>
  );
}
