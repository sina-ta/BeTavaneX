type Props = {
  label: string;
  children: React.ReactNode;
};

export default function FormField({
  label,
  children,
}: Props) {

  return (

    <div
      className="
        flex
        flex-col
        gap-2
      "
    >

      <label
        className="
          text-sm
          font-medium
          text-gray-400
        "
      >

        {label}

      </label>

      {children}

    </div>
  );
}