type ProgressBarProps = {
  value: number;
};

export default function ProgressBar({
  value,
}: ProgressBarProps) {

  const color =
    value >= 80
      ? "bg-green-500"
      : value >= 50
      ? "bg-yellow-500"
      : "bg-red-500";

  return (

    <div className="flex items-center gap-3">

      <div className="w-full bg-gray-200 rounded-full h-3">

        <div
          className={`${color} h-3 rounded-full`}
          style={{
            width: `${value}%`,
          }}
        />

      </div>

      <span className="text-sm font-semibold text-gray-700 min-w-[45px]">
        {value}%
      </span>

    </div>

  );
}