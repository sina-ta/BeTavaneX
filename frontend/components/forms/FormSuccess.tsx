type FormSuccessProps = {
  message?: string | null;
};

export default function FormSuccess({
  message,
}: FormSuccessProps) {
  if (!message) {
    return null;
  }

  return (
    <section role="status" className="form-alert form-alert--success">
      {message}
    </section>
  );
}
