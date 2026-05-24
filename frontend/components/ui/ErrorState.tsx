type ErrorStateProps = {
  title?: string;
  message: string;
  onRetry?: () => void;
};

export default function ErrorState({
  title = "Something went wrong",
  message,
  onRetry,
}: ErrorStateProps) {
  return (
    <div className="empty-state">
      <div className="empty-icon">!</div>

      <p className="font-semibold">{title}</p>

      <p className="text-sm opacity-70">{message}</p>

      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="
            mt-4
            rounded
            bg-black
            px-4
            py-2
            text-sm
            text-white
          "
        >
          Try again
        </button>
      )}
    </div>
  );
}
