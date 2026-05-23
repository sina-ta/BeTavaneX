type Props = {
  options: string[];
};

export default function SelectInput({
  options,
}: Props) {

  return (

    <select
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
    >

      {options.map((option) => (

        <option
          key={option}
          value={option}
        >

          {option}

        </option>

      ))}

    </select>
  );
}