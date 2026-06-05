import type { ComponentProps } from "react";

export type EntityOption = {
  value: string;
  label: string;
  updatedAt?: string;
};

type Props = Omit<ComponentProps<"select">, "children"> & {
  options: EntityOption[];
  placeholder?: string;
};

/**
 * Select whose option value differs from its label (e.g. UUID value, name
 * label). Mirrors the styling of the string-based `SelectInput` so the form
 * kit stays visually consistent.
 */
export default function EntitySelect({
  options,
  placeholder = "Select…",
  className = "",
  ...props
}: Props) {
  return (
    <select
      {...props}
      className={`form-input ${className}`.trim()}
    >
      <option value="">{placeholder}</option>
      {options.map((option) => (
        <option key={option.value} value={option.value}>
          {option.label}
        </option>
      ))}
    </select>
  );
}
