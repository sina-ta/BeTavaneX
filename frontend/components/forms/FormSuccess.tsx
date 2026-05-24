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
    <section
      role="status"
      className="
        rounded-xl
        border
        border-green-500/30
        bg-green-500/10
        px-4
        py-3
        text-sm
        text-green-300
      "
    >
      {message}
    </section>
  );
}
