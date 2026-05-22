export default function KpiCard({
  title,
  value,
}: any) {

  return (

    <div className="card-base">

      <div className="card-title">

        {title}

      </div>

      <div className="card-value">

        {value}

      </div>

    </div>
  );
}