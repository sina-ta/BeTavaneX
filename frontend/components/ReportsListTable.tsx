type Props = {
  reports: any[];
};

export default function ReportsListTable({
  reports,
}: Props) {

  return (

    <div className="table-container">

      <h2 className="table-title">
        Reports History
      </h2>

      <table className="table-base">

        <thead className="table-head">

          <tr>

            <th className="table-head-cell">
              WO ID
            </th>

            <th className="table-head-cell">
              Reporter
            </th>

            <th className="table-head-cell">
              Qty
            </th>

            <th className="table-head-cell">
              Manpower
            </th>

            <th className="table-head-cell">
              Delay
            </th>

            <th className="table-head-cell">
              Weather
            </th>

            <th className="table-head-cell">
              Status
            </th>

          </tr>

        </thead>

        <tbody>

          {reports.map((report) => (

            <tr
              key={report.id}
              className="table-row"
            >

              <td className="table-cell">
                {report.work_order_id}
              </td>

              <td className="table-cell">
                {report.reported_by}
              </td>

              <td className="table-cell">
                {report.actual_qty}
              </td>

              <td className="table-cell">
                {report.manpower_count}
              </td>

              <td className="table-cell">
                {report.delay_reason}
              </td>

              <td className="table-cell">
                {report.weather_status}
              </td>

              <td className="table-cell">
                {report.report_status}
              </td>

            </tr>

          ))}

        </tbody>

      </table>

    </div>
  );
}