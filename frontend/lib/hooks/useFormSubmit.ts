"use client";

import { useCallback, useState } from "react";
import { ApiError } from "@/lib/api/client";

export type FormSubmitStatus =
  | "idle"
  | "submitting"
  | "success"
  | "error";

type UseFormSubmitOptions<TInput, TResult> = {
  submit: (data: TInput) => Promise<TResult>;
  onSuccess?: (result: TResult) => void;
};

export function useFormSubmit<TInput, TResult>({
  submit,
  onSuccess,
}: UseFormSubmitOptions<TInput, TResult>) {
  const [status, setStatus] =
    useState<FormSubmitStatus>("idle");
  const [validationErrors, setValidationErrors] =
    useState<Record<string, string>>({});
  const [apiError, setApiError] = useState<string | null>(
    null
  );
  const [successMessage, setSuccessMessage] =
    useState<string | null>(null);

  const reset = useCallback(() => {
    setStatus("idle");
    setValidationErrors({});
    setApiError(null);
    setSuccessMessage(null);
  }, []);

  const handleSubmit = useCallback(
    async (
      validation:
        | { success: true; data: TInput }
        | {
            success: false;
            errors: Record<string, string>;
          },
      successText = "Saved successfully"
    ) => {
      setApiError(null);
      setSuccessMessage(null);

      if (!validation.success) {
        setValidationErrors(validation.errors);
        setStatus("error");
        return;
      }

      setValidationErrors({});
      setStatus("submitting");

      try {
        const result = await submit(validation.data);

        setStatus("success");
        setSuccessMessage(successText);
        onSuccess?.(result);
      } catch (error) {
        const message =
          error instanceof ApiError
            ? error.message
            : error instanceof Error
              ? error.message
              : "Submission failed";

        setApiError(message);
        setStatus("error");
      }
    },
    [onSuccess, submit]
  );

  return {
    status,
    validationErrors,
    apiError,
    successMessage,
    isSubmitting: status === "submitting",
    handleSubmit,
    reset,
  };
}
