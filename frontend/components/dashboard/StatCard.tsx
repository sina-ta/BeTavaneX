type StatCardProps = {

  title: string;

  value: string | number;

  trend?: string;

};

export default function StatCard({
  title,
  value,
  trend,
}: StatCardProps) {

  return (

    <div className="stat-card">

      <div className="stat-card-title">

        {title}

      </div>

      <div className="stat-card-value">

        {value}

      </div>

      {trend && (

        <div className="stat-card-trend">

          {trend}

        </div>

      )}

    </div>
  );
}