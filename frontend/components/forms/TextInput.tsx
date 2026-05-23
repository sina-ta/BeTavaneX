type Props = {
  placeholder?: string;
  type?: string;
};

export default function TextInput({
  placeholder,
  type = "text",
}: Props) {

  return (

    <input
      type={type}
      placeholder={placeholder}
      className="
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
      "
    />

  );
}