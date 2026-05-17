type StatusBadgeProps = {

  status: string;
};

export default function StatusBadge({

  status,

}: StatusBadgeProps) {

  let styles = "";

  if (status.includes("Critical")) {

    styles = `
      bg-red-100
      text-red-700
    `;

  } else if (status.includes("Warning")) {

    styles = `
      bg-yellow-100
      text-yellow-700
    `;

  } else {

    styles = `
      bg-green-100
      text-green-700
    `;
  }

  return (

    <span
      className={`
        px-3
        py-1
        rounded-full
        text-sm
        font-semibold
        ${styles}
      `}
    >
      {status}
    </span>
  );
}