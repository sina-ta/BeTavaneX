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
    <section className="form-field">
      <label className="input-label">{label}</label>

      {children}

      <ValidationMessage message={error} />
    </section>
  );
}
