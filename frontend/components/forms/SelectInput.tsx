import type { ComponentProps } from "react";

type Props = ComponentProps<"select"> & {
  options: readonly string[] | string[];
};

export default function SelectInput({
  options,
  className = "",
  ...props
}: Props) {
  return (
    <select {...props} className={`form-input ${className}`.trim()}>
      {options.map((option) => (
        <option key={option} value={option}>
          {option}
        </option>
      ))}
    </select>
  );
}
