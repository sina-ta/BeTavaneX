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
    <section
      role="alert"
      className="
        rounded-xl
        border
        border-red-500/30
        bg-red-500/10
        px-4
        py-3
        text-sm
        text-red-300
      "
    >
      {message}
    </section>
  );
}
