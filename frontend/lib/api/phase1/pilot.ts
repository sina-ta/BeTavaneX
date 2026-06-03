import { apiRequest } from "@/lib/api/client";

export type PilotFeedbackCategory =
  | "confusion"
  | "blocker"
  | "missing_flow"
  | "ux_pain"
  | "gap"
  | "other";

export interface PilotFeedbackPayload {
  category: PilotFeedbackCategory;
  message: string;
  page_path?: string;
  project_id?: string;
}

export async function submitPilotFeedback(
  payload: PilotFeedbackPayload,
): Promise<{ status: string; recorded_at: string }> {
  return apiRequest("/pilot/feedback", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
