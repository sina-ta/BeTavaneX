type Props = {
  title: string;
  value: string | number;
  footer?: string;
};

export default function KpiCard({
  title,
  value,
  footer,
}: Props) {

  return (

    <div className="kpi-card">

      <div className="kpi-title">
        {title}
      </div>

      <div className="kpi-value">
        {value}
      </div>

      {footer && (
        <div className="kpi-footer">
          {footer}
        </div>
      )}

    </div>
  );
}