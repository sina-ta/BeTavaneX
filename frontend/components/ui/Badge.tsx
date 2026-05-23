type BadgeProps = {

  status: string;

};

export default function Badge({
  status,
}: BadgeProps) {

  const getStatusClass = () => {

    switch (
      status.toLowerCase()
    ) {

      case "good":

        return "badge-good";

      case "approved":

        return "badge-good";

      case "warning":

        return "badge-warning";

      case "pending":

        return "badge-warning";

      case "critical":

        return "badge-critical";

      case "delayed":

        return "badge-critical";

      default:

        return "badge-default";
    }

  };

  return (

    <span
      className={`badge-base ${getStatusClass()}`}
    >

      {status}

    </span>
  );
}