type LoadingStateProps = {
  message?: string;
};

export default function LoadingState({
  message = "Loading data...",
}: LoadingStateProps) {
  return (
    <div className="loading-state">
      <div className="loading-spinner" />
      <p>{message}</p>
    </div>
  );
}
