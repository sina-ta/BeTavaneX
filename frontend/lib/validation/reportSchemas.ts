import type { ValidationResult } from "./commonSchemas";
import {
  requireNumber,
  requireString,
} from "./commonSchemas";
import type { CreateReportPayload } from "@/types/report";

export type ReportFormValues = {
  work_order_id: string;
  reported_by: string;
  actual_qty: string;
  manpower_count: string;
  equipment_hours: string;
  material_consumption: string;
  delay_reason: string;
  weather_status: string;
  photo_count: string;
  report_status: string;
  approved_by: string;
};

export const reportFormDefaults: ReportFormValues = {
  work_order_id: "",
  reported_by: "",
  actual_qty: "",
  manpower_count: "",
  equipment_hours: "",
  material_consumption: "",
  delay_reason: "",
  weather_status: "Good",
  photo_count: "0",
  report_status: "Draft",
  approved_by: "",
};

export function validateReportForm(
  values: ReportFormValues
): ValidationResult<CreateReportPayload> {
  const errors: Record<string, string> = {};

  const workOrderError = requireNumber(
    values.work_order_id,
    "work_order_id",
    "Work order ID",
    { min: 1 }
  );

  if (workOrderError) {
    errors.work_order_id = workOrderError;
  }

  const reportedByError = requireString(
    values.reported_by,
    "reported_by",
    "Reported by"
  );

  if (reportedByError) {
    errors.reported_by = reportedByError;
  }

  const actualQtyError = requireNumber(
    values.actual_qty,
    "actual_qty",
    "Actual quantity",
    { min: 0 }
  );

  if (actualQtyError) {
    errors.actual_qty = actualQtyError;
  }

  const manpowerError = requireNumber(
    values.manpower_count,
    "manpower_count",
    "Manpower count",
    { min: 0 }
  );

  if (manpowerError) {
    errors.manpower_count = manpowerError;
  }

  const equipmentError = requireNumber(
    values.equipment_hours,
    "equipment_hours",
    "Equipment hours",
    { min: 0 }
  );

  if (equipmentError) {
    errors.equipment_hours = equipmentError;
  }

  const materialError = requireString(
    values.material_consumption,
    "material_consumption",
    "Material consumption"
  );

  if (materialError) {
    errors.material_consumption = materialError;
  }

  const weatherError = requireString(
    values.weather_status,
    "weather_status",
    "Weather status"
  );

  if (weatherError) {
    errors.weather_status = weatherError;
  }

  const statusError = requireString(
    values.report_status,
    "report_status",
    "Report status"
  );

  if (statusError) {
    errors.report_status = statusError;
  }

  if (Object.keys(errors).length > 0) {
    return { success: false, errors };
  }

  return {
    success: true,
    data: {
      work_order_id: Number(values.work_order_id),
      reported_by: values.reported_by.trim(),
      actual_qty: Number(values.actual_qty),
      manpower_count: Number(values.manpower_count),
      equipment_hours: Number(values.equipment_hours),
      material_consumption: values.material_consumption.trim(),
      delay_reason: values.delay_reason.trim(),
      weather_status: values.weather_status,
      photo_count: Number(values.photo_count || 0),
      report_status: values.report_status,
      approved_by: values.approved_by.trim(),
    },
  };
}
