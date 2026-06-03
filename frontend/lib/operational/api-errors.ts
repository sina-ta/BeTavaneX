import { ApiError } from "@/lib/api/client";

/**
 * Plain-language API errors for field and supervisor workflows (Stage 26).
 */
export function formatOperationalApiError(error: unknown): string {
  if (!(error instanceof ApiError)) {
    return error instanceof Error ? error.message : "Submission failed";
  }

  if (error.status === 409) {
    return (
      "This record was updated by someone else. Refresh the page, then submit again."
    );
  }

  if (error.status === 403) {
    return (
      "You do not have access to this project or action. Check the selected project and your role."
    );
  }

  if (error.status === 401) {
    return "Your session expired. Sign in again.";
  }

  if (error.status === 404) {
    return "That item no longer exists or is not in this project. Refresh and pick again.";
  }

  if (error.status === 422) {
    return error.message || "Check required fields and try again.";
  }

  return error.message;
}
