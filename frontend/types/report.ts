export interface DailyReport {
  id: number;
  work_order_id: number;
  reported_by: string;
  actual_qty: number;
  manpower_count: number;
  equipment_hours: number;
  material_consumption: string;
  delay_reason: string;
  weather_status: string;
  photo_count: number;
  report_status: string;
  approved_by: string;
}

export interface CreateReportPayload {
  work_order_id: number;
  reported_by: string;
  actual_qty: number;
  manpower_count: number;
  equipment_hours: number;
  material_consumption: string;
  delay_reason: string;
  weather_status: string;
  photo_count: number;
  report_status: string;
  approved_by: string;
}

export interface CreateReportResponse {
  message: string;
  validation_warnings: string[];
}
