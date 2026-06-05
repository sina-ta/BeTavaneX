import type { ComponentProps } from "react";

type Props = ComponentProps<"textarea"> & {
  placeholder?: string;
};

export default function TextareaInput({
  placeholder,
  className = "",
  ...props
}: Props) {
  return (
    <textarea
      {...props}
      placeholder={placeholder}
      className={`form-input ${className}`.trim()}
    />
  );
}
