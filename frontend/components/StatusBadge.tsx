export default function StatusBadge({
  status,
}: any) {

  let color = "";

  if (status === "Good") {

    color =
      "bg-green-500/20 text-green-400";

  }

  else if (status === "Warning") {

    color =
      "bg-yellow-500/20 text-yellow-400";

  }

  else {

    color =
      "bg-red-500/20 text-red-400";
  }

  return (

    <div
      className={`
        inline-flex
        px-4
        py-2
        rounded-full
        font-semibold
        ${color}
      `}
    >

      {status}

    </div>
  );
}