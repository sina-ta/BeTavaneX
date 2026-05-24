import type { ValidationResult } from "./commonSchemas";
import {
  requireNumber,
  requireString,
} from "./commonSchemas";

export type WorkforceWorkerFormValues = {
  first_name: string;
  last_name: string;
  national_id: string;
  phone: string;
  trade_id: string;
  current_role: string;
  skill_level: string;
  availability_status: string;
  daily_cost: string;
  safety_clearance: string;
};

export const workforceWorkerFormDefaults: WorkforceWorkerFormValues = {
  first_name: "",
  last_name: "",
  national_id: "",
  phone: "",
  trade_id: "",
  current_role: "",
  skill_level: "mid",
  availability_status: "available",
  daily_cost: "",
  safety_clearance: "",
};

export function validateWorkforceWorkerForm(
  values: WorkforceWorkerFormValues
): ValidationResult<WorkforceWorkerFormValues> {
  const errors: Record<string, string> = {};

  const firstNameError = requireString(
    values.first_name,
    "first_name",
    "First name"
  );
  if (firstNameError) errors.first_name = firstNameError;

  const lastNameError = requireString(
    values.last_name,
    "last_name",
    "Last name"
  );
  if (lastNameError) errors.last_name = lastNameError;

  const nationalIdError = requireString(
    values.national_id,
    "national_id",
    "National ID"
  );
  if (nationalIdError) errors.national_id = nationalIdError;

  const tradeError = requireNumber(
    values.trade_id,
    "trade_id",
    "Trade",
    { min: 1 }
  );
  if (tradeError) errors.trade_id = tradeError;

  if (values.daily_cost) {
    const costError = requireNumber(
      values.daily_cost,
      "daily_cost",
      "Daily cost",
      { min: 0 }
    );
    if (costError) errors.daily_cost = costError;
  }

  if (Object.keys(errors).length > 0) {
    return { success: false, errors };
  }

  return {
    success: true,
    data: {
      ...values,
      first_name: values.first_name.trim(),
      last_name: values.last_name.trim(),
      national_id: values.national_id.trim(),
      phone: values.phone.trim(),
      current_role: values.current_role.trim(),
      safety_clearance: values.safety_clearance.trim(),
    },
  };
}
