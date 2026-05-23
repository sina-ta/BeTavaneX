type Props = {
  placeholder?: string;
};

export default function TextareaInput({
  placeholder,
}: Props) {

  return (

    <textarea
      placeholder={placeholder}
      rows={5}
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