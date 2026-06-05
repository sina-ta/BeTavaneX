"use client";

import FormField from "@/components/forms/FormField";

export type EntityOption = {
  value: string;
  label: string;
};

type Props = {
  label: string;
  value: string;
  onChange: (value: string) => void;
  options: EntityOption[];
  placeholder?: string;
  error?: string;
  disabled?: boolean;
};

/**
 * UUID-aware select: shows a human label, submits a UUID value. Styled to match
 * the existing form kit (same classes as SelectInput) — no new design system.
 */
export default function EntitySelect({
  label,
  value,
  onChange,
  options,
  placeholder = "Select…",
  error,
  disabled = false,
}: Props) {
  return (
    <FormField label={label} error={error}>
      <select
        value={value}
        disabled={disabled}
        onChange={(event) => onChange(event.target.value)}
        className="form-input"
      >
        <option value="">{placeholder}</option>
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </FormField>
  );
}
