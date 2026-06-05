type ValidationMessageProps = {
  message?: string;
};

export default function ValidationMessage({
  message,
}: ValidationMessageProps) {
  if (!message) {
    return null;
  }

  return <p className="form-validation-message">{message}</p>;
}
