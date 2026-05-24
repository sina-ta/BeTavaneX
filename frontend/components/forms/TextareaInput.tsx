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
      rows={props.rows ?? 5}
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
