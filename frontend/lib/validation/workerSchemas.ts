import type { ValidationResult } from "./commonSchemas";
import { requireString } from "./commonSchemas";

export type WorkerFormValues = {
  full_name: string;
  role: string;
  crew: string;
  daily_wage: string;
};

export function validateWorkerForm(
  values: WorkerFormValues
): ValidationResult<WorkerFormValues> {
  const errors: Record<string, string> = {};

  const nameError = requireString(
    values.full_name,
    "full_name",
    "Full name"
  );

  if (nameError) {
    errors.full_name = nameError;
  }

  const roleError = requireString(
    values.role,
    "role",
    "Role"
  );

  if (roleError) {
    errors.role = roleError;
  }

  if (Object.keys(errors).length > 0) {
    return { success: false, errors };
  }

  return { success: true, data: values };
}
