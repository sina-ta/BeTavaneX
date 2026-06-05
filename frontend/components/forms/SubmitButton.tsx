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
      className="button-submit"
    >
      {loading ? "…" : title}
    </button>
  );
}
