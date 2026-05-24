import ValidationMessage from "./ValidationMessage";

type Props = {
  label: string;
  children: React.ReactNode;
  error?: string;
};

export default function FormField({
  label,
  children,
  error,
}: Props) {
  return (
    <section className="flex flex-col gap-2">
      <label className="text-sm font-medium text-gray-400">
        {label}
      </label>

      {children}

      <ValidationMessage message={error} />
    </section>
  );
}
