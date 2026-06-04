import { Exercise, UserProfile } from "../api/types";

const homeEquipmentKeywords = [
  "adjustable",
  "bodyweight",
  "barbell",
  "dumbbell",
  "floor",
  "chair",
  "band",
  "walking",
  "shoes",
  "optional",
];

export function isExerciseCompatible(exercise: Exercise, preferredMode: UserProfile["preferred_mode"] | undefined) {
  if (preferredMode === "gym") {
    return true;
  }
  const equipment = exercise.equipment.join(" ").toLowerCase();
  return homeEquipmentKeywords.some((keyword) => equipment.includes(keyword));
}

export function equipmentLabel(exercise: Exercise) {
  return exercise.equipment.length > 0 ? exercise.equipment.join(", ") : "No equipment listed";
}
