export type UserProfile = {
  user_id: string;
  height_cm: string | null;
  current_weight_kg: string | null;
  goal: string | null;
  training_level: string | null;
  preferred_mode: "home" | "gym";
  target_weekly_weight_loss_kg: string | null;
  target_protein_g: string | null;
  target_calories: number | null;
  created_at: string;
  updated_at: string;
};

export type User = {
  id: string;
  email: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  profile: UserProfile | null;
};

export type TokenResponse = {
  access_token: string;
  token_type: "bearer";
};

export type Exercise = {
  id: string;
  name: string;
  primary_muscle: string;
  secondary_muscles: string[];
  equipment: string[];
  difficulty: string | null;
  instructions: string | null;
  easier_variation_notes: string | null;
  alternative_exercise_ids: string[];
  created_at: string;
  updated_at: string;
};

export type ExerciseDetail = Exercise & {
  alternatives: Exercise[];
  equipment_compatible: boolean;
};

export type ExerciseOverride = {
  id: string;
  user_id: string;
  workout_exercise_id: string;
  exercise_id: string;
  exercise: Exercise;
  created_at: string;
  updated_at: string;
};

export type WorkoutExercise = {
  id: string;
  workout_day_id: string;
  exercise_id: string;
  order_index: number;
  sets: number;
  rep_min: number;
  rep_max: number;
  rest_seconds: number | null;
  tempo: string | null;
  notes: string | null;
  exercise: Exercise;
  created_at: string;
  updated_at: string;
};

export type WorkoutDay = {
  id: string;
  program_id: string;
  day_of_week: number;
  title: string;
  focus: string | null;
  workout_exercises: WorkoutExercise[];
  created_at: string;
  updated_at: string;
};

export type Program = {
  id: string;
  user_id: string;
  name: string;
  description: string | null;
  is_active: boolean;
  workout_days: WorkoutDay[];
  created_at: string;
  updated_at: string;
};

export type SetLog = {
  id: string;
  workout_log_id: string;
  exercise_id: string;
  set_index: number;
  weight_kg: string | null;
  reps: number;
  rpe: string | null;
  created_at: string;
  updated_at: string;
};

export type WorkoutLog = {
  id: string;
  user_id: string;
  workout_day_id: string | null;
  started_at: string;
  completed_at: string | null;
  notes: string | null;
  set_logs: SetLog[];
  created_at: string;
  updated_at: string;
};

export type BodyMetric = {
  id: string;
  user_id: string;
  date: string;
  weight_kg: string | null;
  waist_cm: string | null;
  steps: number | null;
  protein_g: string | null;
  calories: number | null;
  nutrition_note: string | null;
  sleep_hours: string | null;
  mood: string | null;
  created_at: string;
  updated_at: string;
};
