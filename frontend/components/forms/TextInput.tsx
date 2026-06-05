import type { ComponentProps } from "react";

type Props = ComponentProps<"input"> & {
  placeholder?: string;
};

export default function TextInput({
  placeholder,
  className = "",
  ...props
}: Props) {
  return (
    <input
      {...props}
      placeholder={placeholder}
      className={`form-input ${className}`.trim()}
    />
  );
}
