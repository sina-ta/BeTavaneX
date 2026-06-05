type FormErrorProps = {
  message?: string | null;
};

export default function FormError({
  message,
}: FormErrorProps) {
  if (!message) {
    return null;
  }

  return (
    <section role="alert" className="form-alert form-alert--error">
      {message}
    </section>
  );
}
