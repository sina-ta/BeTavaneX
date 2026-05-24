type Props = {
  title: string;
  loading?: boolean;
  disabled?: boolean;
};

export default function SubmitButton({
  title,
  loading = false,
  disabled = false,
}: Props) {
  return (
    <button
      type="submit"
      disabled={disabled || loading}
      className="
        rounded-2xl
        bg-blue-600
        px-6
        py-4
        font-semibold
        text-white
        transition
        hover:bg-blue-700
        disabled:cursor-not-allowed
        disabled:opacity-60
      "
    >
      {loading ? "Submitting..." : title}
    </button>
  );
}
