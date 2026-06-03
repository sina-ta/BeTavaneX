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
      className={`
        w-full
        rounded-2xl
        border
        border-slate-700
        bg-slate-900
        px-4
        py-3
        text-white
        outline-none
        transition
        focus:border-blue-500
        ${className}
      `}
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
