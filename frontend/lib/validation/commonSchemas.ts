export type ValidationResult<T> =
  | {
      success: true;
      data: T;
    }
  | {
      success: false;
      errors: Record<string, string>;
    };

export function fieldError(
  errors: Record<string, string>,
  field: string
): string | undefined {
  return errors[field];
}

export function hasFieldError(
  errors: Record<string, string>,
  field: string
): boolean {
  return Boolean(errors[field]);
}

export function requireString(
  value: unknown,
  field: string,
  label: string
): string | null {
  if (typeof value !== "string" || !value.trim()) {
    return `${label} is required`;
  }

  return null;
}

export function requireNumber(
  value: unknown,
  field: string,
  label: string,
  options?: { min?: number }
): string | null {
  const parsed = Number(value);

  if (Number.isNaN(parsed)) {
    return `${label} must be a number`;
  }

  if (options?.min !== undefined && parsed < options.min) {
    return `${label} must be at least ${options.min}`;
  }

  return null;
}

export function collectErrors(
  checks: Array<string | null>
): Record<string, string> {
  return checks.reduce<Record<string, string>>(
    (errors, message, index) => {
      if (message) {
        errors[`field_${index}`] = message;
      }

      return errors;
    },
    {}
  );
}
