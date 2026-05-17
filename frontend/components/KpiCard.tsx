type KpiCardProps = {
  title: string;
  value: string | number;
};

export default function KpiCard({
  title,
  value,
}: KpiCardProps) {

  return (

    <div className="bg-white p-6 rounded-2xl shadow">

      <p className="text-gray-500 text-sm font-medium">
        {title}
      </p>

      <h2 className="text-3xl font-bold mt-2 text-gray-800">
        {value}
      </h2>

    </div>

  );
}