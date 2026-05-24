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
    />
  );
}
